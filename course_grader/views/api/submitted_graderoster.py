# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from uw_saml.decorators import group_required
from course_grader.views.rest_dispatch import RESTDispatch
from course_grader.models import (
    GradeImport, SubmittedGradeRoster as SubmittedGradeRosterModel)
from course_grader.dao.person import person_from_regid, person_display_name
from course_grader.dao.section import section_from_label
from course_grader.dao.term import term_from_param
from uw_sws_graderoster.models import GradeRoster
from lxml import etree
from logging import getLogger
import csv
import re

logger = getLogger(__name__)


@method_decorator(group_required(settings.GRADEPAGE_SUPPORT_GROUP),
                  name='dispatch')
class SubmissionsByTerm(RESTDispatch):
    def get(self, request, *args, **kwargs):
        term_id = kwargs.get("term_id")

        try:
            selected_term = term_from_param(term_id)
        except Exception as ex:
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
            "section_id",
            "secondary_section_id",
            "submitted_by",
            "submitted_date",
            "total_imports",
            "import_source",
        ])

        for graderoster in graderosters:
            import_section_id = "-".join([
                re.sub(r"[,/]", "-", graderoster["section_id"]),
                graderoster["submitted_by"]])

            writer.writerow([
                graderoster["section_id"],
                graderoster["secondary_section_id"],
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
                "Download failed for graderoster model {}: {}".format(
                    graderoster_id, ex))
            return self.error_response(500, "{}".format(ex))

        if model.secondary_section_id is not None:
            filename = model.secondary_section_id
        else:
            filename = model.section_id

        if file_type == "xml":
            return self.xml_response(content=document, filename=filename)

        graderoster = GradeRoster.from_xhtml(
            etree.fromstring(document), section=section, instructor=instructor)

        response = self.csv_response(filename=filename)

        csv.register_dialect("unix_newline", lineterminator="\n")
        writer = csv.writer(response, dialect="unix_newline")
        writer.writerow([
            "Student number",
            "Student name",
            "Course",
            "Section",
            "Credits",
            "Incomplete",
            "Grade",
            "Writing credit",
            "Instructor name",
            "Instructor netid",
            "Submitter name",
            "Submitter netid"
        ])

        secondary_section = getattr(graderoster, "secondary_section", None)
        for item in graderoster.items:
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                continue

            writer.writerow([
                item.student_number,
                "{first_name} {last_name}".format(
                    first_name=item.student_first_name,
                    last_name=item.student_surname),
                "{curr_abbr} {course_num}".format(
                    curr_abbr=section.curriculum_abbr,
                    course_num=section.course_number),
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

        logger.info("Graderoster downloaded: {}-{}".format(
            model.section_id, model.instructor_id))

        return response

    @staticmethod
    def xml_response(content="", status=200, filename="file"):
        response = HttpResponse(content=content,
                                status=status,
                                content_type="application/xhtml+xml")

        if not filename.lower().endswith(".xhtml"):
            filename += ".xhtml"

        response["Content-Disposition"] = (
            'attachment; filename="{}"').format(re.sub(r"[,/]", "-", filename))

        return response
