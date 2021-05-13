# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase, override_settings
from course_grader.dao.canvas import (
    GradeImportCanvas, grading_scheme_for_course)
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
    @mock.patch.object(Courses, 'get_course')
    def test_grading_scheme_for_course(self, mock_get_course):
        mock_get_course.return_value = CanvasCourse(course_id=1234567,
                                                    grading_standard_id=54321,
                                                    name='Train 101 A')

        gs_data = grading_scheme_for_course(1234567)
        self.assertEqual(gs_data['context_id'], 1234567)
        self.assertEqual(len(gs_data['grading_scheme']), 35)
        self.assertEqual(gs_data['course_id'], 1234567)
        self.assertEqual(gs_data['course_name'], 'Train 101 A')

    @mock.patch('course_grader.dao.canvas.grading_scheme_for_course')
    def test_grades_for_section(self, mock_grading_scheme):
        mock_grading_scheme.return_value = None

        section = get_section_by_label('2013,spring,A B&C,101/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')

        r = GradeImportCanvas().grades_for_section(section, user)
        self.assertEqual(len(r['grades']), 1)
        self.assertEqual(len(r['course_grading_schemes']), 0)
