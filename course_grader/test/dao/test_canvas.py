from django.test import TestCase
from course_grader.dao.canvas import *
from course_grader.dao.person import PWS
from course_grader.dao.section import get_section_by_label
from uw_canvas.models import Assignment
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
import mock


@fdao_sws_override
@fdao_pws_override
class CanvasDAOFunctionsTest(TestCase):
    def test_muted_assignment(self):
        assignment = Assignment(
            muted=False, published=False, has_submissions=False)
        self.assertEquals(assignment_muted(assignment), False)

        assignment = Assignment(
            muted=True, published=False, has_submissions=False)
        self.assertEquals(assignment_muted(assignment), False)

        assignment = Assignment(
            muted=True, published=True, has_submissions=True)
        self.assertEquals(assignment_muted(assignment), True)

        assignment = Assignment(
            muted=True, published=True, has_submissions=False)
        self.assertEquals(assignment_muted(assignment), True)

        assignment = Assignment(
            muted=True, published=False, has_submissions=True)
        self.assertEquals(assignment_muted(assignment), True)

    @mock.patch.object(Assignments, 'get_assignments')
    def test_grades_for_section(self, mock_method):
        mock_method.return_value = []

        section = get_section_by_label('2013,spring,A B&C,101/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')

        r = grades_for_section(section, user)
        self.assertEquals(len(r['grades']), 1)
        self.assertEquals(len(r['warnings']), 0)
