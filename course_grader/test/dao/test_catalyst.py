from django.test import TestCase
from course_grader.dao.catalyst import grades_for_section
from course_grader.dao.person import PWS
from course_grader.dao.section import get_section_by_label
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override


@fdao_sws_override
@fdao_pws_override
class CatalystDAOFunctionsTest(TestCase):
    def test_grades_for_section(self):
        section = get_section_by_label('2013,summer,CSS,161/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')

        r = grades_for_section(section, user)
        self.assertEquals(len(r['grades']), 3)

    def test_grades_for_book(self):
        section = get_section_by_label('2013,summer,CSS,161/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')

        r = grades_for_section(section, user, gradebook_id=12345)
        self.assertEquals(len(r['grades']), 3)
