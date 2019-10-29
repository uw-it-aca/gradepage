from django.conf import settings
from uw_canvas.courses import Courses
from uw_canvas.enrollments import Enrollments
from uw_canvas.assignments import Assignments
from uw_canvas.grading_standards import GradingStandards
# from uw_canvas.submissions import Submissions
from course_grader.dao.section import section_from_url


def assignment_muted(assignment):
    return (assignment.muted and (
        assignment.published or assignment.has_submissions))


def grading_standard_for_course(course_id):
    course = Courses().get_course(course_id)
    if course.grading_standard_id:
        return GradingStandards().get_grading_standard_for_course(
            course_id, course.grading_standard_id).json_data()


def hidden_grades_for_course(course_id):
    """
    For courses using Old Gradebook, 'muted' indicates whether the
    assignment is muted.
    For courses using New Gradebook, 'muted' is true if the assignment has
    any unposted submissions, otherwise false.
    To see the posted status of submissions, check 'posted_at' on Submission.
    """
    assignments_with_hidden_grades = []
    canvas = Assignments(per_page=getattr(settings, "CANVAS_PER_PAGE", 200))
    # canvas = Submissions(per_page=getattr(settings, "CANVAS_PER_PAGE", 200))
    for assignment in canvas.get_assignments(course_id):
        if assignment_muted(assignment):
            assignment_data = {"course_id": course_id,
                               "assignment_id": assignment.assignment_id,
                               "name": assignment.name,
                               "muted": True,
                               "unposted_submission_count": 0}

            # for sub in canvas_s.get_submissions_by_course_and_assignment(
            #        course_id, assignment.assignment_id):
            #    if sub.posted_at is None:
            #        assignment_data["unposted_submission_count"] += 1

            # if assignment_data["unposted_submission_count"] > 0:
            #    assignment_data["muted"] = False

            assignments_with_hidden_grades.append(assignment_data)

    return assignments_with_hidden_grades


def grades_for_section(section, instructor):
    grade_data = {"grades": [], "warnings": []}
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
        grade_data["warnings"].extend(hidden_grades_for_course(course_id))

    return grade_data
