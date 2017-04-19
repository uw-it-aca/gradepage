from django.test import TestCase
from uw_sws.util import fdao_sws_override
from course_grader.dao.term import *
from course_grader.exceptions import InvalidTerm


@fdao_sws_override
class TermDAOFunctionsTest(TestCase):
    def test_submission_deadline_warning(self):
        term = term_from_param('2013-autumn')
        with self.settings(SUBMISSION_DEADLINE_WARNING_HOURS=48,
                           CURRENT_DATETIME_OVERRIDE='2013-10-15 00:00:00'):
            self.assertEquals(submission_deadline_warning(term), False)

        with self.settings(SUBMISSION_DEADLINE_WARNING_HOURS=48,
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

