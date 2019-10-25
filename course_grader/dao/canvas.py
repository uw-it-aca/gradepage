"""
This module encapsulates the interactions with Canvas gradebook
"""

from uw_canvas.enrollments import Enrollments
from uw_canvas.assignments import Assignments
from uw_canvas.submissions import Submissions
from course_grader.dao.section import section_from_url

PER_PAGE = 200


def assignment_muted(assignment):
    return (assignment.muted and (
        assignment.published or assignment.has_submissions))


def grades_for_section(section, instructor):
    section_sis_ids = set()

    # Use the canvas section resource, since individual sections
    # may be cross-listed to other courses
    canvas = Enrollments(per_page=PER_PAGE)
    if len(section.linked_section_urls):
        enrollments = []
        for url in section.linked_section_urls:
            linked_section = section_from_url(url)
            sis_id = linked_section.canvas_section_sis_id()
            enrollments.extend(
                canvas.get_enrollments_for_section_by_sis_id(sis_id))
            section_sis_ids.add(sis_id)
    else:
        if section.is_independent_study:
            section.independent_study_instructor_regid = instructor.uwregid

        sis_id = section.canvas_section_sis_id()
        enrollments = canvas.get_enrollments_for_section_by_sis_id(sis_id)
        section_sis_ids.add(sis_id)

    grade_data = {"grades": [], "grade_warnings": []}

    courses = set()
    for enrollment in enrollments:
        if enrollment.role == enrollment.STUDENT:
            grade_data["grades"].append(enrollment.json_data())
            courses.add(enrollment.course_id)

    # For courses using Old Gradebook, 'muted' indicates whether the
    # assignment is muted.
    # For courses using New Gradebook, 'muted' is true if the assignment has
    # any unposted submissions, otherwise false.
    # To see the posted status of submissions, check 'posted_at' on Submission.
    canvas_a = Assignments(per_page=PER_PAGE)
    canvas_s = Submissions(per_page=PER_PAGE)
    for course_id in courses:
        for assignment in canvas_a.get_assignments(course_id):
            if assignment_muted(assignment):
                assignment_data = {"course_id": course_id,
                                   "assignment_id": assignment.assignment_id,
                                   "name": assignment.name,
                                   "muted": True,
                                   "unposted_submission_count": 0}

                for sub in canvas_s.get_submissions_by_course_and_assignment(
                        course_id, assignment.assignment_id):
                    if sub.posted_at is None:
                        assignment_data["unposted_submission_count"] += 1

                if assignment_data["unposted_submission_count"] > 0:
                    assignment_data["muted"] = False

                grade_data["grade_warnings"].append(assignment_data)

    return grade_data
