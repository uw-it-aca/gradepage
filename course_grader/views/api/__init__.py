from django.conf import settings
from userservice.user import UserService
from course_grader.views.rest_dispatch import RESTDispatch
from course_grader.models import Grade
from course_grader.exceptions import OverrideNotPermitted
import logging


logger = logging.getLogger(__name__)

# Assign numeric strings, for mixed sorting with 4.0 scale grades
grade_order = {"": "9.9", "I": "9.8", "W": "9.7", "HW": "9.5",
               "HP": "7.3", "H": "7.2", "P": "7.1", "F": "7.0",
               "CR": "6.1", "NC": "6.0", "N": "5"}


class GradeFormHandler(RESTDispatch):
    def valid_user_override(self):
        if (not getattr(settings, "ALLOW_GRADE_SUBMISSION_OVERRIDE", False) and
                UserService().get_override_user() is not None):
            raise OverrideNotPermitted()

    def save_grade(self, section_id, data):
        try:
            student_id = data["student_id"]
            (student_reg_id, duplicate_code) = student_id.split("-", 1)
        except ValueError:
            student_reg_id = student_id
            duplicate_code = ""

        try:
            grade = Grade.objects.get(section_id=section_id,
                                      student_reg_id=student_reg_id,
                                      duplicate_code=duplicate_code,
                                      modified_by=self.user.uwregid)
        except Grade.DoesNotExist:
            grade = Grade(section_id=section_id,
                          student_reg_id=student_reg_id,
                          duplicate_code=duplicate_code,
                          modified_by=self.user.uwregid)

        action = "saved"
        if "grade" in data:
            grade.grade = data["grade"]
        if "is_incomplete" in data:
            grade.is_incomplete = data["is_incomplete"]
        if "is_writing" in data:
            grade.is_writing = data["is_writing"]
        if "no_grade_now" in data:
            grade.no_grade_now = data["no_grade_now"]
        if "import_source" in data:
            grade.import_source = data["import_source"]
        if "import_grade" in data:
            grade.import_grade = data["import_grade"]
            action = "imported"
        if "comment" in data:
            grade.comment = data["comment"]
        grade.save()

        logged_grade = "%s" % ("X" if grade.no_grade_now else grade.grade)
        if not len(logged_grade):
            logged_grade = "None"
        if grade.is_incomplete:
            logged_grade = "I," + logged_grade
        if grade.is_writing:
            logged_grade += ",W"

        logger.info("Grade %s, Student: %s, Section: %s, Grade: %s" % (
            action, student_id, section_id, logged_grade))

        return grade


def sorted_students(students):
    return sorted(students, key=lambda s: (
        s.student_surname.upper(), s.student_first_name.upper(),
        s.section_id))


def sorted_grades(grades):
    return sorted(grades, key=lambda s: grade_order.get(s, s),
                  reverse=True)


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


def graderoster_status_params(graderoster, secondary_section_id=None):
    total_count = 0
    submitted_count = 0
    for item in graderoster.items:
        if (secondary_section_id is not None and
                secondary_section_id != item.section_id):
            continue

        if item.is_auditor or item.date_withdrawn:
            continue

        total_count += 1
        if item_is_submitted(item):
            submitted_count += 1

    data = {
        "submitted_count": submitted_count,
        "unsubmitted_count": total_count - submitted_count
    }

    section = graderoster.section
    if hasattr(graderoster, "submissions"):
        submission = graderoster.submissions.get(secondary_section_id, None)
        if submission is None:
            submission = graderoster.submissions.get(section.section_id, None)

        if submission is not None:
            submitted_date = submission["submitted_date"]
            submitted_by = submission["submitted_by"]
            accepted_date = submission["accepted_date"]
            grade_import = submission["grade_import"]
            data["submitted_date"] = submitted_date.isoformat()
            data["accepted_date"] = accepted_date.isoformat() if (
                accepted_date is not None) else None
            data["submitted_by"] = display_person_name(submitted_by)
            data["grade_import"] = grade_import.json_data() if (
                grade_import is not None) else None

    if (section.is_grading_period_open() and data["unsubmitted_count"]):
        data["deadline_warning"] = submission_deadline_warning(section.term)

    return data
