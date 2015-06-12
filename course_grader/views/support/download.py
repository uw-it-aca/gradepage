from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from restclients.sws.graderoster import graderoster_from_xhtml
from course_grader.models import SubmittedGradeRoster
from course_grader.dao.person import person_from_regid
from course_grader.dao.section import section_from_label
from course_grader.views.support import is_admin_user
from course_grader.views import display_person_name
import logging
import json
import csv
import re


logger = logging.getLogger(__name__)


@login_required
def graderoster(request, *args, **kwargs):
    if not is_admin_user():
        return HttpResponseRedirect("/")

    graderoster_id = kwargs.get("graderoster_id")

    try:
        model = SubmittedGradeRoster.objects.get(pk=graderoster_id)
        section = section_from_label(model.section_id)
        instructor = person_from_regid(model.instructor_id)
        submitter = person_from_regid(model.submitted_by)
        graderoster = graderoster_from_xhtml(model.document, section,
                                             instructor)

    except SubmittedGradeRoster.DoesNotExist:
        response = render_to_response("404.html", {}, RequestContext(request))
        response.status_code = 404
        return response

    except Exception as ex:
        logger.exception(ex)
        raise

    if model.secondary_section_id is not None:
        filename = model.secondary_section_id
    else:
        filename = model.section_id

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="%s.csv"' % (
        re.sub(r"[,/]", "-", filename))

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
            display_person_name(instructor),
            instructor.uwnetid,
            display_person_name(submitter),
            submitter.uwnetid
        ])

    logger.info("Graderoster downloaded: %s-%s" % (model.section_id,
                                                   model.instructor_id))

    return response
