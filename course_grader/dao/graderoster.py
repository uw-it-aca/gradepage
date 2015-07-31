"""
This module encapsulates the access of sws graderoster data
"""

from django.db.models import Q
from restclients.sws.graderoster import get_graderoster, graderoster_from_xhtml
from restclients.sws.section import get_section_by_url
from course_grader.dao.person import person_from_user, person_from_regid
from course_grader.dao.section import is_grader_for_section
from course_grader.exceptions import GradingNotPermitted, ReceiptNotFound
from course_grader.exceptions import GradingPeriodNotOpen
from course_grader.models import SubmittedGradeRoster, GradeImport
import re


def graderoster_for_section(section, instructor):
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
        person = person_from_user()

        if (not section.is_instructor(instructor) and
                section.is_instructor(person)):
            instructor = person

        if not is_grader_for_section(section, person):
            raise GradingNotPermitted(section.section_label(),
                                      person.uwregid)

    # If grading period is open, start with a "live" graderoster
    if section.is_grading_period_open():
        ret_graderoster = get_graderoster(section, instructor)
        ret_graderoster.secondary_section = secondary_section
        ret_graderoster.submissions = {}

    # Look for a submission receipt in the SubmittedGradeRoster table
    kwargs = {"section_id": section.section_label()}
    if secondary_section is not None:
        args = (Q(secondary_section_id=secondary_section.section_label()) |
                Q(secondary_section_id__isnull=True),)
    else:
        args = ()
        if section.is_independent_study:
            kwargs["instructor_id"] = instructor.uwregid

    queryset = SubmittedGradeRoster.objects.filter(
        *args, **kwargs).order_by("secondary_section_id")

    people = {instructor.uwregid: instructor}
    submitted_graderosters = []

    for model in queryset:
        instructor_id = model.instructor_id
        if instructor_id not in people:
            people[instructor_id] = person_from_regid(instructor_id)
        if model.submitted_by not in people:
            people[model.submitted_by] = person_from_regid(model.submitted_by)

        graderoster = graderoster_from_xhtml(model.document, section,
                                             people[instructor_id])

        grade_import = None
        if model.submitted_date is not None:
            imp_section_id = "-".join([re.sub(r"[,/]", "-", model.section_id),
                                       model.instructor_id])
            try:
                grade_import = GradeImport.objects.filter(
                    section_id=imp_section_id,
                    import_conversion__isnull=False,
                    status_code="200").order_by("-imported_date")[0:1].get()
            except GradeImport.DoesNotExist:
                pass

        graderoster.submission_id = model.submission_id()
        graderoster.submissions = {
            graderoster.submission_id: {
                "submitted_date": model.submitted_date,
                "submitted_by": people[model.submitted_by],
                "accepted_date": model.accepted_date,
                "status_code": model.status_code,
                "grade_import": grade_import,
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
