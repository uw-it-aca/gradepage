# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.test import TestCase, override_settings
from course_grader.dao.csv import InsensitiveDictReader, GradeImportCSV
from course_grader.dao.section import get_section_by_label
from course_grader.dao.person import PWS
from course_grader.exceptions import InvalidCSV
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
import mock
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
        self.assertTrue(grade_import.is_true("T"))
        self.assertTrue(grade_import.is_true("TRUE"))
        self.assertFalse(grade_import.is_true("0"))
        self.assertFalse(grade_import.is_true("2"))
        self.assertFalse(grade_import.is_true("N"))
        self.assertFalse(grade_import.is_true("NO"))
        self.assertFalse(grade_import.is_true("F"))
        self.assertFalse(grade_import.is_true("Z"))
        self.assertFalse(grade_import.is_true(""))
        self.assertFalse(grade_import.is_true(None))

    def test_validate(self):
        grade_import = GradeImportCSV()

        with open(os.path.join(self.resource_path, "test1.csv"), "rb") as fh:
            r = grade_import.validate(fh)
            self.assertEqual(grade_import.has_header, True)
            self.assertEqual(grade_import.dialect.delimiter, ",")

        with open(os.path.join(
                self.resource_path, "missing_header.csv"), "rb") as fh:
            self.assertRaisesRegex(InvalidCSV, "Missing header: grade$",
                                   grade_import.validate, fh)

        with open(os.path.join(
                self.resource_path, "missing_grade.csv"), "rb") as fh:
            self.assertRaisesRegex(InvalidCSV, "Missing header: grade$",
                                   grade_import.validate, fh)

        with open(os.path.join(
                self.resource_path, "large_header.csv"), "rb") as fh:
            r = grade_import.validate(fh)
            self.assertEqual(grade_import.has_header, True)
            self.assertEqual(grade_import.dialect.delimiter, ",")

        with open(os.path.join(
                self.resource_path, "unk_delimiter.csv"), "rb") as fh:
            r = grade_import.validate(fh)
            self.assertEqual(grade_import.has_header, True)
            self.assertEqual(grade_import.dialect.delimiter, ",")

    @mock.patch("course_grader.dao.csv.default_storage.open")
    @override_settings(CURRENT_DATETIME_OVERRIDE='2013-05-18 08:10:00')
    def test_grades_for_section(self, mock_open):
        # Section/user do not matter here
        section = get_section_by_label("2013,spring,A B&C,101/A")
        user = PWS().get_person_by_regid("FBB38FE46A7C11D5A4AE0004AC494FFE")
        importer = GradeImportCSV()

        with open(os.path.join(self.resource_path, "test1.csv"), "rb") as fh:
            r = importer.grades_for_section(section, user, fileobj=fh)
            self.assertEqual(len(r.get("grades")), 6)
            self.assertEqual(
                len([g for g in r["grades"] if g["is_incomplete"] is True]), 2)
            self.assertEqual(
                len([g for g in r["grades"] if g["is_writing"] is True]), 2)
            self.assertEqual(r["grades"][0]["student_number"], "0800000")
            self.assertEqual(r["grades"][1]["student_number"], "0040000")
            self.assertEqual(r["grades"][2]["student_number"], "1000000")
            self.assertEqual(
                importer.get_filepath(),
                "2013-spring/A_B&C-101-A/bill/20130518T081000/test1.csv")

        importer = GradeImportCSV()
        with open(os.path.join(self.resource_path, "test2.csv"), "rb") as fh:
            r = importer.grades_for_section(section, user, fileobj=fh)
            self.assertEqual(len(r.get("grades")), 6)
            self.assertEqual(r["grades"][0]["student_number"], None)
            self.assertEqual(
                importer.get_filepath(),
                "2013-spring/A_B&C-101-A/bill/20130518T081000/test2.csv")

    @mock.patch("course_grader.dao.csv.default_storage.open")
    @override_settings(CURRENT_DATETIME_OVERRIDE='2013-05-18 08:10:00')
    def test_write_files(self, mock_open):
        section = get_section_by_label("2013,spring,A B&C,101/A")
        user = PWS().get_person_by_regid("FBB38FE46A7C11D5A4AE0004AC494FFE")

        with open(os.path.join(self.resource_path, "test1.csv"), "rb") as fh:
            r = GradeImportCSV()._write_file(section, user, fileobj=fh)
            mock_open.assert_called_with(
                "2013-spring/A_B&C-101-A/bill/20130518T081000/test1.csv",
                mode="w")

        with open(os.path.join(self.resource_path, "test2.csv"), "rb") as fh:
            r = GradeImportCSV()._write_file(section, user, fileobj=fh)
            mock_open.assert_called_with(
                "2013-spring/A_B&C-101-A/bill/20130518T081000/test2.csv",
                mode="w")


class InsensitiveDictReaderTest(CVSDAOFunctionsTest):
    def test_insensitive_dict_reader(self):
        with open(os.path.join(self.resource_path, "test3.csv")) as fh:
            reader = InsensitiveDictReader(fh)

            row = next(reader)
            self.assertEqual(row.get("Field1"), "ök1")
            self.assertEqual(row.get("Field2"), "øk2")
            self.assertEqual(row.get("Field3"), "ok3")
            self.assertEqual(row.get("Field4"), "ok4")
            self.assertEqual(row.get("Field 5", "Field5"), "ok5")
            self.assertEqual(row.get("Field6", "field 6"), "")
            self.assertEqual(row.get("Field7"), "")
            self.assertEqual(row.get("Field8"), None)
