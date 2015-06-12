"""
This module encapsulates the interactions with canvas gradebook
"""

from restclients.canvas.enrollments import Enrollments
from restclients.canvas.assignments import Assignments
from course_grader.dao.section import section_from_url


def grades_for_section(section, instructor):
    canvas = Enrollments()

    # Use the canvas section resource, since individual sections
    # may be cross-listed to other courses
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

    courses = {}
    grade_data = {"grades": [], "muted_assignments": []}
    for enrollment in enrollments:
        if enrollment.role == enrollment.STUDENT:
            grade_data["grades"].append(enrollment.json_data())
            courses[enrollment.course_id] = True

    canvas = Assignments()
    for course_id in courses.keys():
        for assignment in canvas.get_assignments(course_id):
            if assignment.muted:
                assignment_data = {"course_id": course_id,
                                   "assignment_id": assignment.assignment_id,
                                   "name": assignment.name}
                grade_data["muted_assignments"].append(assignment_data)

    return grade_data
