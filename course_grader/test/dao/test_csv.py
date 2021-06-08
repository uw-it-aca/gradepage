# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase, override_settings
from course_grader.dao.csv import InsensitiveDictReader, GradeImportCSV
from course_grader.dao.section import get_section_by_label
from course_grader.dao.person import PWS
from course_grader.exceptions import InvalidCSV
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
import os


@fdao_sws_override
@fdao_pws_override
class CVSDAOFunctionsTest(TestCase):
    def setUp(self):
        self.resource_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "resources", "csv"))

    def test_is_true(self):
        grade_import = GradeImportCSV()
        self.assertTrue(grade_import.is_true("1"))
        self.assertTrue(grade_import.is_true("Y"))
        self.assertTrue(grade_import.is_true("Yes"))
        self.assertTrue(grade_import.is_true("TRUE"))
        self.assertFalse(grade_import.is_true("0"))
        self.assertFalse(grade_import.is_true("N"))
        self.assertFalse(grade_import.is_true("NO"))
        self.assertFalse(grade_import.is_true("F"))
        self.assertFalse(grade_import.is_true(""))

    def test_validate(self):
        grade_import = GradeImportCSV()

        fileobj = open(os.path.join(self.resource_path, "test1.csv"))
        r = grade_import.validate(fileobj)
        self.assertEqual(grade_import.has_header, True)
        self.assertEqual(grade_import.dialect.delimiter, ",")

        fileobj = open(os.path.join(self.resource_path, "missing_header.csv"))
        self.assertRaisesRegex(
            InvalidCSV, "Missing header row$", grade_import.validate, fileobj)

        fileobj = open(os.path.join(self.resource_path, "missing_grade.csv"))
        self.assertRaisesRegex(
            InvalidCSV, "Missing grade header$", grade_import.validate,
            fileobj)

    def test_grades_for_section(self):
        # Section/user do not matter here
        section = get_section_by_label("2013,spring,A B&C,101/A")
        user = PWS().get_person_by_regid("FBB38FE46A7C11D5A4AE0004AC494FFE")

        f = open(os.path.join(self.resource_path, "test1.csv"))
        r = GradeImportCSV().grades_for_section(section, user, fileobj=f)
        self.assertEqual(len(r.get("grades")), 6)
        self.assertEqual(
            len([g for g in r["grades"] if g["is_incomplete"] is True]), 2)
        self.assertEqual(
            len([g for g in r["grades"] if g["is_writing"] is True]), 2)
        f.close()

        f = open(os.path.join(self.resource_path, "test2.csv"))
        r = GradeImportCSV().grades_for_section(section, user, fileobj=f)
        self.assertEqual(len(r.get("grades")), 6)
        f.close()


class InsensitiveDictReaderTest(CVSDAOFunctionsTest):
    def test_insensitive_dict_reader(self):
        f = open(os.path.join(self.resource_path, "test3.csv"))
        reader = InsensitiveDictReader(f)

        row = next(reader)
        self.assertEqual(row.get("Field1"), "ök1")
        self.assertEqual(row.get("Field2"), "øk2")
        self.assertEqual(row.get("Field3"), "ok3")
        self.assertEqual(row.get("Field4"), "ok4")
        self.assertEqual(row.get("Field5"), "ok5")
        self.assertEqual(row.get("Field6"), "")
        self.assertEqual(row.get("Field7"), None)
        f.close()
