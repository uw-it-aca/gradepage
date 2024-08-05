# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.test import TestCase
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
from course_grader.dao.person import PWS
from course_grader.dao.section import get_section_by_label
from course_grader.views.api.sections import Section


@fdao_sws_override
@fdao_pws_override
class SectionViewTest(TestCase):
    def test_response_content(self):
        section = get_section_by_label('2013,spring,TRAIN,101/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')

        kwargs = {"section": section, "instructor": user}
        context = Section().response_content(section, user).get("section");
        self.assertEqual(context["page_title"], "TRAIN 101 A")
        self.assertEqual(context["section_quarter"], "Spring")
        self.assertEqual(context["section_year"], 2013)
        self.assertEqual(context["term_url"], "/term/2013-spring")
        self.assertEqual(context["is_independent_study"], False)
