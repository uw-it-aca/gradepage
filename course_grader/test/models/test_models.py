# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.test import TestCase
from course_grader.models import Grade, GradeImport, ImportConversion
from course_grader.dao.canvas import grading_scheme_for_course
from course_grader.dao.section import get_section_by_label
from course_grader.dao.person import PWS
from course_grader.exceptions import InvalidGradingScale
from uw_canvas.courses import Courses
from uw_canvas.models import CanvasCourse
from uw_canvas.utilities import fdao_canvas_override
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
from datetime import datetime
import mock


class GradeTest(TestCase):
    def test_student_label(self):
        uwregid = 'FBB38FE46A7C11D5A4AE0004AC494FFE'

        grade = Grade()
        with self.assertRaises(AttributeError):  # Missing student_reg_id
            x = grade.student_label

        grade = Grade(student_reg_id=uwregid)
        self.assertEqual(
            grade.student_label, 'FBB38FE46A7C11D5A4AE0004AC494FFE')

        grade = Grade(student_reg_id=uwregid, duplicate_code='A')
        self.assertEqual(
            grade.student_label, 'FBB38FE46A7C11D5A4AE0004AC494FFE-A')

    def test_json_data(self):
        grade = Grade(student_reg_id='B2B2B2B2B2B2B2B2B2B2B2B2B2B2B2B2',
                      duplicate_code='A',
                      grade='3.9',
                      import_source='csv',
                      import_grade='99',
                      section_id='2013-spring-A B&C-101-A',
                      modified_by='A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1')

        d = grade.json_data()
        self.assertEqual(d['section_id'], '2013-spring-A B&C-101-A')
        self.assertEqual(d['student_reg_id'],
                         'B2B2B2B2B2B2B2B2B2B2B2B2B2B2B2B2')
        self.assertEqual(d['duplicate_code'], 'A')
        self.assertEqual(d['grade'], '3.9')
        self.assertEqual(d['is_writing'], False)
        self.assertEqual(d['is_incomplete'], False)
        self.assertEqual(d['no_grade_now'], False)
        self.assertEqual(d['import_grade'], '99')
        self.assertEqual(d['import_source'], 'csv')
        self.assertEqual(d['modified_by'], 'A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1')


@fdao_sws_override
@fdao_pws_override
@fdao_canvas_override
class GradeImportTest(TestCase):
    @mock.patch('course_grader.dao.canvas.grading_scheme_for_course')
    def test_grades_for_section(self, mock_grading_scheme):
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

    def test_save_conversion_data(self):
        gi = GradeImport(source=GradeImport.CANVAS_SOURCE)
        self.assertEqual(gi.import_conversion, None)
        self.assertEqual(gi.accepted_date, None)

        gi.save_conversion_data(data=None)

        self.assertEqual(gi.import_conversion, None)
        self.assertIsInstance(gi.accepted_date, datetime)


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
