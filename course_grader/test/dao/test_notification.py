from django.test import TestCase
from django.test.utils import override_settings
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
from course_grader.dao.person import PWS
from course_grader.dao.graderoster import get_graderoster
from course_grader.dao.section import get_section_by_label
from course_grader.dao.notification import *


@fdao_sws_override
@fdao_pws_override
class NotificationDAOFunctionsTest(TestCase):
    def setUp(self):
        pws = PWS()
        self.section = get_section_by_label('2013,summer,CSS,161/A')
        self.user = pws.get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')
        self.graderoster = get_graderoster(
            self.section, self.user, requestor=self.user)

    def test_graderoster_people(self):
        p = graderoster_people(self.graderoster)
        self.assertEquals(len(p), 3)

    def test_create_recipient_list(self):
        people = graderoster_people(self.graderoster)
        r = create_recipient_list(people)
        self.assertEquals(len(r), 3)
        r.sort()
        self.assertEquals(r[0], 'bill@uw.edu')
        self.assertEquals(r[1], 'fred@uw.edu')
        self.assertEquals(r[2], 'james@uw.edu')

    @override_settings(CURRENT_DATETIME_OVERRIDE="2013-08-04 10:00:00")
    def test_create_message_success(self):
        for item in self.graderoster.items:
            item.status_code = '200'

        (subject, text, html) = create_message(self.graderoster, self.user)

        self.assertEquals(
            subject, 'Bill Teacher submitted four grades for CSS 161 A')
        self.assertEquals(text, '\nBill Teacher submitted grades for four students to the Registrar on August 04 at 10:00 AM UTC.  These grades have been successfully processed and will be available to the students via MyUW.\n\nTo view or print a copy of this grade submission for your records, go to: http://localhost/section/2013-summer-CSS-161-A-FBB38FE46A7C11D5A4AE0004AC494FFE\n\nNo changes can be made through GradePage.  To change submitted grades use the Change of Grade form: https://depts.washington.edu/registra/staffFaculty/gradeChange/\n\n\n')
        self.assertEquals(html, '\n<p>Bill Teacher submitted grades for four students to the Registrar on August 04 at 10:00 AM UTC.  These grades have been successfully processed and will be available to the students via MyUW.\n</p>\n\n<a href="http://localhost/section/2013-summer-CSS-161-A-FBB38FE46A7C11D5A4AE0004AC494FFE">View or print a copy of this grade submission for your records.</a>\n\n<p>No changes can be made through GradePage.  To change submitted grades, use the <a href="https://depts.washington.edu/registra/staffFaculty/gradeChange/">Change of Grade form</a>.</p>\n\n\n')

    @override_settings(CURRENT_DATETIME_OVERRIDE="2013-08-04 10:00:00")
    def test_create_message_failure(self):
        for item in self.graderoster.items:
            item.status_code = '400'

        (subject, text, html) = create_message(self.graderoster, self.user)

        self.assertEquals(
            subject, 'Failed grade submission attempt for CSS 161 A')
        self.assertEquals(text, '\nBill Teacher unsuccessfully submitted grades for four students to the Registrar on August 04 at 10:00 AM UTC.  There was a problem processing these grades and they have not been submitted.\n\nNo changes can be made through GradePage.  To change submitted grades, use the Change of Grade form: https://depts.washington.edu/registra/staffFaculty/gradeChange/\n\n\n')
        self.assertEquals(html, '\n<p>Bill Teacher unsuccessfully submitted grades for four students to the Registrar on August 04 at 10:00 AM UTC.  There was a problem processing these grades and they have not been submitted.  For more information, see the <a href="http://localhost/section/2013-summer-CSS-161-A-FBB38FE46A7C11D5A4AE0004AC494FFE">grade submission receipt</a>.</p>\n\n<p>No changes can be made through GradePage.  To change submitted grades, use the <a href="https://depts.washington.edu/registra/staffFaculty/gradeChange/">Change of Grade form</a>.</p>\n\n\n')

    @override_settings(CURRENT_DATETIME_OVERRIDE="2013-08-04 10:00:00")
    def test_create_message_partial(self):
        for item in self.graderoster.items:
            item.status_code = '200'
        self.graderoster.items[0].status_code = '400'

        (subject, text, html) = create_message(self.graderoster, self.user)

        self.assertEquals(
            subject, 'Failed grade submission attempt for CSS 161 A')
        self.assertEquals(text, '\nBill Teacher submitted grades for four students to the Registrar on August 04 at 10:00 AM UTC.  These grades have been successfully processed and will be available to the students via MyUW.\n\nHowever, one grade failed to be submitted successfully.  For more information, see the grade submission receipt: http://localhost/section/2013-summer-CSS-161-A-FBB38FE46A7C11D5A4AE0004AC494FFE\n\nNo changes can be made through GradePage.  To change submitted grades, use the Change of Grade form: https://depts.washington.edu/registra/staffFaculty/gradeChange/\n\n\n')
        self.assertEquals(html, '\n<p>Bill Teacher submitted grades for four students to the Registrar on August 04 at 10:00 AM UTC.  These grades have been successfully processed and will be available to the students via MyUW.\n</p>\n\n<p>However, one grade failed to be submitted successfully.  For more information, see the <a href="http://localhost/section/2013-summer-CSS-161-A-FBB38FE46A7C11D5A4AE0004AC494FFE">grade submission receipt</a>.</p>\n\n<p>No changes can be made through GradePage.  To change submitted grades, use the <a href="https://depts.washington.edu/registra/staffFaculty/gradeChange/">Change of Grade form</a>.</p>\n\n\n')