from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.cache import never_cache
from userservice.user import UserService
from course_grader.dao.term import current_datetime, term_from_param,\
    all_viewable_terms, next_gradable_term, previous_gradable_term
from course_grader.exceptions import InvalidTerm
from course_grader.views import url_for_term, display_datetime,\
    grade_submission_deadline_params
import logging


logger = logging.getLogger(__name__)


@login_required
@never_cache
def home(request):
    term_id = request.GET.get("term", "").strip()
    try:
        all_terms = all_viewable_terms()
        now_term = all_terms[0]

        if len(term_id):
            selected_term = term_from_param(term_id)
            if selected_term not in all_terms:
                raise InvalidTerm()
        else:
            selected_term = all_terms[0]

    except InvalidTerm:
        return HttpResponseRedirect("/")

    except Exception as ex:
        if (hasattr(ex, "status") and ex.status == 503):
            return render_to_response("503.html", {}, RequestContext(request))
        else:
            logger.error("GET selected term failed: %s" % ex)
            raise

    opt_terms = []
    for opt_term in all_terms:
        opt_terms.append({
            "quarter": opt_term.get_quarter_display(),
            "year": opt_term.year,
            "url": url_for_term(opt_term),
            "is_selected": opt_term == selected_term,
        })

    params = {
        "now_quarter": now_term.get_quarter_display(),
        "now_year": now_term.year,
        "selected_quarter": selected_term.get_quarter_display(),
        "selected_year": selected_term.year,
        "terms": opt_terms,
        "sections_url": "/api/v1/sections/%s-%s" % (selected_term.year,
                                                    selected_term.quarter),
        "page_title": "%s %s" % (selected_term.get_quarter_display(),
                                 selected_term.year),
    }

    if now_term.is_grading_period_open():
        params["grading_window_open"] = True
        params.update(grade_submission_deadline_params(now_term))
    else:
        try:
            prev_term = previous_gradable_term()
            next_term = next_gradable_term()
        except Exception as ex:
            logger.error("GET previous/next term failed: %s" % ex)
            raise

        if next_term.quarter == next_term.SUMMER:
            next_open_date = next_term.aterm_grading_period_open
        else:
            next_open_date = next_term.grading_period_open

        params["grading_window_open"] = False
        params["prev_year"] = prev_term.year
        params["prev_quarter"] = prev_term.get_quarter_display()
        params["prev_window_close_date"] = display_datetime(
            prev_term.grade_submission_deadline)
        params["next_year"] = next_term.year
        params["next_quarter"] = next_term.get_quarter_display()
        params["next_window_open_date"] = display_datetime(next_open_date)
        params["in_current_quarter"] = True if (
            next_term.first_day_quarter < current_datetime().date()) else False

    return render_to_response("home.html", params, RequestContext(request))
