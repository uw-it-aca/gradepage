# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from course_grader.models import GradeImport, ImportConversion
from course_grader.dao.canvas import grading_scheme_for_course
from course_grader.dao.section import get_section_by_label
from course_grader.dao.person import PWS
from course_grader.exceptions import InvalidGradingScale
from uw_canvas.courses import Courses
from uw_canvas.models import CanvasCourse
from uw_canvas.utilities import fdao_canvas_override
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
import mock


@fdao_sws_override
@fdao_pws_override
@fdao_canvas_override
class GradeImportTest(TestCase):
    @mock.patch('course_grader.dao.canvas.grading_scheme_for_course')
    def test_grades_for_section(self, mock_grading_scheme):
        section = get_section_by_label('2013,summer,CSS,161/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')

        gi = GradeImport(source=GradeImport.CATALYST_SOURCE)
        gi.grades_for_section(section, user)
        data = gi.json_data()
        self.assertEqual(len(data['imported_grades']), 3)

        section = get_section_by_label('2013,spring,A B&C,101/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')

        mock_grading_scheme.return_value = None
        gi = GradeImport(source=GradeImport.CANVAS_SOURCE)
        gi.grades_for_section(section, user)
        data = gi.json_data()
        self.assertEqual(len(data['imported_grades']), 1)
        self.assertEqual(len(data['course_grading_schemes']), 0)

        gi = GradeImport(source='Bad')
        self.assertRaises(KeyError, gi.grades_for_section, section, user)


@fdao_canvas_override
class ImportConversionTest(TestCase):
    def test_valid_scale(self):
        ic = ImportConversion()
        self.assertEqual(ic.valid_scale('ug'), 'ug')
        self.assertEqual(ic.valid_scale('UG'), 'ug')
        self.assertRaises(InvalidGradingScale, ic.valid_scale, '')
        self.assertRaises(InvalidGradingScale, ic.valid_scale, 'abc')

    @mock.patch.object(Courses, 'get_course')
    def test_from_grading_scheme(self, mock_get_course):
        mock_get_course.return_value = CanvasCourse(course_id=1234567,
                                                    grading_standard_id=54321,
                                                    name='Train 101 A')
        gs_data = grading_scheme_for_course(1234567)

        ic = ImportConversion.from_grading_scheme(gs_data).json_data()
        self.assertEqual(ic['scale'], 'ug')
        self.assertEqual(len(ic['grade_scale']), 34)
        self.assertEqual(ic['calculator_values'], [])
        self.assertEqual(ic['lowest_valid_grade'], 0.0)
        self.assertEqual(ic['grading_scheme_id'], 54321)
        self.assertEqual(ic['grading_scheme_name'], 'Scale1')
        self.assertEqual(ic['course_id'], 1234567)
        self.assertEqual(ic['course_name'], 'Train 101 A')

        # CR/NC scheme
        gs_data['grading_scheme'] = [
            {"name": "CR", "value": 0.90}, {"name": "NC", "value": 0.50}]

        ic = ImportConversion.from_grading_scheme(gs_data).json_data()
        self.assertEqual(ic['scale'], 'cnc')
        self.assertEqual(len(ic['grade_scale']), 2)
        self.assertEqual(ic['calculator_values'], [])
        self.assertEqual(ic['lowest_valid_grade'], 0.0)

    @mock.patch.object(Courses, 'get_course')
    def test_from_grading_scheme_errors(self, mock_get_course):
        mock_get_course.return_value = CanvasCourse(course_id=1234567,
                                                    grading_standard_id=54321,
                                                    name='Train 101 A')
        gs_data = grading_scheme_for_course(1234567)

        # Letter grade scale is not a valid scale for grade submission
        gs_data['grading_scheme'] = [
            {"name": "A", "value": 0.90}, {"name": "B", "value": 0.80},
            {"name": "C", "value": 0.70}, {"name": "D", "value": 0.60},
            {"name": "F", "value": 0.50}]

        self.assertRaises(InvalidGradingScale,
                          ImportConversion.from_grading_scheme, gs_data)

    def test_decimal_to_percentage(self):
        ic = ImportConversion()
        self.assertEqual(ic.decimal_to_percentage(0.0), 0)
        self.assertEqual(ic.decimal_to_percentage(1), 100.0)
        self.assertEqual(ic.decimal_to_percentage(0.1), 10.0)
        self.assertEqual(ic.decimal_to_percentage(0.01), 1.0)
        self.assertEqual(ic.decimal_to_percentage(0.001), 0.1)
        self.assertEqual(ic.decimal_to_percentage(0.999), 99.9)
        self.assertEqual(ic.decimal_to_percentage(0.278), 27.8)
        self.assertEqual(ic.decimal_to_percentage(0.539), 53.9)

    def test_leading_zero(self):
        ic = ImportConversion()
        self.assertEqual(ic.leading_zero('0.1'), '0.1')
        self.assertEqual(ic.leading_zero('.1'), '0.1')
        self.assertEqual(ic.leading_zero('P'), 'P')
