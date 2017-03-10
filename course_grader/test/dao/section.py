from django.test import TestCase
from restclients.pws import PWS
from restclients.test import fdao_sws_override, fdao_pws_override
from course_grader.dao.section import *


@fdao_sws_override
@fdao_pws_override
class SectionDAOFunctionsTest(TestCase):
    def test_section_from_param(self):
        pass

    def test_all_gradable_sections(self):
        pass

    def test_is_grader_for_section(self):
        pass

    def test_section_url_token(self):
        section = get_section_by_label('2013,spring,TRAIN,101/A')
        user = PWS().get_person_by_netid('javerage')

        self.assertEquals(section_url_token(section, user),
                          '2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

    def test_section_display_name(self):
        section = get_section_by_label('2013,spring,TRAIN,101/A')
        self.assertEquals(section_display_name(section), 'TRAIN 101 A')

        section = get_section_by_label('2013,spring,TRAIN,101/A')
        section.is_independent_study = True
        self.assertEquals(section_display_name(section), 'TRAIN 101 A')

        user = PWS().get_person_by_netid('javerage')
        self.assertEquals(section_display_name(section, user),
                          'TRAIN 101 A (James Student)')
