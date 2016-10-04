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

    def sorted_students(self, students):
        return sorted(students, key=lambda s: (
            s.student_surname.upper(), s.student_first_name.upper(),
            s.section_id))

    def sorted_grades(self, grades):
        return sorted(grades, key=lambda s: grade_order.get(s, s),
                      reverse=True)
