# Copyright 2026 UWIT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from logging import getLogger

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from userservice.user import UserService

from course_grader.dao.person import person_display_name, person_from_user
from course_grader.dao.term import all_viewable_terms, term_from_param
from course_grader.exceptions import DataFailureException, InvalidTerm
from course_grader.views import url_for_term
from course_grader.views.support import can_override_user

logger = getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class HomeView(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        kwargs["term_id"] = request.GET.get("term", "").strip()
        try:
            context = self.get_context_data(**kwargs)
            return self.render_to_response({"context_data": context})
        except InvalidTerm:
            return HttpResponseRedirect("/")
        except DataFailureException as ex:
            if ex.status == 404:
                response = render(request, "404.html", {})
                response.status_code = ex.status
            else:
                logger.error(f"{ex}")
                response = render(request, "503.html", {})
            return response

    def get_context_data(self, **kwargs):
        context = {}
        person = person_from_user()
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
            opt_term_id = f"{opt_term.year}-{opt_term.quarter}"
            opt_terms.append({
                "id": opt_term_id,
                "quarter": opt_term.get_quarter_display(),
                "year": opt_term.year,
                "url": url_for_term(opt_term),
                "sections_url": reverse("section-list", kwargs={
                    "term_id": opt_term_id}),
                "is_selected": opt_term == selected_term,
            })

        # Term context
        context["now_quarter"] = now_term.get_quarter_display()
        context["now_year"] = now_term.year
        context["selected_quarter"] = selected_term.get_quarter_display()
        context["selected_year"] = selected_term.year
        context["terms"] = opt_terms
        context["sections_url"] = reverse("section-list", kwargs={
            "term_id": f"{selected_term.year}-{selected_term.quarter}"
        })
        context["page_title"] = (
            f"{selected_term.get_quarter_display()} {selected_term.year}")

        # User context
        user_service = UserService()
        context["login_user"] = user_service.get_original_user()
        context["override_user"] = user_service.get_override_user()
        context["user_fullname"] = person_display_name(person)
        context["signout_url"] = reverse("saml_logout")
        context["debug_mode"] = settings.DEBUG

        if can_override_user(self.request):
            context["clear_override_url"] = reverse("userservice_override")
            context["support_url"] = reverse("gradepage-status")

        return context
