from restclients.sws.graderoster import (
    update_graderoster, graderoster_from_xhtml)
from restclients.util.retry import retry
from course_grader.dao.section import section_from_label
from course_grader.dao.person import person_from_regid
from urllib3.exceptions import SSLError
import logging


logger = logging.getLogger(__name__)


def submit_grades(model):
    @retry(SSLError, tries=3, delay=1, logger=logger)
    def _update_graderoster(graderoster, requestor):
        return update_graderoster(graderoster, requestor)

    graderoster = graderoster_from_xhtml(
        model.document, section_from_label(model.section_id),
        person_from_regid(model.instructor_id))

    logged_section_id = model.section_id
    if model.secondary_section_id is not None:
        logged_section_id = model.secondary_section_id
        graderoster.secondary_section = section_from_label(
            model.secondary_section_id)

    requestor = person_from_regid(model.submitted_by)
    ret_graderoster = _update_graderoster(graderoster, requestor)

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
                logger.info(
                    "Grade submitted, Student: %s, Section: %s, Grade: %s, " +
                    "Code: %s, Message: %s" % (
                        graderoster.items[idx].student_label(separator="-"),
                        logged_section_id, logged_grade,
                        graderoster.items[idx].status_code,
                        graderoster.items[idx].status_message))

        except Exception as ex:
            pass

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
