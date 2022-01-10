# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.files.storage import default_storage
from course_grader.dao import GradeImportSource, current_datetime
from course_grader.dao.person import person_from_netid
from course_grader.exceptions import InvalidCSV
from restclients_core.exceptions import InvalidNetID, DataFailureException
from logging import getLogger
import chardet
import csv
import os

logger = getLogger(__name__)

STUDENT_NUM_LEN = 7


class InsensitiveDict(dict):
    """
    Override the get method to strip() and lower() the input key, and
    strip() the returned value.
    """
    def get(self, *k, default=None):
        for i in k:
            if i.strip().lower() in self:
                try:
                    return super().get(i.strip().lower()).strip()
                except AttributeError:
                    break
        return default


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
    def __init__(self):
        self.encoding = None

    def decode_file(self, csvfile):
        if not self.encoding:
            result = chardet.detect(csvfile)
            self.encoding = result["encoding"]
        return csvfile.decode(self.encoding)

    def validate(self, fileobj):
        # Read the first line of the file to validate the header
        decoded_file = self.decode_file(fileobj.readline())
        self.has_header = csv.Sniffer().has_header(decoded_file)
        self.dialect = csv.Sniffer().sniff(decoded_file)

        reader = InsensitiveDictReader(decoded_file.splitlines(),
                                       dialect=self.dialect)

        if ("import grade" not in reader.fieldnames and
                "importgrade" not in reader.fieldnames):
            raise InvalidCSV("Missing header: grade")

        if ("uwregid" not in reader.fieldnames and
                "sis user id" not in reader.fieldnames and
                "studentno" not in reader.fieldnames):
            raise InvalidCSV("Missing header: student")

        fileobj.seek(0, 0)

    def grades_for_section(self, section, instructor, **kwargs):
        """
        Convert CSV file object into normalized JSON

        Supported column names are:

        "UWRegID" OR "SIS User ID" OR "StudentNo" (required),
        "Import Grade" OR "ImportGrade" (required),
        "Incomplete" (optional),
        "Writing Credit" OR "WritingCredit" (optional)

        All other field names are ignored.
        """
        fileobj = kwargs.get("fileobj")
        self.validate(fileobj)
        decoded_file = self.decode_file(fileobj.read()).splitlines()

        grade_data = []
        for row in InsensitiveDictReader(decoded_file, dialect=self.dialect):
            student_number = row.get("StudentNo")
            student_data = {
                "student_reg_id": row.get("UWRegID", "SIS User ID"),
                "student_number": student_number.zfill(STUDENT_NUM_LEN) if (
                    student_number is not None) else student_number,
                "grade": row.get("Import Grade", "ImportGrade"),
                "is_incomplete": self.is_true(row.get("Incomplete")),
                "is_writing": self.is_true(
                    row.get("Writing Credit", "WritingCredit")),
            }
            if (student_data["student_reg_id"] or
                    student_data["student_number"]):
                grade_data.append(student_data)

        try:
            self._write_file(section, instructor, fileobj)
        except Exception as ex:
            logger.error("WRITE upload file {} for {} failed: {}".format(
                fileobj.name, section.section_label(), ex))

        return {"grades": grade_data}

    def _write_file(self, section, instructor, fileobj):
        """
        Writes a copy of the uploaded file to the default storage backend.
        The path format is:

        [term_id]/[section_id]/[uwnetid]/[timestamp]/[original_file_name]

        Ex: 2013-spring/CHEM-101-A/javerage/20131018T083055/grades.csv
        """
        self.filepath = os.path.join(
            section.term.canvas_sis_id(),
            "-".join([section.curriculum_abbr.upper().replace(" ", "_"),
                      section.course_number,
                      section.section_id.upper()]),
            instructor.uwnetid,
            current_datetime().strftime("%Y%m%dT%H%M%S"),
            os.path.basename(fileobj.name).replace("/", "-"))

        fileobj.seek(0, 0)
        decoded_file = self.decode_file(fileobj.read()).splitlines()

        with default_storage.open(self.filepath, mode="w") as f:
            for line in decoded_file:
                f.write(line + "\n")
