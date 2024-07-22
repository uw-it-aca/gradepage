# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.urls import reverse
from course_grader.dao import display_datetime
from course_grader.dao.person import person_display_name
from course_grader.dao.section import section_url_token, section_display_name
from course_grader.dao.term import (
    is_grading_period_open, is_grading_period_past)
import re


def clean_section_id(section_id):
    """ Returns a section_id suitable for use in html ids and jquery selectors.
    """
    return re.sub(r"[\s&]", "_", section_id)


def url_for_term(term):
    return f"/term/{term.year}-{term.quarter}"


def url_for_section(section_id):
    return reverse("section", kwargs={"section_id": section_id})


def url_for_graderoster(section_id):
    return reverse("graderoster-edit", kwargs={"section_id": section_id})


def url_for_grading_status(section_id):
    return reverse("grading-status", kwargs={"section_id": section_id})


def url_for_import(section_id):
    return reverse("grade-import", kwargs={"section_id": section_id})


def url_for_upload(section_id, import_id=None):
    kwargs = {"section_id": section_id}
    if import_id:
        kwargs["import_id"] = import_id
    return reverse("grade-import-file", kwargs=kwargs)


def url_for_export(section_id):
    return reverse("graderoster-export", kwargs={"section_id": section_id})


def section_status_params(section, instructor):
    section_id = section_url_token(section, instructor)
    grading_period_open = is_grading_period_open(section)
    grading_deadline = None
    if section.term.grade_submission_deadline is not None:
        grading_deadline = section.term.grade_submission_deadline.isoformat()

    if section.is_independent_study:
        display_name = section_display_name(section, instructor)
    else:
        display_name = section_display_name(section)

    data = {
        "section_id": clean_section_id(section_id),
        "display_name": display_name,
        "section_url": None,
        "status_url": None,
        "grading_status": None,
        "grading_period_open": grading_period_open,
        "grade_submission_deadline": grading_deadline,
    }

    if (grading_period_open or is_grading_period_past(section.term)):
        if (section.is_primary_section and section.allows_secondary_grading):
            data["grading_status"] = (
                "Secondary grading is enabled for this course.")
        else:
            data["section_url"] = url_for_section(section_id)
            data["status_url"] = url_for_grading_status(section_id)
    elif section.is_full_summer_term():
        data["grading_status"] = (
            "Summer full-term grade submission opens on {}.".format(
                display_datetime(section.term.grading_period_open)))
    elif section.is_summer_b_term():
        data["grading_status"] = (
            "Summer B-term grade submission opens on {}.".format(
                display_datetime(section.term.grading_period_open)))

    return data
