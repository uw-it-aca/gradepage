from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from course_grader.dao.term import term_from_param, all_viewable_terms
from course_grader.dao.message import get_messages_for_term
from course_grader.exceptions import InvalidTerm
from course_grader.views import url_for_term
from restclients_core.exceptions import DataFailureException
from logging import getLogger

logger = getLogger(__name__)


@login_required
@never_cache
def home(request):
    params = {}
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

        params.update(get_messages_for_term(now_term))

    except InvalidTerm:
        return HttpResponseRedirect("/")

    except DataFailureException as ex:
        logger.error("GET selected term failed: {}".format(ex))
        return render(request, "503.html", {})

    opt_terms = []
    for opt_term in all_terms:
        opt_terms.append({
            "quarter": opt_term.get_quarter_display(),
            "year": opt_term.year,
            "url": url_for_term(opt_term),
            "is_selected": opt_term == selected_term,
        })

    params.update({
        "now_quarter": now_term.get_quarter_display(),
        "now_year": now_term.year,
        "selected_quarter": selected_term.get_quarter_display(),
        "selected_year": selected_term.year,
        "terms": opt_terms,
        "sections_url": "/api/v1/sections/{year}-{quarter}".format(
            year=selected_term.year, quarter=selected_term.quarter),
        "page_title": "{quarter} {year}".format(
            quarter=selected_term.get_quarter_display(),
            year=selected_term.year),
    })

    return render(request, "home.html", params)
