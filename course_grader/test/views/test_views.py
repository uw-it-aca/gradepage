# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
from course_grader.dao.person import PWS
from course_grader.dao.section import get_section_by_label
from course_grader.dao.term import get_term_by_year_and_quarter
from course_grader.views import *


@fdao_sws_override
@fdao_pws_override
class ViewFunctionsTest(TestCase):
    def test_clean_section_id(self):
        self.assertEquals(
            clean_section_id(
                '2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
            '2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

        self.assertEquals(
            clean_section_id(
                '2013-spring-T RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE'),
            '2013-spring-T_RAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')

        self.assertEquals(
            clean_section_id(
                '2013-spring-AB&C-101-A-9136CCB8F66711D5BE060004AC494FFE'),
            '2013-spring-AB_C-101-A-9136CCB8F66711D5BE060004AC494FFE')

    def test_url_for_term(self):
        term = get_term_by_year_and_quarter(2013, 'spring')
        self.assertEquals(url_for_term(term), '/?term=2013-spring')

    def test_url_for_section(self):
        with self.settings(GRADEPAGE_HOST=''):
            self.assertEquals(
                url_for_section((
                    '2013-spring-TRAIN-101-A-'
                    '9136CCB8F66711D5BE060004AC494FFE')), (
                    '/section/2013-spring-TRAIN-101-A-'
                    '9136CCB8F66711D5BE060004AC494FFE'))

            self.assertEquals(
                url_for_section((
                    '2013-spring-T RAIN-101-A-'
                    '9136CCB8F66711D5BE060004AC494FFE')), (
                    '/section/2013-spring-T%20RAIN-101-A-'
                    '9136CCB8F66711D5BE060004AC494FFE'))

        with self.settings(GRADEPAGE_HOST='https://abc.edu'):
            self.assertEquals(
                url_for_section((
                    '2013-spring-TRAIN-101-A-'
                    '9136CCB8F66711D5BE060004AC494FFE')), (
                    '/section/2013-spring-TRAIN-101-'
                    'A-9136CCB8F66711D5BE060004AC494FFE'))

            self.assertEquals(
                url_for_section((
                    '2013-spring-T RAIN-101-A-'
                    '9136CCB8F66711D5BE060004AC494FFE')), (
                    '/section/2013-spring-T%20RAIN-101-'
                    'A-9136CCB8F66711D5BE060004AC494FFE'))

    def test_url_for_grading_status(self):
        with self.settings(GRADEPAGE_HOST=''):
            self.assertEquals(
                url_for_grading_status((
                    '2013-spring-TRAIN-101-A-'
                    '9136CCB8F66711D5BE060004AC494FFE')), (
                    '/api/v1/grading_status/2013-spring-TRAIN-101-'
                    'A-9136CCB8F66711D5BE060004AC494FFE'))

            self.assertEquals(
                url_for_grading_status((
                    '2013-spring-T RAIN-101-A-'
                    '9136CCB8F66711D5BE060004AC494FFE')), (
                    '/api/v1/grading_status/2013-spring-T%20RAIN-101-'
                    'A-9136CCB8F66711D5BE060004AC494FFE'))

        with self.settings(GRADEPAGE_HOST='https://abc.edu'):
            self.assertEquals(
                url_for_grading_status((
                    '2013-spring-TRAIN-101-A-'
                    '9136CCB8F66711D5BE060004AC494FFE')), (
                    '/api/v1/grading_status/2013-spring-TRAIN-'
                    '101-A-9136CCB8F66711D5BE060004AC494FFE'))

            self.assertEquals(
                url_for_grading_status((
                    '2013-spring-T RAIN-101-A-'
                    '9136CCB8F66711D5BE060004AC494FFE')), (
                    '/api/v1/grading_status/2013-spring-T%20RAIN-'
                    '101-A-9136CCB8F66711D5BE060004AC494FFE'))

    def test_url_for_graderoster(self):
        self.assertEquals(
            url_for_graderoster((
                '2013-spring-TRAIN-101-A-'
                '9136CCB8F66711D5BE060004AC494FFE')), (
                '/api/v1/graderoster/2013-spring-TRAIN-'
                '101-A-9136CCB8F66711D5BE060004AC494FFE'))

        self.assertEquals(
            url_for_graderoster((
                '2013-spring-T RAIN-101-A-'
                '9136CCB8F66711D5BE060004AC494FFE')), (
                '/api/v1/graderoster/2013-spring-T%20RAIN-'
                '101-A-9136CCB8F66711D5BE060004AC494FFE'))

    def test_url_for_import(self):
        self.assertEquals(
            url_for_import((
                '2013-spring-TRAIN-101-A-'
                '9136CCB8F66711D5BE060004AC494FFE')), (
                '/api/v1/import/2013-spring-TRAIN-'
                '101-A-9136CCB8F66711D5BE060004AC494FFE'))

        self.assertEquals(
            url_for_import((
                '2013-spring-T RAIN-101-A-'
                '9136CCB8F66711D5BE060004AC494FFE')), (
                '/api/v1/import/2013-spring-T%20RAIN-'
                '101-A-9136CCB8F66711D5BE060004AC494FFE'))

    def test_url_for_upload(self):
        self.assertEquals(
            url_for_upload((
                '2013-spring-TRAIN-101-A-'
                '9136CCB8F66711D5BE060004AC494FFE')), (
                '/api/v1/import_file/2013-spring-TRAIN-'
                '101-A-9136CCB8F66711D5BE060004AC494FFE'))

        self.assertEquals(
            url_for_upload((
                '2013-spring-T RAIN-101-A-'
                '9136CCB8F66711D5BE060004AC494FFE')), (
                '/api/v1/import_file/2013-spring-T%20RAIN-'
                '101-A-9136CCB8F66711D5BE060004AC494FFE'))

    def test_url_for_export(self):
        self.assertEquals(
            url_for_export((
                '2013-spring-TRAIN-101-A-'
                '9136CCB8F66711D5BE060004AC494FFE')), (
                '/api/v1/export/2013-spring-TRAIN-'
                '101-A-9136CCB8F66711D5BE060004AC494FFE'))

        self.assertEquals(
            url_for_export((
                '2013-spring-T RAIN-101-A-'
                '9136CCB8F66711D5BE060004AC494FFE')), (
                '/api/v1/export/2013-spring-T%20RAIN-'
                '101-A-9136CCB8F66711D5BE060004AC494FFE'))

    def test_section_status_params(self):
        section = get_section_by_label('2013,summer,TRAIN,101/A')
        user = PWS().get_person_by_netid('javerage')

        p = section_status_params(section, user)

        self.assertEquals(p['grading_period_open'], False)
        self.assertEquals(
            p['grade_submission_deadline'], '2013-08-27T17:00:00')
        self.assertEquals(
            p['grading_status'], (
                'Summer B-term grade submission opens on August 16 '
                'at  8:00 AM PDT.'))
