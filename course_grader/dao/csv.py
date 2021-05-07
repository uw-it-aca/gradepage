# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from course_grader.dao.person import person_from_netid
from restclients_core.exceptions import InvalidNetID, DataFailureException
from logging import getLogger
from io import StringIO
import csv

logger = getLogger(__name__)


def grades_for_section(section, instructor, csv_data):
    """
    Convert CSV document into normalized JSON

    CSV Format:  uwnetid, grade, incomplete, default_grade, writing_credit
    """
    grade_data = []
    reader = csv.reader(StringIO(csv_data))
    for row in reader:
        netid = row.get("uwnetid")
        try:
            person = person_from_netid(netid)
        except (InvalidNetID, DataFailureException) as ex:
            log.info("SKIP import user {}: {}".format(netid, ex))
            continue

        student_data = {
            "student_reg_id": person.uwregid,
            "imported_grade": "",
        }
        grade_data.append(student_data)

    return {"grades": grade_data}
