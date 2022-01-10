# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from uw_sws.util import fdao_sws_override
from course_grader.dao.term import *
from course_grader.dao.section import get_section_by_label
from course_grader.exceptions import InvalidTerm


@fdao_sws_override
class TermDAOFunctionsTest(TestCase):
    def test_submission_deadline_warning(self):
        term = term_from_param('2013-autumn')
        with self.settings(SUBMISSION_DEADLINE_WARNING_HOURS=41,
                           CURRENT_DATETIME_OVERRIDE='2013-10-15 00:00:00'):
            self.assertEquals(submission_deadline_warning(term), False)

        with self.settings(SUBMISSION_DEADLINE_WARNING_HOURS=41,
                           CURRENT_DATETIME_OVERRIDE='2013-12-16 00:00:00'):
            self.assertEquals(submission_deadline_warning(term), True)

    def test_term_from_param(self):
        term = term_from_param('2013-autumn')
        self.assertEquals(term.year, 2013)
        self.assertEquals(term.quarter, 'autumn')

        term = term_from_param('2013-AUTUMN')
        self.assertEquals(term.year, 2013)
        self.assertEquals(term.quarter, 'autumn')

        self.assertRaises(InvalidTerm, term_from_param, '')
        self.assertRaises(InvalidTerm, term_from_param, '2013')
        self.assertRaises(InvalidTerm, term_from_param, 'autumn')
        self.assertRaises(InvalidTerm, term_from_param, '1999-autumn')
        self.assertRaises(InvalidTerm, term_from_param, '2013,autumn')

    def test_current_term(self):
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-10-15 00:00:00'):
            term = current_term()
            self.assertEquals(term.year, 2013)
            self.assertEquals(term.quarter, 'autumn')

    def test_next_gradable_term(self):
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-10-15 00:00:00'):
            term = next_gradable_term()
            self.assertEquals(term.year, 2013)
            self.assertEquals(term.quarter, 'autumn')

        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-12-20 00:00:00'):
            term = next_gradable_term()
            self.assertEquals(term.year, 2014)
            self.assertEquals(term.quarter, 'winter')

    def test_previous_gradable_term(self):
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-10-15 00:00:00'):
            term = previous_gradable_term()
            self.assertEquals(term.year, 2013)
            self.assertEquals(term.quarter, 'summer')

        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-12-20 00:00:00'):
            term = previous_gradable_term()
            self.assertEquals(term.year, 2013)
            self.assertEquals(term.quarter, 'autumn')

    def test_all_viewable_terms(self):
        with self.settings(PAST_TERMS_VIEWABLE=2,
                           CURRENT_DATETIME_OVERRIDE='2013-10-15 00:00:00'):
            terms = all_viewable_terms()
            self.assertEquals(len(terms), 3)
            self.assertEquals(terms[0].quarter, 'autumn')
            self.assertEquals(terms[1].quarter, 'summer')
            self.assertEquals(terms[2].quarter, 'spring')

    def test_is_grading_period_open(self):
        section = get_section_by_label('2013,winter,COM,201/A')

        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-03-26 16:59:00'):
            self.assertTrue(is_grading_period_open(section))

        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-03-26 17:01:00'):
            self.assertFalse(is_grading_period_open(section))

    def test_is_graderoster_available_for_term(self):
        section = get_section_by_label('2013,winter,COM,201/A')

        # Grading period is not yet open for term
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-02-01 00:00:00'):
            self.assertFalse(is_graderoster_available_for_term(section))

        # Grading period is open for term
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-03-24 00:00:00'):
            self.assertTrue(is_graderoster_available_for_term(section))

        # Current term, date is grade_submission_deadline + 1 day
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-03-27 17:00:00'):
            self.assertTrue(is_graderoster_available_for_term(section))

        # Prior term, date is current term.census_day
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-04-12 08:00:00'):
            self.assertTrue(is_graderoster_available_for_term(section))

        # Prior term, date is current term.last_day_instruction
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-06-07 08:00:00'):
            self.assertTrue(is_graderoster_available_for_term(section))

        # Prior term, date is current term.grade_submission_deadline
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-06-18 08:00:00'):
            self.assertFalse(is_graderoster_available_for_term(section))
