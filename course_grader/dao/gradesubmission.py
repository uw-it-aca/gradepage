# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from uw_sws_graderoster import update_graderoster
from uw_sws_graderoster.models import GradeRoster
from course_grader.dao.section import section_from_label
from course_grader.dao.person import person_from_regid
from lxml import etree
from logging import getLogger

logger = getLogger(__name__)


def format_logged_grade(item):
    logged_grade = None
    if not (item.is_auditor or item.date_withdrawn):
        logged_grade = "X" if item.no_grade_now else str(item.grade)
        if item.has_incomplete:
            logged_grade = "I," + logged_grade
        if item.has_writing_credit:
            logged_grade += ",W"

    return logged_grade


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
    ret_graderoster__dict = {}
    for item in ret_graderoster.items:
        key = item.student_label(separator="-")
        ret_graderoster_dict[key] = item

    for item in graderoster.items:
        key = item.student_label(separator="-")

        # Capture the submitted grade for logging
        submitted_grade = format_logged_grade(item)

        try:
            ret_item = ret_graderoster_dict[key]
        except KeyError:
            logger.info((
                "Grade submitted, Student: {student}, Section: "
                "{section_id}, Submitted grade: {submitted_grade}, "
                "Returned grade: {returned_grade}, Code: {status_code}, "
                "Message: {message}").format(
                    student=key,
                    section_id=logged_section_id,
                    submitted_grade=submitted_grade,
                    returned_grade=None,
                    status_code=None,
                    message=None))
            continue

        # Update the graderoster with data returned from PUT
        # item.grade = ret_item.grade
        # item.no_grade_now = ret_item.no_grade_now
        # item.has_incomplete = ret_item.has_incomplete
        # item.has_writing_credit = ret_item.has_writing_credit
        item.status_code = ret_item.status_code
        item.status_message = ret_item.status_message
        item.date_graded = ret_item.date_graded
        item.grade_document_id = ret_item.grade_document_id
        item.grade_submitter_source = ret_item.grade_submitter_source

        logger.info((
            "Grade submitted, Student: {student}, Section: "
            "{section_id}, Submitted grade: {submitted_grade}, "
            "Returned grade: {returned_grade}, Code: {status_code}, "
            "Message: {message}").format(
                student=key,
                section_id=logged_section_id,
                submitted_grade=submitted_grade,
                returned_grade=format_logged_grade(ret_item),
                status_code=item.status_code,
                message=item.status_message))

    return graderoster
