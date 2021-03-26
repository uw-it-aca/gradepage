# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from uw_canvas.courses import Courses
from uw_canvas.enrollments import Enrollments
from uw_canvas.grading_standards import GradingStandards
from course_grader.dao.section import section_from_url
from restclients_core.exceptions import DataFailureException


def grading_scheme_for_course(course_id):
    course = Courses().get_course(course_id)
    if course.grading_standard_id:
        canvas = GradingStandards()
        try:
            grading_standard = canvas.get_grading_standard_for_course(
                course_id, course.grading_standard_id)
        except DataFailureException as ex:
            if ex.status != 404:
                raise

            grading_standard = canvas.find_grading_standard_for_account(
                course.account_id, course.grading_standard_id)

        json_data = grading_standard.json_data()
        json_data["course_id"] = course_id
        json_data["course_name"] = course.name
        return json_data


def grades_for_section(section, instructor):
    grade_data = {"grades": [], "course_grading_schemes": []}
    course_ids = set()

    # Use the canvas section resource, since individual sections
    # may be cross-listed to other courses
    canvas = Enrollments(per_page=getattr(settings, "CANVAS_PER_PAGE", 200))
    if len(section.linked_section_urls):
        enrollments = []
        for url in section.linked_section_urls:
            linked_section = section_from_url(url)
            sis_id = linked_section.canvas_section_sis_id()
            enrollments.extend(
                canvas.get_enrollments_for_section_by_sis_id(sis_id))
    else:
        if section.is_independent_study:
            section.independent_study_instructor_regid = instructor.uwregid

        sis_id = section.canvas_section_sis_id()
        enrollments = canvas.get_enrollments_for_section_by_sis_id(sis_id)

    for enrollment in enrollments:
        if enrollment.role == enrollment.STUDENT:
            grade_data["grades"].append(enrollment.json_data())
            course_ids.add(enrollment.course_id)

    for course_id in course_ids:
        grading_scheme = grading_scheme_for_course(course_id)
        if grading_scheme:
            grade_data["course_grading_schemes"].append(grading_scheme)

    return grade_data
