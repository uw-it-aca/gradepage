from django.test import TestCase
from course_grader.models import ImportConversion
from course_grader.dao.canvas import grading_standard_for_course
from course_grader.exceptions import InvalidGradingScale
from uw_canvas.courses import Courses
from uw_canvas.models import CanvasCourse
from uw_canvas.utilities import fdao_canvas_override
import mock


@fdao_canvas_override
class ImportConversionTest(TestCase):
    def test_valid_scale(self):
        ic = ImportConversion()
        self.assertEqual(ic.valid_scale('ug'), 'ug')
        self.assertEqual(ic.valid_scale('UG'), 'ug')
        self.assertRaises(InvalidGradingScale, ic.valid_scale, '')
        self.assertRaises(InvalidGradingScale, ic.valid_scale, 'abc')

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

        # CR/NC scheme
        gs_data['grading_scheme'] = [
            {"name": "CR", "value": 0.90}, {"name": "NC", "value": 0.50}]

        ic = ImportConversion.from_grading_standard(gs_data).json_data()
        self.assertEqual(ic['scale'], 'cnc')
        self.assertEqual(len(ic['grade_scale']), 2)
        self.assertEqual(ic['calculator_values'], [
            {'grade': 'CR', 'is_first': True, 'percentage': 90.0},
            {'grade': 'NC', 'is_last': True, 'percentage': 50.0}])
        self.assertEqual(ic['lowest_valid_grade'], 0.0)

    @mock.patch.object(Courses, 'get_course')
    def test_from_grading_standard_errors(self, mock_get_course):
        mock_get_course.return_value = CanvasCourse(course_id=1234567,
                                                    grading_standard_id=54321,
                                                    name='Train 101 A')
        gs_data = grading_standard_for_course(1234567)

        # Letter grade scale is not a valid scale for grade submission
        gs_data['grading_scheme'] = [
            {"name": "A", "value": 0.90}, {"name": "B", "value": 0.80},
            {"name": "C", "value": 0.70}, {"name": "D", "value": 0.60},
            {"name": "F", "value": 0.50}]

        self.assertRaises(InvalidGradingScale,
                          ImportConversion.from_grading_standard, gs_data)
