from django.test import TestCase
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
from course_grader.dao.person import PWS
from course_grader.dao.graderoster import get_graderoster
from course_grader.dao.section import get_section_by_label
from course_grader.dao.notification import *


@fdao_sws_override
@fdao_pws_override
class NotificationDAOFunctionsTest(TestCase):
    def test_graderoster_people(self):
        section = get_section_by_label('2013,summer,CSS,161/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')
        graderoster = get_graderoster(section, user, requestor=user)

	p = graderoster_people(graderoster)
        self.assertEquals(len(p), 3)

    def test_create_recipient_list(self):
	section = get_section_by_label('2013,summer,CSS,161/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')
        graderoster = get_graderoster(section, user, requestor=user)

	people = graderoster_people(graderoster)
	r = create_recipient_list(people)
	self.assertEquals(len(r), 3)
        r.sort()
        self.assertEquals(r[0], 'bill@uw.edu')
        self.assertEquals(r[1], 'fred@uw.edu')
        self.assertEquals(r[2], 'james@uw.edu')
