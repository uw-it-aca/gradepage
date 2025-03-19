# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.test import TestCase
from uw_sws_graderoster.models import GradeRosterItem
from course_grader.dao.gradesubmission import *


class GradeSubmissionDAOFunctionsTest(TestCase):
    def test_format_logged_grade(self):
        self.assertEqual(
            format_logged_grade(GradeRosterItem()), 'None')
        self.assertEqual(
            format_logged_grade(GradeRosterItem(is_auditor=True)), None)
        self.assertEqual(
            format_logged_grade(GradeRosterItem(
                date_withdrawn='2013-05-31')), None)
        self.assertEqual(
            format_logged_grade(GradeRosterItem(no_grade_now=True)), 'X')
        self.assertEqual(
            format_logged_grade(GradeRosterItem(
                no_grade_now=True, has_incomplete=True)), 'I,X')
        self.assertEqual(
            format_logged_grade(GradeRosterItem(grade=3.9)), '3.9')
        self.assertEqual(
            format_logged_grade(GradeRosterItem(
                grade=3.9, has_incomplete=True)), 'I,3.9')
        self.assertEqual(
            format_logged_grade(GradeRosterItem(
                grade=3.9, has_writing_credit=True)), '3.9,W')
        self.assertEqual(
            format_logged_grade(GradeRosterItem(
                grade=3.9, has_incomplete=True, has_writing_credit=True)),
            'I,3.9,W')
