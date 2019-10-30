from django.test import TestCase, override_settings
from course_grader.dao.canvas import *
from course_grader.dao.person import PWS
from course_grader.dao.section import get_section_by_label
from uw_canvas.courses import Courses
from uw_canvas.models import CanvasCourse, Assignment
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
from uw_canvas.utilities import fdao_canvas_override
import mock


@fdao_sws_override
@fdao_pws_override
@fdao_canvas_override
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

    @mock.patch.object(Courses, 'get_course')
    def test_grading_standard_for_course(self, mock_get_course):
        mock_get_course.return_value = CanvasCourse(course_id=1234567,
                                                    grading_standard_id=54321,
                                                    name='Train 101 A')

        gs_data = grading_standard_for_course(1234567)
        self.assertEqual(gs_data['context_id'], 1234567)
        self.assertEqual(len(gs_data['grading_scheme']), 35)
        self.assertEqual(gs_data['course_id'], 1234567)
        self.assertEqual(gs_data['course_name'], 'Train 101 A')

    @override_settings(CANVAS_PER_PAGE=0)
    def test_hidden_grades_for_course(self):
        r = hidden_grades_for_course(862539)
        self.assertEqual(len(r), 0)

    @mock.patch('course_grader.dao.canvas.grading_standard_for_course')
    @mock.patch('course_grader.dao.canvas.hidden_grades_for_course')
    def test_grades_for_section(
            self, mock_hidden_grades, mock_grading_standard):
        mock_hidden_grades.return_value = []
        mock_grading_standard.return_value = None

        section = get_section_by_label('2013,spring,A B&C,101/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')

        r = grades_for_section(section, user)
        self.assertEqual(len(r['grades']), 1)
        self.assertEqual(len(r['warnings']), 0)
        self.assertEqual(len(r['grading_standards']), 0)
