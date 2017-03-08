from django.test import TestCase
from django.utils.timezone import utc
from restclients.pws import PWS
from restclients.sws.section import get_section_by_label
from restclients.sws.term import get_term_by_year_and_quarter
from course_grader.views import *
from datetime import datetime


class ViewFunctionsTest(TestCase):
    def test_section_url_token(self):
        with self.settings(
                RESTCLIENTS_SWS_DAO_CLASS='restclients.dao_implementation.sws.File',
                RESTCLIENTS_PWS_DAO_CLASS='restclients.dao_implementation.pws.File'):

            section = get_section_by_label('2013,spring,TRAIN,101/A')
            user = PWS().get_person_by_netid('javerage')

            self.assertEquals(section_url_token(section, user),
                              '2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

    def test_clean_section_id(self):
        self.assertEquals(
            clean_section_id('2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
            '2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

        self.assertEquals(
            clean_section_id('2013-spring-T RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
            '2013-spring-T_RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

        self.assertEquals(
            clean_section_id('2013-spring-AB&C-101-A-9136CCB8F66711D5BE060004AC494FFE'),
            '2013-spring-AB_C-101-A-9136CCB8F66711D5BE060004AC494FFE')

    def test_url_for_term(self):
        term = get_term_by_year_and_quarter(2013, 'spring')
        self.assertEquals(url_for_term(term), '/?term=2013-spring')

    def test_url_for_section(self):
        with self.settings(GRADEPAGE_HOST=''):
            self.assertEquals(
                url_for_section('2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
                '/section/2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

            self.assertEquals(
                url_for_section('2013-spring-T RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
                '/section/2013-spring-T RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

        with self.settings(GRADEPAGE_HOST='https://abc.edu'):
            self.assertEquals(
                url_for_section('2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
                'https://abc.edu/section/2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

            self.assertEquals(
                url_for_section('2013-spring-T RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
                'https://abc.edu/section/2013-spring-T RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

    def test_url_for_grading_status(self):
        with self.settings(GRADEPAGE_HOST=''):
            self.assertEquals(
                url_for_grading_status('2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
                '/api/v1/grading_status/2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

            self.assertEquals(
                url_for_grading_status('2013-spring-T RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
                '/api/v1/grading_status/2013-spring-T RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

        with self.settings(GRADEPAGE_HOST='https://abc.edu'):
            self.assertEquals(
                url_for_grading_status('2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
                'https://abc.edu/api/v1/grading_status/2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

            self.assertEquals(
                url_for_grading_status('2013-spring-T RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
                'https://abc.edu/api/v1/grading_status/2013-spring-T RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

    def test_display_datetime(self):
        with self.settings(TIME_ZONE='UTC'):
            self.assertEquals(
                display_datetime(datetime(2000, 1, 1, 14, 30)),
                'January 01 at  2:30 PM UTC')

            self.assertEquals(
                display_datetime(datetime(2000, 1, 1, 14, 30).replace(tzinfo=utc)),
                'January 01 at  2:30 PM UTC')

        with self.settings(TIME_ZONE='America/Los_Angeles'):
	    self.assertEquals(
                display_datetime(datetime(2000, 1, 1, 14, 30)),
                'January 01 at  2:30 PM PST')

            self.assertEquals(
                display_datetime(datetime(2000, 1, 1, 14, 30).replace(tzinfo=utc)),
                'January 01 at  6:30 AM PST')

    def test_display_person_name(self):
        with self.settings(
                RESTCLIENTS_PWS_DAO_CLASS='restclients.dao_implementation.pws.File'):

            user = PWS().get_person_by_netid('javerage')
            user.display_name = 'Joe Student'
            self.assertEquals(display_person_name(user), 'Joe Student')

            user = PWS().get_person_by_netid('javerage')
            user.display_name = None
            self.assertEquals(display_person_name(user), 'James Student')

    def test_display_section_name(self):
        with self.settings(
                RESTCLIENTS_SWS_DAO_CLASS='restclients.dao_implementation.sws.File',
                RESTCLIENTS_PWS_DAO_CLASS='restclients.dao_implementation.pws.File'):

            section = get_section_by_label('2013,spring,TRAIN,101/A')
            self.assertEquals(display_section_name(section), 'TRAIN 101 A')

            section = get_section_by_label('2013,spring,TRAIN,101/A')
            section.is_independent_study = True
            self.assertEquals(display_section_name(section), 'TRAIN 101 A')

    def test_section_status_params(self):
        with self.settings(
                RESTCLIENTS_SWS_DAO_CLASS='restclients.dao_implementation.sws.File',
                RESTCLIENTS_PWS_DAO_CLASS='restclients.dao_implementation.pws.File'):

            section = get_section_by_label('2013,summer,TRAIN,101/A')
            user = PWS().get_person_by_netid('javerage')

            p = section_status_params(section, user)

            self.assertEquals(p['grading_period_open'], False)
            self.assertEquals(p['grade_submission_deadline'], '2013-08-27T17:00:00')
            self.assertEquals(p['grading_status'], None)

    def test_grade_submission_deadline_params(self):
        with self.settings(
                RESTCLIENTS_SWS_DAO_CLASS='restclients.dao_implementation.sws.File'):

            term = get_term_by_year_and_quarter(2013, 'spring')
            p = grade_submission_deadline_params(term)

            self.assertEquals(p['deadline_year'], 2013)
            self.assertEquals(p['deadline_quarter'], 'Spring')
            self.assertEquals(str(p['grade_submission_deadline']), '2017-03-09 17:00:00')
