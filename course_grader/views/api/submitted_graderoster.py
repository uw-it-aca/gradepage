from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from uw_saml.decorators import group_required
from course_grader.views.rest_dispatch import RESTDispatch
from course_grader.models import (
    SubmittedGradeRoster as SubmittedGradeRosterModel)
from course_grader.dao.person import person_from_regid, person_display_name
from course_grader.dao.section import section_from_label
from course_grader.dao.term import term_from_param
from uw_sws_graderoster import graderoster_from_xhtml
import logging
import csv


logger = logging.getLogger(__name__)


@method_decorator(group_required(settings.GRADEPAGE_ADMIN_GROUP),
                  name='dispatch')
@method_decorator(never_cache, name='dispatch')
class SubmissionsByTerm(RESTDispatch):
    def get(self, request, *args, **kwargs):
        term_id = kwargs.get("term_id")

        try:
            selected_term = term_from_param(term_id)
        except Exception as ex:
            return self.error_response(400, "Invalid Term ID")

        graderosters = SubmittedGradeRosterModel.objects.get_status_by_term(
            selected_term)

        response = self.csv_response(filename=term_id)

        csv.register_dialect("unix_newline", lineterminator="\n")
        writer = csv.writer(response, dialect="unix_newline")
        writer.writerow([
            "Section",
            "Secondary section",
            "Submitter",
            "Submission datetime"
        ])

        for graderoster in graderosters:
            writer.writerow([
                graderoster["section_id"],
                graderoster["secondary_section_id"],
                graderoster["submitted_by"],
                graderoster["submitted_date"],
            ])

        return response


@method_decorator(group_required(settings.GRADEPAGE_ADMIN_GROUP),
                  name='dispatch')
@method_decorator(never_cache, name='dispatch')
class SubmittedGradeRoster(RESTDispatch):
    def get(self, request, *args, **kwargs):
        graderoster_id = kwargs.get("graderoster_id")

        try:
            model = SubmittedGradeRosterModel.objects.get(pk=graderoster_id)
            section = section_from_label(model.section_id)
            instructor = person_from_regid(model.instructor_id)
            submitter = person_from_regid(model.submitted_by)
            graderoster = graderoster_from_xhtml(model.document, section,
                                                 instructor)

        except SubmittedGradeRosterModel.DoesNotExist:
            return self.error_response(404, "Not Found")

        except Exception as ex:
            logger.error("Download failed for graderoster model %s: %s" % (
                graderoster_id, ex))
            return self.error_response(500, "%s" % ex)

        if model.secondary_section_id is not None:
            filename = model.secondary_section_id
        else:
            filename = model.section_id

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
                "%s %s" % (item.student_first_name, item.student_surname),
                "%s %s" % (section.curriculum_abbr, section.course_number),
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

        logger.info("Graderoster downloaded: %s-%s" % (model.section_id,
                                                       model.instructor_id))

        return response
