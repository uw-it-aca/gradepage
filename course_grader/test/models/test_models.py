from django.test import TestCase
from course_grader.models import ImportConversion
from course_grader.dao.canvas import grading_standard_for_course
from uw_canvas.courses import Courses
from uw_canvas.models import CanvasCourse
from uw_canvas.utilities import fdao_canvas_override
import mock


@fdao_canvas_override
class ImportConversionTest(TestCase):
    @mock.patch.object(Courses, 'get_course')
    def test_from_grading_standard(self, mock_get_course):
        mock_get_course.return_value = CanvasCourse(course_id=1234567,
                                                    grading_standard_id=54321,
                                                    name='Train 101 A')
        gs_data = grading_standard_for_course(1234567)

        ic = ImportConversion.from_grading_standard(gs_data).json_data()
        self.assertEqual(ic['scale'], 'ug')
        self.assertEqual(len(ic['grade_scale']), 34)
        self.assertEqual(ic['calculator_values'], [
            {'grade': '4.0', 'is_first': True, 'percentage': 95.0},
            {'grade': '0.7', 'is_last': True, 'percentage': 20.0}])
        self.assertEqual(ic['lowest_valid_grade'], 0.0)
        self.assertEqual(ic['grading_standard_id'], 54321)
        self.assertEqual(ic['grading_standard_name'], 'Scale1')
        self.assertEqual(ic['course_id'], 1234567)
        self.assertEqual(ic['course_name'], 'Train 101 A')
