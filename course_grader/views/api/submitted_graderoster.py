# Copyright 2026 UWIT, University of Washington
# SPDX-License-Identifier: Apache-2.0


import csv
import re
from logging import getLogger

from django.conf import settings
from django.utils.decorators import method_decorator
from lxml import etree
from uw_saml.decorators import group_required
from uw_sws_graderoster.models import GradeRoster

from course_grader.dao.person import person_display_name, person_from_regid
from course_grader.dao.section import section_from_label
from course_grader.dao.term import term_from_param
from course_grader.models import GradeImport
from course_grader.models import SubmittedGradeRoster as SubmittedGradeRosterModel
from course_grader.views.rest_dispatch import RESTDispatch

logger = getLogger(__name__)


@method_decorator(group_required(settings.GRADEPAGE_SUPPORT_GROUP),
                  name='dispatch')
class SubmissionsByTerm(RESTDispatch):
    def get(self, request, *args, **kwargs):
        term_id = kwargs.get("term_id")

        try:
            selected_term = term_from_param(term_id)
        except Exception:
            return self.error_response(400, "Invalid Term ID")

        graderosters = SubmittedGradeRosterModel.objects.get_status_by_term(
            selected_term)
        grade_imports = GradeImport.objects.get_import_sources_by_term(
            selected_term)

        import_sources = {}
        import_counts = {}
        for grade_import in grade_imports:
            count = import_counts.get(grade_import["section_id"], 0)
            import_counts[grade_import["section_id"]] = count + 1
            import_sources[grade_import["section_id"]] = grade_import["source"]

        response = self.csv_response(filename=term_id)

        csv.register_dialect("unix_newline", lineterminator="\n")
        writer = csv.writer(response, dialect="unix_newline")
        writer.writerow([
            "Section ID",
            "Secondary Section ID",
            "Instructor ID",
            "Submitted By",
            "Submitted Date",
            "Total Imports",
            "Import Source",
        ])

        for graderoster in graderosters:
            import_section_id = "-".join([
                re.sub(r"[,/]", "-", graderoster["section_id"]),
                graderoster["submitted_by"]])

            writer.writerow([
                graderoster["section_id"],
                graderoster["secondary_section_id"],
                graderoster["instructor_id"],
                graderoster["submitted_by"],
                graderoster["submitted_date"],
                import_counts.get(import_section_id, 0),
                import_sources.get(import_section_id),
            ])

        return response


@method_decorator(group_required(settings.GRADEPAGE_SUPPORT_GROUP),
                  name='dispatch')
class SubmittedGradeRoster(RESTDispatch):
    def get(self, request, *args, **kwargs):
        graderoster_id = kwargs.get("graderoster_id")
        file_type = request.GET.get("type", "csv").strip().lower()

        try:
            model = SubmittedGradeRosterModel.objects.get(pk=graderoster_id)
            section = section_from_label(model.section_id)
            instructor = person_from_regid(model.instructor_id)
            submitter = person_from_regid(model.submitted_by)
            document = model.document.strip()

        except SubmittedGradeRosterModel.DoesNotExist:
            return self.error_response(404, "Not Found")

        except Exception as ex:
            logger.error(
                f"Download failed for graderoster model {graderoster_id}: {ex}")
            return self.error_response(500, f"{ex}")

        if model.secondary_section_id is not None:
            filename = f"{model.secondary_section_id}-{model.instructor_id}"
        else:
            filename = f"{model.section_id}-{model.instructor_id}"

        if file_type == "xml":
            return self.xml_response(content=document, filename=filename)

        graderoster = GradeRoster.from_xhtml(
            etree.fromstring(document), section=section, instructor=instructor)

        response = self.csv_response(filename=filename)

        csv.register_dialect("unix_newline", lineterminator="\n")
        writer = csv.writer(response, dialect="unix_newline")
        writer.writerow([
            "Student Number",
            "Student Name",
            "Course",
            "Section",
            "Credits",
            "Incomplete",
            "Grade",
            "Writing Credit",
            "Instructor Name",
            "Instructor UWNetid",
            "Submitter Name",
            "Submitter UWNetid"
        ])

        secondary_section = getattr(graderoster, "secondary_section", None)
        for item in graderoster.items:
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                continue

            writer.writerow([
                item.student_number,
                f"{item.student_first_name} {item.student_surname}",
                f"{section.curriculum_abbr} {section.course_number}",
                item.section_id,
                item.student_credits,
                "I" if item.has_incomplete else "",
                "X" if item.no_grade_now else str(item.grade),
                "W" if item.has_writing_credit else "",
                person_display_name(instructor),
                instructor.uwnetid,
                person_display_name(submitter),
                submitter.uwnetid
            ])

        logger.info(
            f"Graderoster downloaded: {model.section_id}-{model.instructor_id}")

        return response
