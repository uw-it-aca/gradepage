from django.conf import settings
from django.utils.translation import ugettext as _
from course_grader.dao.person import person_from_user
from course_grader.dao.term import term_from_param, all_viewable_terms
from course_grader.dao.section import all_gradable_sections
from course_grader.views import section_status_params
from course_grader.views.rest_dispatch import RESTDispatch
from course_grader.exceptions import InvalidUser, InvalidTerm
import logging
import re


logger = logging.getLogger(__name__)


class Sections(RESTDispatch):
    def GET(self, request, **kwargs):
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
            return self.error_response(404, "%s" % ex)
        except Exception as ex:
            logger.error("GET selected term failed: %s" % ex)
            return self.error_response(500, _("sws_not_available"))

        try:
            sections = all_gradable_sections(self.user, self.term)
        except Exception as ex:
            if (hasattr(ex, "status") and
                    (ex.status == 401 or ex.status == 404)):
                sections = []
            else:
                logger.error("GET gradable sections failed: %s" % ex)
                return self.error_response(500, _("sws_not_available"))

        content = self.response_content(sections, **kwargs)
        return self.json_response(content)

    def response_content(self, sections, **kwargs):
        sections.sort(key=lambda section: (section.section_label(),
                                           section.grader.surname,
                                           section.grader.first_name))

        primary_sections = {}
        for section in sections:
            if section.is_primary_section and not section.is_independent_study:
                primary_sections[section.section_label()] = []

        section_data = []
        for section in sections:
            data = section_status_params(section)

            if (not section.is_primary_section and
                    section.primary_section_label() in primary_sections):
                # Nested secondary
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
