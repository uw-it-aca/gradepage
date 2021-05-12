# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase, override_settings
from course_grader.dao.csv import InsensitiveDictReader, grades_for_section
from course_grader.dao.section import get_section_by_label
from course_grader.dao.person import PWS
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
import os


@fdao_sws_override
@fdao_pws_override
class CVSDAOFunctionsTest(TestCase):
    def test_grades_for_section(self):
        # Section/user do not matter here
        section = get_section_by_label('2013,spring,A B&C,101/A')
        user = PWS().get_person_by_regid('FBB38FE46A7C11D5A4AE0004AC494FFE')

        resource_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "resources", "csv"))

        f = open(os.path.join(resource_path, "test1.csv"))
        r = grades_for_section(section, user, f)
        self.assertEqual(len(r.get("grades")), 6)
        f.close()

        f = open(os.path.join(resource_path, "test2.csv"))
        r = grades_for_section(section, user, f)
        self.assertEqual(len(r.get("grades")), 6)
        f.close()


class InsensitiveDictReaderTest(TestCase):
    def test_insensitive_dict_reader(self):
        resource_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "resources", "csv"))

        f = open(os.path.join(resource_path, "test3.csv"))
        reader = InsensitiveDictReader(f)
        row = next(reader)

        self.assertEqual(row.get("Field1"), "ok1")
        self.assertEqual(row.get("Field2"), "ok2")
        self.assertEqual(row.get("Field3"), "ok3")
        self.assertEqual(row.get("Field4"), "ok4")
        self.assertEqual(row.get("Field5"), "ok5")
        self.assertEqual(row.get("Field6"), "")
        self.assertEqual(row.get("Field7"), None)

        f.close()
