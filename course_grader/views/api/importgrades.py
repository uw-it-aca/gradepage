# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from course_grader.models import GradeImport, ImportConversion
from course_grader.dao.person import person_from_user
from course_grader.dao.term import all_viewable_terms
from course_grader.dao.section import (
    section_from_param, is_grader_for_section, section_display_name,
    section_url_token)
from course_grader.dao.graderoster import graderoster_for_section
from course_grader.views.api import GradeFormHandler, sorted_students
from course_grader.views import clean_section_id
from course_grader.exceptions import *
from restclients_core.exceptions import DataFailureException
from userservice.user import UserService
from uw_saml.decorators import group_required
from logging import getLogger
import json
import csv
import re

logger = getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class ImportGrades(GradeFormHandler):
    def _authorize(self, request, *args, **kwargs):
        try:
            self.user = person_from_user()

            section_id = kwargs.get("section_id")
            (section, instructor) = section_from_param(section_id)
            self.section = section
            self.instructor = instructor

            if section.term not in all_viewable_terms():
                raise InvalidTerm()

            if not is_grader_for_section(section, instructor):
                raise GradingNotPermitted(section.section_label(),
                                          instructor.uwnetid)

            if (self.user != instructor and
                    not is_grader_for_section(section, self.user)):
                raise GradingNotPermitted(section.section_label(),
                                          self.user.uwnetid)

            if section.is_primary_section and section.allows_secondary_grading:
                raise SecondaryGradingEnabled()

            if "PUT" == request.method:
                self.valid_user_override()

            self.graderoster = graderoster_for_section(
                self.section, self.instructor, self.user)

        except (InvalidUser, GradingNotPermitted, OverrideNotPermitted) as ex:
            logger.info("Grading for {} not permitted for {}".format(
                section_id, UserService().get_original_user()))
            return self.error_response(403, "{}".format(ex))
        except (SecondaryGradingEnabled, GradingPeriodNotOpen,
                InvalidTerm) as ex:
            return self.error_response(400, "{}".format(ex))
        except InvalidSection as ex:
            return self.error_response(404, "{}".format(ex))
        except DataFailureException as ex:
            logger.info("GET graderoster error: {}".format(ex))
            (status, msg) = self.data_failure_error(ex)
            return self.error_response(status, msg)

    def get(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        section_id = kwargs.get("section_id")
        import_id = kwargs.get("import_id")

        try:
            grade_import = GradeImport.objects.get(pk=import_id)
        except GradeImport.DoesNotExist:
            return self.error_response(400, "Invalid import")

        return self.response_content(grade_import)

    def put(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        section_id = kwargs.get("section_id")
        import_id = kwargs.get("import_id")

        try:
            grade_import = GradeImport.objects.get(pk=import_id)
            put_data = json.loads(request.body)

        except GradeImport.DoesNotExist:
            return self.error_response(404, "Import not found")
        except Exception as ex:
            return self.error_response(400, "Invalid import")

        conversion_data = put_data.get("conversion_scale", None)
        try:
            grade_import.save_conversion_data(conversion_data)
        except Exception as ex:
            logger.error("PUT import error for {}: {}".format(
                section_id, ex))

        import_data = grade_import.json_data()
        converted_grades = put_data.get("converted_grades", {})
        secondary_section = getattr(self.graderoster, "secondary_section",
                                    None)
        for item in self.graderoster.items:
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                continue

            if (item.date_graded is not None or item.is_auditor or
                    item.date_withdrawn is not None):
                continue

            # Find the grade data for each graderoster item
            grade = next((g for g in import_data.get("imported_grades") if (
                g["student_reg_id"] == item.student_uwregid or
                g["student_number"] == item.student_number)), None)

            if grade is not None:
                grade_data = {
                    "student_id": item.student_label(separator="-"),
                    "import_source": grade_import.source,
                    "import_grade": grade["imported_grade"],
                    "is_override_grade": grade["is_override_grade"],
                    "comment": grade["comment"],
                    "grade": converted_grades.get(item.student_uwregid,
                                                  grade["imported_grade"]),
                    "is_writing": grade["is_writing"],
                    "is_incomplete": grade["is_incomplete"],
                    "no_grade_now": False,
                }
                self.save_grade(section_id, grade_data)

        return self.response_content(grade_import)

    def post(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        try:
            data = json.loads(request.body)
            source = data.get("source", None)
            source_id = data.get("source_id", None)
        except Exception as ex:
            logger.error("POST import failed for {}: {}".format(
                self.section.section_label(), ex))
            return self.error_response(400, "Invalid import")

        grade_import = GradeImport(
            section_id=section_url_token(self.section, self.instructor),
            term_id=self.section.term.term_label(),
            imported_by=self.user.uwregid,
            source=source,
            source_id=source_id)

        try:
            grade_import.grades_for_section(self.section, self.instructor)
        except Exception as ex:
            logger.error("POST import failed for {}: {}".format(
                self.section.section_label(), ex))
            return self.error_response(500, "{}".format(ex))

        return self.response_content(grade_import)

    def response_content(self, grade_import):
        return_data = grade_import.json_data()
        return_data["section_name"] = section_display_name(self.section)

        # Create a new list of imported grades, including only students who are
        # actually on the graderoster
        imported_grades = return_data.pop("imported_grades", [])
        return_data["students"] = []

        secondary_section = getattr(self.graderoster, "secondary_section",
                                    None)
        for item in sorted_students(self.graderoster.items):
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                # Filtering by secondary section
                continue

            # Find the grade data for each graderoster item
            grade = next((g for g in imported_grades if (
                g["student_reg_id"] == item.student_uwregid or
                g["student_number"] == item.student_number)), None)

            if grade is not None:
                item_id = "-".join([grade_import.section_id,
                                    item.student_label(separator="-")])
                grade["item_id"] = clean_section_id(item_id)
                grade["section_id"] = self.section.section_id
                grade["student_firstname"] = item.student_first_name
                grade["student_lastname"] = item.student_surname
                grade["student_reg_id"] = item.student_uwregid
                grade["student_number"] = item.student_number
                grade["is_auditor"] = item.is_auditor
                grade["is_withdrawn"] = item.date_withdrawn is not None
                return_data["students"].append(grade)

        return self.json_response({"grade_import": return_data})


class UploadGrades(ImportGrades):
    def post(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        uploaded_file = request.FILES.get("file")

        if uploaded_file is None:
            return self.error_response(status=400, message="Missing file")

        grade_import = GradeImport(
            section_id=section_url_token(self.section, self.instructor),
            term_id=self.section.term.term_label(),
            imported_by=self.user.uwregid,
            source=GradeImport.CSV_SOURCE,
            file_name=uploaded_file.name)

        try:
            grade_import.grades_for_section(
                self.section, self.instructor, fileobj=uploaded_file)
        except Exception as ex:
            logger.error("POST upload {} failed for {}: {}".format(
                uploaded_file.name, self.section.section_label(), ex))
            return self.error_response(400, "{}".format(ex))

        return self.response_content(grade_import)

    @method_decorator(group_required(settings.GRADEPAGE_SUPPORT_GROUP),
                      name="dispatch")
    def get(self, request, *args, **kwargs):
        section_id = kwargs.get("section_id")
        import_id = kwargs.get("import_id")

        try:
            grade_import = GradeImport.objects.get(
                section_id=section_id, pk=import_id)
        except GradeImport.DoesNotExist:
            return self.error_response(404, "Not found")

        if not grade_import.file_path:
            return self.error_response(400, "No data")

        response = self.csv_response(filename=grade_import.file_name)

        with default_storage.open(grade_import.file_path, mode="r") as f:
            response.content = f.read()

        return response
