# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.test import TestCase
from django.utils import timezone
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
from course_grader.dao.person import PWS
from course_grader.dao.section import get_section_by_label
from course_grader.dao.graderoster import (
    graderoster_for_section, DataFailureException)
from course_grader.models import SubmittedGradeRoster
from course_grader.exceptions import (
    GradingNotPermitted, ReceiptNotFound, GradingPeriodNotOpen)


@fdao_sws_override
@fdao_pws_override
class GraderosterDAOFunctionsTest(TestCase):
    def test_graderoster_for_section(self):
        section = get_section_by_label('2013,spring,TRAIN,101/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')
        gr = graderoster_for_section(section, user, user)
        self.assertEqual(len(gr.items), 1000)

        section = get_section_by_label('2013,spring,TRAIN,101/B')
        gr = graderoster_for_section(section, user, user)
        self.assertEqual(len(gr.items), 2)

    def test_submitted_graderoster_for_section(self):
        section = get_section_by_label('2013,spring,TRAIN,101/B')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')

        gr = graderoster_for_section(section, user, user)
        self.assertEqual(len(gr.items), 2)
        self.assertFalse(hasattr(gr, 'submission_id'))

        model = SubmittedGradeRoster(
            section_id='2013,spring,TRAIN,101/B',
            instructor_id='FBB38FE46A7C11D5A4AE0004AC494FFE',
            term_id='2013,spring',
            submitted_date=timezone.now(),
            submitted_by='FBB38FE46A7C11D5A4AE0004AC494FFE',
            accepted_date=timezone.now(),
            status_code=200,
            document=gr.xhtml()
        )
        model.save()

        gr = graderoster_for_section(section, user, user)
        self.assertEqual(len(gr.items), 2)
        self.assertFalse(hasattr(gr, 'submission_id'))

        # Test handing of etree.XMLSyntaxError
        model.document = '<' + model.document
        model.save()
        self.assertRaises(DataFailureException, graderoster_for_section,
                          section, user, user)

    def test_submitted_only_graderoster_for_section(self):
        section = get_section_by_label('2013,spring,TRAIN,101/B')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')

        self.assertRaises(
            ReceiptNotFound, graderoster_for_section, section, user, user,
            submitted_graderosters_only=True)

        gr = graderoster_for_section(section, user, user)

        model = SubmittedGradeRoster(
            section_id='2013,spring,TRAIN,101/B',
            instructor_id='FBB38FE46A7C11D5A4AE0004AC494FFE',
            term_id='2013,spring',
            submitted_date=timezone.now(),
            submitted_by='FBB38FE46A7C11D5A4AE0004AC494FFE',
            accepted_date=timezone.now(),
            status_code=200,
            document=gr.xhtml()
        )
        model.save()

        gr = graderoster_for_section(
            section, user, user, submitted_graderosters_only=True)
        self.assertEqual(len(gr.items), 2)
        self.assertEqual(gr.submission_id, 'B')

    def test_graderoster_not_permitted(self):
        section = get_section_by_label('2013,spring,TRAIN,100/AA')
        user = PWS().get_person_by_regid('9136CCB8F66711D5BE060004AC494FFE')

        self.assertRaises(
            GradingNotPermitted, graderoster_for_section, section, user, user)
