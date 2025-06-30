# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.conf import settings
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from course_grader.models import SubmittedGradeRoster, Grade, GradeImport
from course_grader.dao.graderoster import graderoster_for_section
from course_grader.dao.section import (
    section_from_param, is_grader_for_section, section_display_name)
from course_grader.dao.person import (
    person_from_user, person_from_request, person_display_name)
from course_grader.dao.term import (
    all_viewable_terms, is_grading_period_open, is_grading_period_past,
    current_term)
from course_grader.views import (
    section_status_params, clean_section_id, url_for_section,
    url_for_grading_status, url_for_graderoster)
from course_grader.views.api import (
    GradeFormHandler, graderoster_status_params, item_is_submitted,
    sorted_students, sorted_grades)
from course_grader.views.decorators import xhr_login_required
from course_grader.exceptions import *
from userservice.user import UserService
from restclients_core.exceptions import DataFailureException
from datetime import datetime
from logging import getLogger
import time
import json
import csv
import re

logger = getLogger(__name__)


@method_decorator(xhr_login_required, name='dispatch')
class GradeRoster(GradeFormHandler):
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

            if (re.match(r"(PATCH|PUT|POST|DELETE)", request.method)):
                self.valid_user_override()

            if (re.match(r"(GET|PUT|POST|DELETE)", request.method)):
                submitted_graderosters_only = kwargs.get(
                    "submitted_graderosters_only", False)
                self.graderoster = graderoster_for_section(
                    self.section, self.instructor, self.user,
                    submitted_graderosters_only=submitted_graderosters_only)

        except (InvalidUser, GradingNotPermitted, OverrideNotPermitted) as ex:
            user = UserService().get_original_user()
            logger.info(f"Grading for {section_id} not permitted for {user}")
            return self.error_response(401, f"{ex}")
        except (SecondaryGradingEnabled, GradingPeriodNotOpen,
                InvalidTerm, InvalidSection, MissingInstructorParam) as ex:
            return self.error_response(400, f"{ex}")
        except ReceiptNotFound as ex:
            return self.error_response(404, f"{ex}")
        except DataFailureException as ex:
            logger.info(f"GET graderoster error: {ex}")
            (status, msg) = self.data_failure_error(ex)
            return self.error_response(status, msg)
        except Exception as ex:
            logger.info(f"GET graderoster error: {ex}")
            return self.error_response(500, f"{ex.__class__.__name__}: {ex}")

    def get(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        section_id = kwargs.get("section_id")

        if is_grading_period_open(self.section):
            kwargs["saved_grades"] = self.saved_grades(section_id)

        content = self.response_content(**kwargs)
        return self.json_response(content)

    def patch(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        section_id = kwargs.get("section_id")

        try:
            grade_data = json.loads(request.body)
            grade = self.save_grade(section_id, grade_data)
        except Exception as ex:
            logger.error(f"PATCH grade failed for {section_id}: {ex}")
            return self.error_response(500)

        # PATCH does not return a full graderoster resource
        return self.json_response(grade.json_data())

    def put(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        section_id = kwargs.get("section_id")
        saved_grades = {}
        try:
            grade_data = json.loads(request.body)
            for data in grade_data.get("grades"):
                grade = self.save_grade(section_id, data)
                saved_grades[data["student_id"]] = grade

        except Exception as ex:
            logger.error(f"PUT grade failed for {section_id}: {ex}")
            return self.error_response(500)

        secondary_section = getattr(self.graderoster, "secondary_section",
                                    None)

        status = 200
        for item in self.graderoster.items:
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                continue

            if (item.is_auditor or item.date_withdrawn is not None):
                continue

            student_id = item.student_label(separator="-")
            if not self.validate_grade(item, saved_grades.get(student_id)):
                status = 409

        kwargs["saved_grades"] = saved_grades
        content = self.response_content(**kwargs)
        return self.json_response(content, status=status)

    def post(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        section_id = kwargs.get("section_id")
        saved_grades = self.saved_grades(section_id)
        secondary_section = getattr(self.graderoster, "secondary_section",
                                    None)

        status = 200
        gradable_count = 0
        for item in self.graderoster.items:
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                continue

            if (item.is_auditor or item.date_withdrawn is not None):
                continue

            gradable_count += 1
            student_id = item.student_label(separator="-")
            saved_grade = saved_grades.get(student_id)
            if self.validate_grade(item, saved_grade):
                item.no_grade_now = saved_grade.no_grade_now
                item.grade = "" if (
                    item.no_grade_now is True) else saved_grade.grade
                item.has_incomplete = saved_grade.is_incomplete
                item.has_writing_credit = saved_grade.is_writing
                item.grade_submitter_person = self.user
            else:
                status = 409

        if status == 200 and gradable_count:
            section = self.graderoster.section
            model = SubmittedGradeRoster(
                section_id=section.section_label(),
                instructor_id=self.graderoster.instructor.uwregid,
                term_id=section.term.term_label(),
                submitted_by=self.user.uwregid,
                document=self.graderoster.xhtml())

            if secondary_section is not None:
                model.secondary_section_id = secondary_section.section_label()

            model.save()
            model.submit(section_id)

            self.graderoster = graderoster_for_section(
                self.section, self.instructor, self.user)

        kwargs["saved_grades"] = self.saved_grades(section_id)

        content = self.response_content(**kwargs)
        content["graderoster"]["is_submission_confirmation"] = True
        return self.json_response(content, status=status)

    def delete(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        section_id = kwargs.get("section_id")

        try:
            Grade.objects.get_by_section_id_and_person(
                section_id, self.user.uwregid).delete()
            logger.info(f"Grades cleared for {section_id}")
        except Exception as ex:
            logger.error(f"DELETE grades failed for {section_id}: {ex}")
            return self.error_response(500)

        kwargs["saved_grades"] = {}
        content = self.response_content(**kwargs)
        return self.json_response(content)

    def validate_grade(self, graderoster_item, saved_grade):
        if saved_grade is None:
            return False

        if (saved_grade.is_incomplete and
                (saved_grade.no_grade_now or saved_grade.grade == "N" or
                    saved_grade.grade == "CR")):
            return False

        if saved_grade.no_grade_now:
            return True

        for choice in graderoster_item.grade_choices:
            if (choice is not None and choice != "" and
                    choice == saved_grade.grade):
                return True

        return False

    def saved_grades(self, section_id):
        grade_lookup = {}
        for grade in Grade.objects.get_by_section_id_and_person(
                section_id, self.user.uwregid):
            grade_lookup[grade.student_label] = grade
        return grade_lookup

    def response_content(self, **kwargs):
        section_id = kwargs.get("section_id")
        saved_grades = kwargs.get("saved_grades", {})
        grading_period_open = is_grading_period_open(self.section)
        allows_writing_credit = self.graderoster.allows_writing_credit
        sources = dict(GradeImport.SOURCE_CHOICES)

        data = {"section_id": section_id,
                "section_name": section_display_name(self.section),
                "is_primary_section": self.section.is_primary_section,
                "linked_section_count": len(self.section.linked_section_urls),
                "students": [],
                "import_choices": [],
                "grade_choices": [],
                "submissions": [],
                "is_writing_section": not allows_writing_credit,
                "has_duplicate_codes": False,
                "has_successful_submissions": False,
                "has_failed_submissions": False,
                "failed_submission_count": 0,
                "has_inprogress_submissions": False,
                "has_saved_grades": False,
                "gradable_student_count": 0,
                "ungraded_count": 0,
                "has_grade_imports": False,
                "grade_import_count": 0}

        secondary_section = getattr(self.graderoster, "secondary_section",
                                    None)

        submissions = getattr(self.graderoster, "submissions", {})
        for key in sorted(submissions.keys()):
            sid = key if key != self.graderoster.section.section_id else None
            submission_status = graderoster_status_params(
                self.graderoster, secondary_section_id=sid,
                include_grade_imports=True)
            submission_status["section_id"] = sid
            if (submission_status["accepted_date"] is None and
                    submission_status["status_code"] == "200"):
                data["has_inprogress_submissions"] = True
            if submission_status["grade_import"] is not None:
                data["has_grade_imports"] = True
                data["grade_import_count"] += 1
            data["submissions"].append(submission_status)

        if grading_period_open:
            for choice in GradeImport.SOURCE_CHOICES:
                if choice[0] != GradeImport.CATALYST_SOURCE:
                    data["import_choices"].append({"value": choice[0],
                                                   "label": choice[1]})

        grade_lookup = {}
        for item in sorted_students(self.graderoster.items):
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                # Filtering by secondary section
                continue

            student_id = item.student_label(separator="-")
            item_id = "-".join([section_id, student_id])
            is_submitted = item_is_submitted(item)
            grade_choices_index = None
            grade_url = None
            grade = "" if item.no_grade_now is True else item.grade
            no_grade_now = item.no_grade_now
            has_incomplete = item.has_incomplete
            has_writing_credit = item.has_writing_credit
            date_graded = None
            saved_grade_data = {}

            if item.duplicate_code is not None:
                data["has_duplicate_codes"] = True

            if is_submitted:
                if has_incomplete and grade.lower() == "i":
                    grade = ""

                if item.date_graded is not None:
                    data["has_successful_submissions"] = True
                    date = datetime.strptime(item.date_graded, "%Y-%m-%d")
                    date_graded = date.strftime("%m/%d/%Y")

                if item.status_code is not None:
                    if item.status_code.startswith("2"): # 2xx status
                        data["has_successful_submissions"] = True
                    else:
                        data["has_failed_submissions"] = True
                        data["failed_submission_count"] += 1

            elif item.date_withdrawn is None and not item.is_auditor:
                data["ungraded_count"] += 1

            if (grading_period_open and not item.is_auditor and
                    item.date_withdrawn is None):
                grade_url = url_for_graderoster(section_id)
                if grade_url:
                    data["gradable_student_count"] += 1

                # Use an existing grade_choices list, or add this one
                grade_choices_csv = ",".join(item.grade_choices)
                try:
                    grade_choices_index = grade_lookup[grade_choices_csv]
                except KeyError:
                    data["grade_choices"].append(
                        sorted_grades(item.grade_choices))
                    grade_choices_index = len(data["grade_choices"]) - 1
                    grade_lookup[grade_choices_csv] = grade_choices_index

                # Add saved grade data if it exists
                try:
                    saved_grade = saved_grades[student_id]
                    saved_grade_data = saved_grade.json_data()
                    if saved_grade.no_grade_now is True:
                        saved_grade_data["grade"] = ""
                    if saved_grade.import_source is not None:
                        saved_grade_data["import_source"] = (
                            sources[saved_grade.import_source])
                    data["has_saved_grades"] = True
                except KeyError:
                    pass

            student_data = {
                "item_id": clean_section_id(item_id),
                "student_id": student_id,
                "student_firstname": item.student_first_name,
                "student_lastname": item.student_surname,
                "student_number": item.student_number,
                "student_credits": item.student_credits,
                "section_id": item.section_id,
                "is_auditor": item.is_auditor,
                "date_withdrawn": item.date_withdrawn,
                "is_submitted": is_submitted,
                "date_graded": date_graded,
                "allows_incomplete": True,
                "has_incomplete": has_incomplete,
                "is_writing_section": not allows_writing_credit,
                "allows_writing_credit": allows_writing_credit,
                "has_writing_credit": has_writing_credit,
                "no_grade_now": no_grade_now,
                "duplicate_code": item.duplicate_code,
                "grade": grade,
                "grade_choices_index": grade_choices_index,
                "grade_url": grade_url,
                "grade_status_code": item.status_code,
                "grade_status": item.status_message,
                "saved_grade": saved_grade_data,
            }
            data["students"].append(student_data)

        return {"graderoster": data}


class GradeRosterExport(GradeRoster):
    def get(self, request, *args, **kwargs):
        start_time = time.time()
        section_id = kwargs.get("section_id")

        err_response = self._authorize(request, *args, **kwargs)
        if err_response is None:
            content = self.response_content(**kwargs)
            saved_grades = self.saved_grades(section_id)
        else:
            return err_response

        response = self.create_response(content, saved_grades)

        logger.info((
            "Graderoster exported for section: {section_id}, "
            "grading_open: {grading_open}, submitted: {submitted}, "
            "current_term: {current_term}, time_taken: {time_taken}").format(
                section_id=section_id,
                grading_open=is_grading_period_open(self.section),
                submitted=content.get("graderoster").get(
                    "has_successful_submissions"),
                current_term=current_term().canvas_sis_id(),
                time_taken=time.time() - start_time))

        return response

    def create_response(self, content, saved_grades={}):
        csv_header = render_to_string("export.txt", {
            "user_name": person_display_name(self.user),
            "user_email": "{}@uw.edu".format(self.user.uwnetid),
            "quarter": self.section.term.quarter.title(),
            "year": self.section.term.year,
            "curriculum_abbr": self.section.curriculum_abbr,
            "course_number": self.section.course_number,
            "section_id": self.section.section_id,
            "cog_form_url": getattr(settings, "COG_FORM_URL", ""),
        })
        response = self.csv_response(
            content=csv_header, filename=self.section.section_label())
        csv.register_dialect("unix_newline", lineterminator="\n")
        writer = csv.writer(response, dialect="unix_newline")

        for student in content.get("graderoster").get("students", []):
            saved_grade = ""
            if student.get("is_auditor"):
                grade = "Auditor"
            elif student.get("date_withdrawn"):
                grade = "Withdrawn ({})".format(student.get("grade", ""))
            else:
                grade = student.get("grade", "")
                if student.get("no_grade_now"):
                    grade = "X"
                elif student.get("has_incomplete"):
                    grade = "Incomplete; {}".format(grade)
                if student.get("has_writing_credit"):
                    grade = "{}; Writing Credit".format(grade)

                if not student.get("date_graded"):
                    try:
                        saved = saved_grades[student.get("student_id")]
                        saved_grade = saved.grade
                        if saved.no_grade_now is True:
                            saved_grade = "X"
                        elif saved.is_incomplete:
                            saved_grade = "Incomplete; {}".format(saved_grade)
                        elif saved.is_writing:
                            saved_grade = "{}; Writing Credit".format(
                                saved_grade)
                    except KeyError:
                        pass

            writer.writerow([
                student.get("student_number"),
                "{last}, {first}".format(
                    first=student.get("student_firstname", "").strip().upper(),
                    last=student.get("student_lastname", "").strip().upper()),
                grade,
                saved_grade,
            ])

        return response


class GradeRosterStatus(GradeFormHandler):
    def get(self, request, *args, **kwargs):
        try:
            self.user = person_from_user()
            self.submitted_graderosters_only = False
        except InvalidUser as ex:
            try:
                self.user = person_from_request(request)
                self.submitted_graderosters_only = True
            except InvalidUser as ex:
                return self.error_response(401, "Invalid user: {}".format(ex))
            except DataFailureException as ex:
                logger.info("GET person error: {}".format(ex))
                (status, msg) = self.data_failure_error(ex)
                return self.error_response(status, msg)

        try:
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

            self.graderoster = graderoster_for_section(
                self.section, self.instructor, self.user,
                submitted_graderosters_only=self.submitted_graderosters_only)

        except GradingNotPermitted as ex:
            logger.info("Grading status for {} not permitted for {}".format(
                ex.section, ex.person))
            return self.error_response(401, "{}".format(ex))
        except (InvalidSection, InvalidUser, MissingInstructorParam) as ex:
            return self.error_response(400, "{}".format(ex))
        except (GradingPeriodNotOpen, SecondaryGradingEnabled,
                ReceiptNotFound, InvalidTerm) as ex:
            data = section_status_params(self.section, self.instructor)
            if data["grading_status"] is None:
                data["grading_status"] = "{}".format(ex)
            return self.json_response({"grading_status": data})
        except DataFailureException as ex:
            logger.info("GET graderoster error: {}".format(ex))
            (status, msg) = self.data_failure_error(ex)
            return self.error_response(status, msg)
        except Exception as ex:
            logger.info("GET graderoster error: {}".format(ex))
            return self.error_response(500, f'{ex.__class__.__name__}: {ex}')

        data = section_status_params(self.section, self.instructor)

        section = self.section
        if section.is_primary_section and not section.allows_secondary_grading:
            # Handle secondary sections in this request if appropriate
            data.update(graderoster_status_params(self.graderoster))
            data["secondary_sections"] = []
            for linked_url in section.linked_section_urls:
                secondary_data = self.secondary_section_status(linked_url)
                data["secondary_sections"].append(secondary_data)
        elif (not section.is_primary_section and
                not section.allows_secondary_grading):
            data.update(graderoster_status_params(
                self.graderoster, secondary_section_id=section.section_id))
        else:
            data.update(graderoster_status_params(self.graderoster))

        if not self.submitted_graderosters_only:
            data["saved_count"] = Grade.objects.get_by_section_id_and_person(
                section_id, self.user.uwregid).count()

        return self.json_response({"grading_status": data})

    def secondary_section_status(self, section_url):
        section = self.section
        # Avoiding an SWS request for this section
        secondary_section_id = section_url.split("/")[-1].split(".")[0]
        section_id = "-".join([str(section.term.year), section.term.quarter,
                              section.curriculum_abbr, section.course_number,
                              secondary_section_id, self.instructor.uwregid])

        data = section_status_params(section, self.instructor)
        data.update(graderoster_status_params(
            self.graderoster, secondary_section_id=secondary_section_id))

        data["section_id"] = clean_section_id(section_id)
        data["section_url"] = url_for_section(section_id)
        data["display_name"] = " ".join([section.curriculum_abbr,
                                        section.course_number,
                                        secondary_section_id])

        if self.submitted_graderosters_only:
            data["status_url"] = url_for_grading_status(section_id)
        else:
            data["status_url"] = None
            data["saved_count"] = Grade.objects.get_by_section_id_and_person(
                section_id, self.user.uwregid).count()

        return data
