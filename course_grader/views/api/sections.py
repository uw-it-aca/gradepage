# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from course_grader.dao.person import person_from_user
from course_grader.dao.term import term_from_param, all_viewable_terms
from course_grader.dao.section import (
    all_gradable_sections, section_display_name, section_url_token)
from course_grader.views import (
    section_status_params, url_for_term, url_for_graderoster, url_for_import,
    url_for_export, url_for_upload)
from course_grader.views.rest_dispatch import RESTDispatch
from course_grader.exceptions import InvalidUser, InvalidTerm
from restclients_core.exceptions import DataFailureException
from logging import getLogger
import re

logger = getLogger(__name__)


@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class Sections(RESTDispatch):
    def get(self, request, *args, **kwargs):
        try:
            term = term_from_param(kwargs.get("term_id"))
            if term is None or term not in all_viewable_terms():
                raise InvalidTerm()
            self.term = term
            self.user = person_from_user()
        except InvalidUser:
            content = self.response_content(sections=[], **kwargs)
            return self.json_response(content)
        except InvalidTerm as ex:
            return self.error_response(404, "{}".format(ex))
        except DataFailureException as ex:
            logger.error("GET selected term failed: {}".format(ex))
            (status, msg) = self.data_failure_error(ex)
            return self.error_response(status, msg)

        try:
            sections = all_gradable_sections(self.user, self.term)
        except DataFailureException as ex:
            if (ex.status == 401 or ex.status == 404):
                sections = []
            else:
                logger.error("GET gradable sections failed: {}".format(ex))
                (status, msg) = self.data_failure_error(ex)
                return self.error_response(status, msg)

        content = self.response_content(sections, **kwargs)
        return self.json_response(content)

    def response_content(self, sections, **kwargs):
        sections = sorted(sections, key=lambda section: (
            section.section_label(), section.grading_instructor.surname,
            section.grading_instructor.first_name))

        primary_sections = {}
        for section in sections:
            if section.is_primary_section and not section.is_independent_study:
                primary_sections[section.section_label()] = []

        section_data = []
        for section in sections:
            data = section_status_params(section, section.grading_instructor)

            if (not section.is_primary_section and
                    section.primary_section_label() in primary_sections):
                # Nested secondary

                if not section.allows_secondary_grading:
                    # Suppress status request from client
                    data["status_url"] = None

                primary_sections[section.primary_section_label()].append(data)
            elif (section.is_primary_section and
                    not section.is_independent_study):
                # Primary "parent" section
                data["secondary_sections"] = primary_sections.get(
                    section.section_label())
                section_data.append(data)
            else:
                # Independent study and un-nested secondary sections
                section_data.append(data)

        return {"sections": section_data,
                "year": self.term.year,
                "quarter": self.term.get_quarter_display()}


@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class Section(RESTDispatch):
    def get(self, request, *args, **kwargs):
        url_token = kwargs.get("section_id")
        try:
            user = person_from_user()
            (section, instructor) = section_from_param(url_token)
        except InvalidSection as ex:
            return self.error_response(404, "Section not found")
        except MissingInstructorParam as ex:
            # MyUW doesn't supply an instructor regid, add the user
            instructor = user
        except DataFailureException as ex:
            if ex.status == 404:
                return self.error_response(404, "Not found")
            else:
                logger.error(
                    "GET section failed: {}, Param: {}".format(ex, url_token))
                return self.error_response(503)

        if (not is_grading_period_open(section) and
                not is_grading_period_past(section.term)):
            # future grading period
            return self.error_response(400, "Future term")

        return self.json_response(self.response_content(section, instructor))

    def response_content(self, section, instructor):
        if section.is_independent_study:
            section_name = section_display_name(section, instructor)
        else:
            section_name = section_display_name(section)

        url_token = section_url_token(section, instructor)

        content = {}
        content["page_title"] = section_name
        content["section_quarter"] = section.term.get_quarter_display()
        content["section_year"] = section.term.year
        content["term_url"] = url_for_term(section.term)
        content["course_title"] = section.course_title_long
        content["section_sln"] = section.sln
        content["section_name"] = section_name
        content["is_independent_study"] = section.is_independent_study
        content["graderoster_url"] = url_for_graderoster(url_token)
        content["import_url"] = url_for_import(url_token)
        content["export_url"] = url_for_export(url_token)
        content["upload_url"] = url_for_upload(url_token)
        return content
