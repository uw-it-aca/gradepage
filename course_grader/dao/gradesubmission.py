# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_sws_graderoster import update_graderoster
from uw_sws_graderoster.models import GradeRoster
from course_grader.dao.section import section_from_label
from course_grader.dao.person import person_from_regid
from lxml import etree
from logging import getLogger

logger = getLogger(__name__)


def submit_grades(model):
    graderoster = GradeRoster.from_xhtml(
        etree.fromstring(model.document.strip()),
        section=section_from_label(model.section_id),
        instructor=person_from_regid(model.instructor_id))

    logged_section_id = model.section_id
    if model.secondary_section_id is not None:
        logged_section_id = model.secondary_section_id
        graderoster.secondary_section = section_from_label(
            model.secondary_section_id)

    requestor = person_from_regid(model.submitted_by)
    ret_graderoster = update_graderoster(graderoster, requestor)

    # The returned graderoster from PUT omits items for which a grade was
    # not actually submitted, and it lacks secondary section info for each
    # item. To create a saved graderoster receipt, merge the returned
    # graderoster into the submitted graderoster, to capture both the
    # submitted grade and the returned status code/message for each item.
    for item in ret_graderoster.items:
        if item.status_code is None:
            continue

        try:
            idx = graderoster.items.index(item)
            graderoster.items[idx].status_code = item.status_code
            graderoster.items[idx].status_message = item.status_message
            graderoster.items[idx].date_graded = item.date_graded
            graderoster.items[idx].grade_document_id = item.grade_document_id
            graderoster.items[idx].grade_submitter_source = (
                item.grade_submitter_source)

            logged_grade = logged_grade(graderoster.items[idx])
            if logged_grade is not None:
                logger.info((
                    "Grade submitted, Student: {student}, Section: "
                    "{section_id}, Grade: {grade}, Code: {status_code}, "
                    "Message: {message}").format(
                        student=graderoster.items[idx].student_label(
                            separator="-"),
                        section_id=logged_section_id,
                        grade=logged_grade,
                        status_code=graderoster.items[idx].status_code,
                        message=graderoster.items[idx].status_message))

        except Exception as ex:
            logger.error("Error logging grade: {}".format(ex))

    return graderoster


def logged_grade(item):
    logged_grade = None
    if not (item.is_auditor or item.date_withdrawn):
        logged_grade = "X" if item.no_grade_now else str(item.grade)
        if item.has_incomplete:
            logged_grade = "I," + logged_grade
        if item.has_writing_credit:
            logged_grade += ",W"

    return logged_grade
