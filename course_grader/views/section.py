# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from course_grader.models import GradeImport
from course_grader.dao.section import (
    section_from_param, section_display_name, section_url_token)
from course_grader.dao.person import person_from_user
from course_grader.dao.term import (
    current_term, is_grading_period_open, is_grading_period_past)
from course_grader.dao.message import get_messages_for_term
from course_grader.views import (
    url_for_term, url_for_graderoster, url_for_import, url_for_export,
    url_for_upload)
from course_grader.exceptions import InvalidSection, MissingInstructorParam
from restclients_core.exceptions import DataFailureException
from uw_catalyst.gradebook import valid_gradebook_id
from logging import getLogger

logger = getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class SectionView(TemplateView):
    template_name = "section.html"

    def get(self, request, *args, **kwargs):
        url_token = kwargs.get("url_token")
        try:
            user = person_from_user()
            (section, instructor) = section_from_param(url_token)

            if (not is_grading_period_open(section) and
                    not is_grading_period_past(section.term)):
                # future grading period
                return HttpResponseRedirect("/")

            kwargs["section"] = section
            kwargs["instructor"] = instructor

            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)
        except InvalidSection as ex:
            response = render(request, "404.html", {})
            response.status_code = 404
            return response
        except MissingInstructorParam as ex:
            # MyUW doesn't supply an instructor regid, add the user
            section_url = "/section/{}-{}".format(url_token, user.uwregid)
            return HttpResponseRedirect(section_url)
        except DataFailureException as ex:
            if ex.status == 404:
                response = render(request, "404.html", {})
                response.status_code = ex.status
            else:
                logger.error(
                    "GET section failed: {}, Param: {}".format(ex, url_token))
                response = render(request, "503.html", {})
            return response

    def get_context_data(self, **kwargs):
        if section.is_independent_study:
            section_name = section_display_name(section, instructor)
        else:
            section_name = section_display_name(section)

        url_token = section_url_token(section, instructor)

        context = get_messages_for_term(current_term())
        context["page_title"] = section_name
        context["section_quarter"] = section.term.get_quarter_display()
        context["section_year"] = section.term.year
        context["term_url"] = url_for_term(section.term)
        context["course_title"] = section.course_title_long
        context["section_sln"] = section.sln
        context["section_name"] = section_name
        context["is_independent_study"] = section.is_independent_study
        context["graderoster_url"] = url_for_graderoster(url_token)
        context["import_url"] = url_for_import(url_token)
        context["export_url"] = url_for_export(url_token)
        context["upload_url"] = url_for_upload(url_token)

        if is_grading_period_open(section):
            import_id = self.request.GET.get("cgb_source_id")
            if valid_gradebook_id(import_id):
                context["auto_import_id"] = import_id
                context["auto_import_src"] = GradeImport.CATALYST_SOURCE

        return context
