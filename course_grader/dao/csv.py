# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from course_grader.dao import GradeImportSource
from course_grader.dao.person import person_from_netid
from course_grader.exceptions import InvalidCSV
from restclients_core.exceptions import InvalidNetID, DataFailureException
from logging import getLogger
import csv

logger = getLogger(__name__)


class InsensitiveDict(dict):
    """
    Override the get method to strip() and lower() the input key, and
    strip() the returned value.
    """
    def get(self, k, default=None):
        try:
            return super().get(k.strip().lower(), default).strip()
        except AttributeError:
            return None


class InsensitiveDictReader(csv.DictReader):
    """
    Override the csv.fieldnames property to strip() and lower() the fieldnames.
    """
    @property
    def fieldnames(self):
        return [field.strip().lower() for field in super().fieldnames]

    def __next__(self):
        return InsensitiveDict(super().__next__())


class GradeImportCSV(GradeImportSource):
    def decode_file(self, csvfile):
        try:
            return csvfile.decode("utf-8")
        except UnicodeDecodeError as ex:
            return csvfile.decode("utf-16")
        except AttributeError:
            return csvfile

    def validate(self, fileobj):
        decoded_file = self.decode_file(fileobj.read(4096))
        self.has_header = csv.Sniffer().has_header(decoded_file)
        self.dialect = csv.Sniffer().sniff(decoded_file)

        reader = InsensitiveDictReader(decoded_file.splitlines(),
                                       dialect=self.dialect)
        if ("grade" not in reader.fieldnames and
                "current score" not in reader.fieldnames):
            raise InvalidCSV("Missing grade header")

        if ("uwregid" not in reader.fieldnames and
                "sis user id" not in reader.fieldnames and
                "studentno" not in reader.fieldnames):
            raise InvalidCSV("Missing student identifer header")

        fileobj.seek(0, 0)

    def grades_for_section(self, section, instructor, **kwargs):
        """
        Convert CSV file object into normalized JSON

        Supported column names are:

        "UWRegID" OR "SIS User ID" OR "StudentNo" (required),
        "Grade" OR "Current Score" (required),
        "Incomplete" (optional),
        "WritingCredit" (optional)

        All other field names are ignored.
        """
        fileobj = kwargs.get("fileobj")
        self.validate(fileobj)
        decoded_file = self.decode_file(fileobj.read()).splitlines()

        grade_data = []
        for row in InsensitiveDictReader(decoded_file, dialect=self.dialect):
            student_data = {
                "student_reg_id": row.get("UWRegID") or row.get("SIS User ID"),
                "student_number": row.get("StudentNo"),
                "grade": row.get("Grade") or row.get("Current Score"),
                "is_incomplete": self.is_true(row.get("Incomplete")),
                "is_writing": self.is_true(row.get("WritingCredit")),
            }
            if (student_data["student_reg_id"] or
                    student_data["student_number"]):
                grade_data.append(student_data)

        return {"grades": grade_data}
