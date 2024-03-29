# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.test import TestCase
from course_grader.dao import current_datetime, display_datetime, sws_now
from django.utils.timezone import utc
from datetime import datetime


class DateTimeFunctionsTest(TestCase):
    def setUp(self):
        self.test_dt = datetime(2000, 1, 1, 14, 30)

    def test_current_datetime(self):
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-05-31 08:00:00'):
            self.assertEquals(current_datetime().strftime('%Y-%m-%d %H:%M:%S'),
                              '2013-05-31 08:00:00')

        with self.settings(CURRENT_DATETIME_OVERRIDE=None):
            self.assertEquals(current_datetime().strftime('%Y-%m-%d %H:%M'),
                              sws_now().strftime('%Y-%m-%d %H:%M'))

    def test_display_datetime(self):
        with self.settings(TIME_ZONE='UTC'):
            self.assertEquals(
                display_datetime(self.test_dt), 'January 01 at  2:30 PM UTC')

            self.assertEquals(
                display_datetime(self.test_dt.replace(tzinfo=utc)),
                'January 01 at  2:30 PM UTC')

        with self.settings(TIME_ZONE='America/Los_Angeles'):
            self.assertEquals(
                display_datetime(self.test_dt), 'January 01 at  2:30 PM PST')

            self.assertEquals(
                display_datetime(self.test_dt.replace(tzinfo=utc)),
                'January 01 at  6:30 AM PST')
