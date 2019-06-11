from django.test import TestCase
from course_grader.dao.person import PWS
from course_grader.dao.section import get_section_by_label
from course_grader.dao.graderoster import get_graderoster
from restclients_core.exceptions import DataFailureException
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
from course_grader.views.rest_dispatch import RESTDispatch, timeout_error
from course_grader.views.api import *


class RestDispatchTest(TestCase):
    def test_data_failure_error(self):
        ex = DataFailureException(url='/', status=404, msg='Not found')
        self.assertEqual(
            (404, 'Not found'), RESTDispatch.data_failure_error(ex))

        ex = DataFailureException(url='/', status=500, msg='Server error')
        self.assertEqual(
            (543, 'Server error'), RESTDispatch.data_failure_error(ex))

        ex = DataFailureException(url='/', status=0, msg='Timeout')
        self.assertEqual(
            (543, timeout_error), RESTDispatch.data_failure_error(ex))

    def test_error_response(self):
        response = RESTDispatch.error_response(400, message='Error')
        self.assertEqual(response.content, b'{"error": "Error"}')
        self.assertEqual(response.status_code, 400)

        response = RESTDispatch.error_response(500, message=Exception('Error'))
        self.assertEqual(response.content, b'{"error": "Error"}')
        self.assertEqual(response.status_code, 500)

    def test_json_response(self):
        response = RESTDispatch.json_response('Test')
        self.assertEqual(response.content, b'"Test"')
        self.assertEqual(response.status_code, 200)

        response = RESTDispatch.json_response({'Test': 3, 'Another Test': 4})
        self.assertEqual(response.content, b'{"Another Test": 4, "Test": 3}')
        self.assertEqual(response.status_code, 200)

    def test_csv_response(self):
        response = RESTDispatch.csv_response(filename="test")
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="test.csv"')

        response = RESTDispatch.csv_response(filename="test/test")
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="test-test.csv"')


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
