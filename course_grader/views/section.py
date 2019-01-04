from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from course_grader.models import GradeImport
from course_grader.dao.section import (
    section_from_param, section_display_name, section_url_token)
from course_grader.dao.person import person_from_user
from course_grader.dao.term import current_term
from course_grader.dao.message import get_messages_for_term
from course_grader.views import url_for_term
from course_grader.exceptions import MissingInstructorParam
from uw_catalyst.gradebook import valid_gradebook_id
import logging
import re

logger = logging.getLogger(__name__)


@login_required
@never_cache
def section(request, url_token):
    params = {}
    try:
        user = person_from_user()
        (section, instructor) = section_from_param(url_token)
        now_term = current_term()

        params.update(get_messages_for_term(now_term))

    except MissingInstructorParam as ex:
        # MyUW doesn't supply an instructor regid, add the user
        section_url = "/section/{}-{}".format(url_token, user.uwregid)
        return HttpResponseRedirect(section_url)

    except Exception as ex:
        if hasattr(ex, "status"):
            if ex.status == 404:
                return error_response(request, status=404)
            elif ex.status == 503:
                return render(request, "503.html", {})
            else:
                logger.error(
                    "Section view error: {}, Param: {}".format(ex, url_token))
                raise
        else:
            logger.error(
                "Section view error: {}, Param: {}".format(ex, url_token))
            return error_response(request, status=404)

    if (not section.is_grading_period_open() and
            not section.term.is_grading_period_past()):
        # future grading period
        return HttpResponseRedirect("/")

    if section.is_independent_study:
        section_name = section_display_name(section, instructor)
    else:
        section_name = section_display_name(section)

    params.update({
        "page_title": section_name,
        "section_quarter": section.term.get_quarter_display(),
        "section_year": section.term.year,
        "term_url": url_for_term(section.term),
        "course_title": section.course_title_long,
        "section_sln": section.sln,
        "section_name": section_name,
        "is_independent_study": section.is_independent_study,
        "graderoster_url": "/api/v1/graderoster/{}".format(
            section_url_token(section, instructor)),
        "import_url": "/api/v1/import/{}".format(
            section_url_token(section, instructor)),
    })

    if now_term.is_grading_period_open():
        import_id = request.GET.get("cgb_source_id", None)
        if valid_gradebook_id(import_id):
            params["auto_import_id"] = import_id
            params["auto_import_src"] = GradeImport.CATALYST_SOURCE

    return render(request, "section.html", params)


def error_response(request, status=500):
    template = "{}.html".format(status)
    response = render(request, template, {})
    response.status_code = status
    return response
