# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
from uw_sws.models import Section
from course_grader.dao.person import PWS
from course_grader.dao.section import *
from course_grader.dao.term import term_from_param
from course_grader.exceptions import InvalidSection, MissingInstructorParam
import mock


@fdao_sws_override
@fdao_pws_override
class SectionDAOFunctionsTest(TestCase):
    def test_section_from_param(self):
        (section, user) = section_from_param(
            '2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')
        self.assertEquals(section.section_label(), '2013,spring,TRAIN,101/A')
        self.assertEquals(user.uwregid, '9136CCB8F66711D5BE060004AC494FFE')

        self.assertRaises(
            InvalidSection, section_from_param, '2013-spring-TRAIN-101')
        self.assertRaises(
            InvalidSection, section_from_param,
            '2013-spring-TRAIN-101--9136CCB8F66711D5BE060004AC494FFE')
        self.assertRaises(
            MissingInstructorParam, section_from_param,
            '2013-spring-TRAIN-101-A')

    @mock.patch('course_grader.dao.section.get_sections_by_delegate_and_term')
    @mock.patch(
        'course_grader.dao.section.get_sections_by_instructor_and_term')
    def test_all_gradable_sections_args(self, mock_ins_fn, mock_del_fn):
        person = PWS().get_person_by_netid('javerage')
        term = term_from_param('2013-autumn')

        ret = all_gradable_sections(person, term)
        mock_ins_fn.assert_called_with(
            person, term,
            delete_flag=[Section.DELETE_FLAG_ACTIVE,
                         Section.DELETE_FLAG_SUSPENDED],
            future_terms=0, include_secondaries=True,
            transcriptable_course='yes')

        mock_del_fn.assert_called_with(
            person, term,
            delete_flag=[Section.DELETE_FLAG_ACTIVE,
                         Section.DELETE_FLAG_SUSPENDED],
            future_terms=0, include_secondaries=True,
            transcriptable_course='yes')

    def test_is_grader_for_section(self):
        section = get_section_by_label('2013,spring,TRAIN,101/A')
        user = PWS().get_person_by_netid('javerage')
        self.assertEquals(is_grader_for_section(section, user), False)

        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')
        self.assertEquals(is_grader_for_section(section, user), True)

    def test_section_url_token(self):
        section = get_section_by_label('2013,spring,TRAIN,101/A')
        user = PWS().get_person_by_netid('javerage')

        self.assertEquals(
            section_url_token(section, user),
            '2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

    def test_section_display_name(self):
        section = get_section_by_label('2013,spring,TRAIN,101/A')
        self.assertEquals(section_display_name(section), 'TRAIN 101 A')

        section = get_section_by_label('2013,spring,TRAIN,101/A')
        section.is_independent_study = True
        self.assertEquals(section_display_name(section), 'TRAIN 101 A')

        user = PWS().get_person_by_netid('javerage')
        self.assertEquals(section_display_name(section, user),
                          'TRAIN 101 A (Jamesy McJamesy)')
