from django.test import TestCase, override_settings
from uw_sws.util import fdao_sws_override
from course_grader.dao.term import current_term
from course_grader.dao.message import (
    get_open_grading_messages, get_closed_grading_messages)


@fdao_sws_override
@override_settings(TIME_ZONE='UTC')
class MessageDAOFunctionsTest(TestCase):
    fixtures = ['persistent_messages.json']

    def test_get_closed_grading_messages(self):
        # Grading closed, next quarter not yet begun
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-09-15 00:00:00'):
            messages = get_closed_grading_messages()
            self.assertEqual(messages['message_level'], 'danger')
            self.assertEqual(messages['messages'][0], (
                'Grade submission for <strong>Summer 2013</strong> closed on '
                'August 27 at  5:00 PM UTC. Summer 2013 grades can no longer '
                'be submitted online. <a href="https://itconnect.uw.edu/learn'
                '/tools/gradepage/change-submitted-grades/" target="_blank" '
                'title="What can I do now?">What can I do now?</a><br />Grade'
                ' submission for <strong>Autumn 2013</strong> opens on '
                'November 18 at  8:00 AM UTC.'))

        # Grading closed
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-10-15 00:00:00'):
            messages = get_closed_grading_messages()
            self.assertEqual(messages['message_level'], 'info')
            self.assertEqual(messages['messages'][0], (
                'Grade submission for <strong>Autumn 2013</strong> opens on '
                'November 18 at  8:00 AM UTC.<br />Grade submission for '
                '<strong>Summer 2013</strong> closed on August 27 at  5:00 PM '
                'UTC. Summer 2013 grades can no longer be submitted online. '
                '<a href="https://itconnect.uw.edu/learn/tools/gradepage/'
                'change-submitted-grades/" target="_blank" title="What can I '
                'do now?">What can I do now?</a>'))

    def test_get_open_grading_messages(self):
        # Grading open
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-12-10 00:00:00',
                           SUBMISSION_DEADLINE_WARNING_HOURS=48):
            messages = get_open_grading_messages(current_term())
            self.assertEqual(messages['message_level'], 'warning')
            self.assertEqual(messages['messages'][0], (
                'Autumn 2013 grades are due on <strong>December 17, 5:00 PM '
                'UTC</strong>.'))

        # Grading open, submission deadline warning
        with self.settings(CURRENT_DATETIME_OVERRIDE='2013-12-16 00:00:00',
                           SUBMISSION_DEADLINE_WARNING_HOURS=48):
            messages = get_open_grading_messages(current_term())
            self.assertEqual(messages['message_level'], 'danger')
            self.assertEqual(messages['messages'][0].startswith(
                '<strong>Attention!</strong> The grading period closes'), True)
            self.assertEqual(messages['messages'][0].endswith(
                'Grades cannot be submitted online after deadline.'), True)
