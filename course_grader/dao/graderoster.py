# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from uw_sws_graderoster import get_graderoster, DataFailureException
from uw_sws_graderoster.models import GradeRoster
from course_grader.dao.person import person_from_regid
from course_grader.dao.section import get_section_by_url, is_grader_for_section
from course_grader.dao.term import (
    is_graderoster_available_for_term, is_grading_period_past)
from course_grader.exceptions import (
    GradingNotPermitted, ReceiptNotFound, GradingPeriodNotOpen)
from course_grader.models import SubmittedGradeRoster, GradeImport
from lxml import etree
from logging import getLogger
import re

logger = getLogger(__name__)


def graderoster_for_section(section, instructor, requestor,
                            submitted_graderosters_only=False):
    live_graderoster = None
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

    # If submitted_graderosters_only is False and a graderoster is available
    # for this term, start with a "live" graderoster
    if (not submitted_graderosters_only and
            is_graderoster_available_for_term(section)):
        live_graderoster = get_graderoster(section, instructor, requestor)
        live_graderoster.secondary_section = secondary_section
        live_graderoster.submissions = []

    # Look for submission receipts in the SubmittedGradeRoster table
    people = {instructor.uwregid: instructor}
    submissions = []
    latest_submission = None
    for model in SubmittedGradeRoster.objects.get_by_section(
            section, instructor, secondary_section=secondary_section):

        if latest_submission is None:
            latest_submission = model

        instructor_id = model.instructor_id
        if instructor_id not in people:
            people[instructor_id] = person_from_regid(instructor_id)
        if model.submitted_by not in people:
            people[model.submitted_by] = person_from_regid(model.submitted_by)

        # If submitted_graderosters_only is False and this graderoster has
        # been submitted, try to find a grade import
        grade_imp = None
        if (not submitted_graderosters_only and
                model.submitted_date is not None):

            imp_section_id = "-".join([
                re.sub(r"[,/]", "-", model.section_id),
                model.instructor_id])

            imp_secondary_section_id = None
            if model.secondary_section_id is not None:
                imp_secondary_section_id = "-".join([
                    re.sub(r"[,/]", "-", model.secondary_section_id),
                    model.instructor_id])

            grade_imp = GradeImport.objects.get_last_import_by_section_id(
                imp_section_id, imp_secondary_section_id)
            if grade_imp:
                logger.info(f"GradeImport FOUND, section_id: "
                            f"{grade_imp.section_id}")

        # Extend the basic model data with person and grade import objects
        submission = model.json_data()
        submission["submission_id"] = model.submission_id()
        submission["grade_import"] = grade_imp
        submission["submitted_by"] = people[model.submitted_by]

        if secondary_section is not None:
            submission["secondary_section"] = secondary_section

        submissions.append(submission)

    if live_graderoster is None and latest_submission is not None:
        try:
            root = etree.fromstring(latest_submission.document.strip())

            live_graderoster = GradeRoster.from_xhtml(
                root,
                section=section,
                instructor=people[latest_submission.submitted_by])
            live_graderoster.submissions = []

        except etree.XMLSyntaxError as ex:
            url = GradeRoster(
                    section=section,
                    instructor=people[latest_submission.submitted_by]
                ).graderoster_label()
            raise DataFailureException(url, latest_submission.status_code, ex)

    if live_graderoster is None:
        if is_grading_period_past(section.term):
            raise ReceiptNotFound()
        else:
            if submitted_graderosters_only:
                raise ReceiptNotFound()
            else:
                raise GradingPeriodNotOpen()

    # Merge any remaining receipts together, if they have a submission_id
    for submission in submissions:
        live_graderoster.submissions.append(submission)

    return live_graderoster
