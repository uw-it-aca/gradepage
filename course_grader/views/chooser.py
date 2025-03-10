# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from course_grader.dao.term import term_from_param, all_viewable_terms
from course_grader.dao.message import get_messages_for_term
from course_grader.exceptions import InvalidTerm
from course_grader.views import url_for_term
from restclients_core.exceptions import DataFailureException
from logging import getLogger

logger = getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class HomeView(TemplateView):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        kwargs["term_id"] = request.GET.get("term", "").strip()
        try:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)
        except InvalidTerm:
            return HttpResponseRedirect("/")
        except DataFailureException as ex:
            if ex.status == 404:
                response = render(request, "404.html", {})
                response.status_code = ex.status
            else:
                logger.error("GET term failed: {}, Param: {}".format(
                    ex, kwargs["term_id"]))
                response = render(request, "503.html", {})
            return response

    def get_context_data(self, **kwargs):
        term_id = kwargs.get("term_id")
        all_terms = all_viewable_terms()
        now_term = all_terms[0]

        if len(term_id):
            selected_term = term_from_param(term_id)
            if selected_term not in all_terms:
                raise InvalidTerm()
        else:
            selected_term = all_terms[0]

        opt_terms = []
        for opt_term in all_terms:
            opt_terms.append({
                "quarter": opt_term.get_quarter_display(),
                "year": opt_term.year,
                "url": url_for_term(opt_term),
                "is_selected": opt_term == selected_term,
            })

        context = get_messages_for_term(now_term)
        context["now_quarter"] = now_term.get_quarter_display()
        context["now_year"] = now_term.year
        context["selected_quarter"] = selected_term.get_quarter_display()
        context["selected_year"] = selected_term.year
        context["terms"] = opt_terms
        context["sections_url"] = reverse(
            "section-list", kwargs={"term_id": "{year}-{qtr}".format(
                year=selected_term.year, qtr=selected_term.quarter)})
        context["page_title"] = "{qtr} {year}".format(
            qtr=selected_term.get_quarter_display(), year=selected_term.year)

        return context
