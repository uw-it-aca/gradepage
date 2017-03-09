from django.test import TestCase
from restclients.pws import PWS
from restclients.sws.section import get_section_by_label
from restclients.sws.graderoster import get_graderoster
from restclients.test import fdao_sws_override, fdao_pws_override
from course_grader.views.api import *


@fdao_sws_override
@fdao_pws_override
class ViewAPIFunctionsTest(TestCase):
    def test_graderoster_status_params(self):
        section = get_section_by_label('2013,spring,TRAIN,101/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')
        graderoster = get_graderoster(section, user, requestor=user)

        p = graderoster_status_params(graderoster)
        self.assertEquals(p['unsubmitted_count'], 994)
        self.assertEquals(p['submitted_count'], 3)
        self.assertEquals(p['deadline_warning'], True)

        section = get_section_by_label('2013,spring,TRAIN,101/B')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')
        graderoster = get_graderoster(section, user, requestor=user)

        p = graderoster_status_params(graderoster)
        self.assertEquals(p['unsubmitted_count'], 0)
        self.assertEquals(p['submitted_count'], 1)
        self.assertEquals('deadline_warning' in p, False)

    def test_item_is_submitted(self):
        section = get_section_by_label('2013,spring,TRAIN,101/B')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')
        graderoster = get_graderoster(section, user, requestor=user)

        item = graderoster.items[0]
        self.assertEquals(item_is_submitted(item), True)

        item.is_auditor = True
        self.assertEquals(item_is_submitted(item), False)
        item.is_auditor = False

        item.date_withdrawn = '2013-05-01'
        self.assertEquals(item_is_submitted(item), False)
        item.date_withdrawn = None

        item.date_graded = None
        item.grade = None
        item.no_grade_now = False
        self.assertEquals(item_is_submitted(item), False)

        item.no_grade_now = True
        self.assertEquals(item_is_submitted(item), True)

    def test_sorted_students(self):
        section = get_section_by_label('2013,spring,TRAIN,101/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')
        graderoster = get_graderoster(section, user, requestor=user)

        graderoster.items[0].student_surname = 'ZZZZZZZZZ'
        graderoster.items[-1].student_surname = '000000000'

        s = sorted_students(graderoster.items)
        self.assertEquals(s[0].student_surname, '000000000')
        self.assertEquals(s[-1].student_surname, 'ZZZZZZZZZ')

    def test_sorted_grades(self):
        section = get_section_by_label('2013,spring,TRAIN,101/B')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')
        graderoster = get_graderoster(section, user, requestor=user)
        item = graderoster.items[0]

        s = sorted_grades(item.grade_choices)

        self.assertEquals(s[0], '')
        self.assertEquals(s[1], 'CR')
        self.assertEquals(s[-1], 'NC')

        item.grade_choices.extend(['4.0', '2.5', '0.0'])

        s = sorted_grades(item.grade_choices)
        self.assertEquals(s[0], '')
        self.assertEquals(s[1], 'CR')
        self.assertEquals(s[-2], '2.5')
        self.assertEquals(s[-1], '0.0')

