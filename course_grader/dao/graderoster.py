"""
This module encapsulates the access of sws graderoster data
"""

from restclients.sws.graderoster import get_graderoster, graderoster_from_xhtml
from restclients.sws.section import get_section_by_url
from restclients.util.retry import retry
from course_grader.dao.person import person_from_regid
from course_grader.dao.section import is_grader_for_section
from course_grader.exceptions import GradingNotPermitted, ReceiptNotFound
from course_grader.exceptions import GradingPeriodNotOpen
from course_grader.models import SubmittedGradeRoster, GradeImport
from urllib3.exceptions import SSLError
import logging
import re


logger = logging.getLogger(__name__)


def item_is_submitted(item):
    if (item.is_auditor or item.date_withdrawn is not None):
        return False

    # Old receipts do not include date_graded, so also check for the
    # existence of a grade
    if (item.date_graded is not None or
            item.grade is not None or item.no_grade_now):
        return True
    else:
        return False


def graderoster_for_section(section, instructor, requestor,
                            submitted_graderosters_only=False):
    ret_graderoster = None
    secondary_section = None

    if (not section.is_primary_section and
            not section.allows_secondary_grading):
        # Section is a secondary section, but secondary grading is not
        # enabled. Try to use the primary section ID, if the user is
        # authorized
        primary_section_href = section.primary_section_href
        secondary_section = section
        section = get_section_by_url(primary_section_href)

        if (not section.is_instructor(instructor) and
                section.is_instructor(requestor)):
            instructor = requestor

        if not is_grader_for_section(section, requestor):
            raise GradingNotPermitted(section.section_label(),
                                      requestor.uwregid)

    @retry(SSLError, tries=3, delay=1, logger=logger)
    def _get_graderoster(section, instructor, requestor):
        return get_graderoster(section, instructor, requestor)

    # If submitted_graderosters_only is False and grading period is open,
    # start with a "live" graderoster
    if (not submitted_graderosters_only and section.is_grading_period_open()):
        ret_graderoster = _get_graderoster(section, instructor, requestor)
        ret_graderoster.secondary_section = secondary_section
        ret_graderoster.submissions = {}

    # Look for submission receipts in the SubmittedGradeRoster table
    people = {instructor.uwregid: instructor}
    submitted_graderosters = []
    for model in SubmittedGradeRoster.objects.get_by_section(
            section, instructor, secondary_section):
        instructor_id = model.instructor_id
        if instructor_id not in people:
            people[instructor_id] = person_from_regid(instructor_id)
        if model.submitted_by not in people:
            people[model.submitted_by] = person_from_regid(model.submitted_by)

        graderoster = graderoster_from_xhtml(model.document, section,
                                             people[instructor_id])

        grade_imp = None
        # If submitted_graderosters_only is False and this graderoster has been
        # submitted, try to find a grade import
        if (not submitted_graderosters_only and
                model.submitted_date is not None):
            imp_section_id = "-".join([re.sub(r"[,/]", "-", model.section_id),
                                       model.instructor_id])
            try:
                grade_imp = GradeImport.objects.get_last_import_by_section_id(
                    imp_section_id)
            except GradeImport.DoesNotExist:
                pass

        graderoster.submission_id = model.submission_id()
        graderoster.submissions = {
            graderoster.submission_id: {
                "submitted_date": model.submitted_date,
                "submitted_by": people[model.submitted_by],
                "accepted_date": model.accepted_date,
                "status_code": model.status_code,
                "grade_import": grade_imp,
            }
        }

        if secondary_section is not None:
            graderoster.secondary_section = secondary_section

        submitted_graderosters.append(graderoster)

    if ret_graderoster is None:
        try:
            ret_graderoster = submitted_graderosters.pop(0)
        except IndexError:
            if section.term.is_grading_period_past():
                raise ReceiptNotFound()
            else:
                if submitted_graderosters_only:
                    raise ReceiptNotFound()
                else:
                    raise GradingPeriodNotOpen()

    # Merge any remaining receipts together, if they have a submission_id
    for graderoster in submitted_graderosters:
        if not hasattr(graderoster, "submission_id"):
            continue

        ret_graderoster.submissions.update(graderoster.submissions)

        for item in graderoster.items:
            if graderoster.submission_id == item.section_id:
                try:
                    idx = ret_graderoster.items.index(item)
                    ret_graderoster.items[idx] = item
                except Exception as ex:
                    pass

    return ret_graderoster
