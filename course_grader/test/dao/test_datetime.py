# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.test import TestCase
from course_grader.dao import current_datetime, display_datetime, sws_now
from datetime import datetime, timezone


class DateTimeFunctionsTest(TestCase):
    def setUp(self):
        self.test_dt = datetime(2000, 1, 1, 14, 30)

    def test_current_datetime(self):
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-05-31 08:00:00'):
            self.assertEqual(current_datetime().strftime('%Y-%m-%d %H:%M:%S'),
                             '2013-05-31 08:00:00')

        with self.settings(CURRENT_DATETIME_OVERRIDE=None):
            self.assertEqual(current_datetime().strftime('%Y-%m-%d %H:%M'),
                             sws_now().strftime('%Y-%m-%d %H:%M'))

    def test_display_datetime(self):
        with self.settings(TIME_ZONE='UTC'):
            self.assertEqual(
                display_datetime(self.test_dt), 'January 01 at  2:30 PM UTC')

            self.assertEqual(
                display_datetime(self.test_dt.replace(tzinfo=timezone.utc)),
                'January 01 at  2:30 PM UTC')

        with self.settings(TIME_ZONE='America/Los_Angeles'):
            self.assertEqual(
                display_datetime(self.test_dt), 'January 01 at  2:30 PM PST')

            self.assertEqual(
                display_datetime(self.test_dt.replace(tzinfo=timezone.utc)),
                'January 01 at  6:30 AM PST')
