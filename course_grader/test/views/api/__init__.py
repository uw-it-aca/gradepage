from django.test import TestCase
from restclients.pws import PWS
from restclients.sws.section import get_section_by_label
from restclients.sws.graderoster import get_graderoster
from course_grader.views.api import *


class ViewAPIFunctionsTest(TestCase):
    def test_graderoster_status_params(self):
        with self.settings(
                RESTCLIENTS_SWS_DAO_CLASS='restclients.dao_implementation.sws.File',
                RESTCLIENTS_PWS_DAO_CLASS='restclients.dao_implementation.pws.File'):

            section = get_section_by_label('2013,spring,TRAIN,101/B')
            user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')
            graderoster = get_graderoster(section, user, requestor=user)

            p = graderoster_status_params(graderoster)
            self.assertEquals(p['unsubmitted_count'], 0)
            self.assertEquals(p['submitted_count'], 1)
