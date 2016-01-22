from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.decorators.cache import never_cache
from course_grader.models import GradeImport
from course_grader.dao.section import section_from_param
from course_grader.dao.person import person_from_user
from course_grader.dao.term import current_term
from course_grader.views import grade_submission_deadline_params,\
    section_url_token, display_section_name, display_person_name, url_for_term
from course_grader.exceptions import MissingInstructorParam
from restclients.catalyst.gradebook import valid_gradebook_id
import logging
import re


logger = logging.getLogger(__name__)


@login_required
@never_cache
def section(request, url_token):
    try:
        user = person_from_user()
        (section, instructor) = section_from_param(url_token)
        now_term = current_term()

    except MissingInstructorParam as ex:
        # MyUW doesn't supply an instructor regid, add the user
        section_url = "/section/%s-%s" % (url_token, user.uwregid)
        return HttpResponseRedirect(section_url)

    except Exception as ex:
        if hasattr(ex, "status"):
            if ex.status == 404:
                return error_response(request, status=404)
            elif ex.status == 503:
                return render_to_response("503.html", {},
                                          RequestContext(request))
            else:
                logger.error("Section view error: %s, Param: %s" % (ex,
                                                                    url_token))
                raise
        else:
            logger.error("Section view error: %s, Param: %s" % (ex, url_token))
            return error_response(request, status=404)

    if (not section.is_grading_period_open() and
            not section.term.is_grading_period_past()):
        # future grading period
        return HttpResponseRedirect("/")

    section_name = display_section_name(section)

    params = {
        "page_title": section_name,
        "section_quarter": section.term.get_quarter_display(),
        "section_year": section.term.year,
        "term_url": url_for_term(section.term),
        "course_title": section.course_title_long,
        "section_sln": section.sln,
        "section_name": section_name,
        "is_independent_study": section.is_independent_study,
        "graderoster_url": "/api/v1/graderoster/%s" % section_url_token(
            section, instructor),
        "import_url": "/api/v1/import/%s" % section_url_token(
            section, instructor),
    }

    if section.is_independent_study:
        params["section_name"] += " (%s)" % display_person_name(instructor)

    if now_term.is_grading_period_open():
        params.update(grade_submission_deadline_params(now_term))

        import_id = request.GET.get("cgb_source_id", None)
        if valid_gradebook_id(import_id):
            params["auto_import_id"] = import_id
            params["auto_import_src"] = GradeImport.CATALYST_SOURCE

    return render_to_response("section.html", params, RequestContext(request))


def error_response(request, status=500):
    template = "%s.html" % status
    response = render_to_response(template, {}, RequestContext(request))
    response.status_code = status
    return response
