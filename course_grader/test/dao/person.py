# -*- coding: utf-8 -*-
from django.test import TestCase
from uw_pws.util import fdao_pws_override
from course_grader.dao.person import *
from course_grader.exceptions import InvalidUser


@fdao_pws_override
class PersonDAOFunctionsTest(TestCase):
    def test_person_from_netid(self):
        self.assertRaises(InvalidUser, person_from_netid, None)
        self.assertRaises(InvalidUser, person_from_netid, '123456')
        self.assertRaises(InvalidUser, person_from_netid, 'nobody')
        self.assertEquals(person_from_netid('javerage').uwregid,
                          '9136CCB8F66711D5BE060004AC494FFE')

    def test_person_from_regid(self):
        self.assertRaises(InvalidUser, person_from_regid, None)
        self.assertRaises(InvalidUser, person_from_regid, '123456')
        self.assertRaises(InvalidUser, person_from_regid,
                          'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        self.assertEquals(
            person_from_regid('9136CCB8F66711D5BE060004AC494FFE').uwnetid,
            'javerage')

    def test_is_netid(self):
        self.assertEquals(is_netid('javerage'), None)
        self.assertEquals(is_netid('Javerage'), None)
        self.assertEquals(is_netid(None), 'No override user supplied, please enter a UWNetID')
        self.assertEquals(is_netid(''), 'No override user supplied, please enter a UWNetID')
        self.assertEquals(is_netid('12345'), 'Not a valid UWNetID: ')
        self.assertEquals(is_netid('nobody'), 'Not a valid UWNetID: ')

    def test_person_display_name(self):
        user = PWS().get_person_by_netid('javerage')
        user.display_name = 'Joe Student'
        self.assertEquals(person_display_name(user), 'Joe Student')

        user = PWS().get_person_by_netid('javerage')
        user.display_name = None
        self.assertEquals(person_display_name(user), 'James Student')

        user = PWS().get_person_by_netid('javerage')
        user.display_name = 'Jôe Stüdent'
        self.assertEquals(person_display_name(user), 'Jôe Stüdent')
