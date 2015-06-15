from course_grader.models import GradeImport, ImportConversion
from course_grader.dao.person import person_from_user
from course_grader.dao.term import all_viewable_terms
from course_grader.dao.section import section_from_param, is_grader_for_section
from course_grader.dao.graderoster import graderoster_for_section
from course_grader.dao.catalyst import valid_gradebook_id
from course_grader.views.api import GradeFormHandler
from course_grader.views import clean_section_id, section_url_token
from course_grader.views import display_section_name
from course_grader.exceptions import *
import json
import logging
import re


logger = logging.getLogger(__name__)


class ImportGrades(GradeFormHandler):
    def run(self, *args, **kwargs):
        request = args[0]
        try:
            self.user = person_from_user()

            section_id = kwargs.get("section_id")
            (section, instructor) = section_from_param(section_id)
            self.section = section
            self.instructor = instructor

            if section.term not in all_viewable_terms():
                raise InvalidTerm()

            if not is_grader_for_section(section, instructor):
                raise GradingNotPermitted(section.section_label(),
                                          instructor.uwnetid)

            if (self.user != instructor and
                    not is_grader_for_section(section, self.user)):
                raise GradingNotPermitted(section.section_label(),
                                          self.user.uwnetid)

            if section.is_primary_section and section.allows_secondary_grading:
                raise SecondaryGradingEnabled()

            if "PUT" == request.method:
                self.valid_user_override()

            self.graderoster = graderoster_for_section(section, instructor)

        except GradingNotPermitted as ex:
            logger.info("Grading for %s not permitted for %s" % (
                ex.section, ex.person))
            return self.error_response(403, "%s" % ex)
        except (SecondaryGradingEnabled, GradingPeriodNotOpen,
                InvalidTerm, InvalidUser, OverrideNotPermitted) as ex:
            return self.error_response(403, "%s" % ex)
        except InvalidSection as ex:
            return self.error_response(404, "%s" % ex)
        except Exception as ex:
            logger.exception(ex)
            if hasattr(ex, "status"):
                status = 404 if (ex.status == 404) else 500
            else:
                status = 500
            err = ex.msg if hasattr(ex, "msg") else ex
            return self.error_response(status, "%s" % err)

        return self.run_http_method(*args, **kwargs)

    def GET(self, request, **kwargs):
        section_id = kwargs.get("section_id")
        import_id = kwargs.get("import_id")

        try:
            grade_import = GradeImport.objects.get(pk=import_id)
        except GradeImport.DoesNotExist:
            return self.error_response(400, "Invalid import")

        return self.response_content(grade_import)

    def PUT(self, request, **kwargs):
        section_id = kwargs.get("section_id")
        import_id = kwargs.get("import_id")

        try:
            grade_import = GradeImport.objects.get(pk=import_id)
            put_data = json.loads(request.body)

        except GradeImport.DoesNotExist:
            return self.error_response(404, "Import not found")
        except Exception as ex:
            return self.error_response(400, "Invalid import")

        conv_data = put_data.get("conversion_scale", None)
        if conv_data is not None:
            try:
                calculator_values = conv_data.get("calculator_values")
                import_conversion = ImportConversion(
                    scale=conv_data.get("scale"),
                    grade_scale=json.dumps(conv_data.get("grade_scale")),
                    calculator_values=json.dumps(calculator_values),
                    lowest_valid_grade=conv_data.get("lowest_valid_grade")
                )
                import_conversion.save()
                grade_import.import_conversion = import_conversion
                grade_import.save()
            except Exception as ex:
                logger.exception(ex)

        import_data = grade_import.json_data()
        converted_grades = put_data.get("converted_grades", {})
        secondary_section = getattr(self.graderoster, "secondary_section",
                                    None)
        for item in self.graderoster.items:
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                continue

            if (item.date_graded is not None or item.is_auditor or
                    item.date_withdrawn is not None):
                continue

            # Find the grade data for each graderoster item
            grade = next((g for g in import_data.get("imported_grades") if (
                g["student_reg_id"] == item.student_uwregid)), None)

            if grade is not None:
                grade_data = {
                    "student_id": item.student_label(separator="-"),
                    "import_source": grade_import.source,
                    "import_grade": grade["imported_grade"],
                    "comment": grade["comment"],
                    "grade": converted_grades.get(grade["student_reg_id"],
                                                  grade["imported_grade"]),
                    "no_grade_now": False,
                }
                self.save_grade(section_id, grade_data)

        return self.response_content(grade_import)

    def POST(self, request, **kwargs):
        try:
            data = json.loads(request.body)
            source = data.get("source", None)
            source_id = data.get("source_id", None)
            source_id = source_id if valid_gradebook_id(source_id) else None
        except Exception as ex:
            logger.exception(ex)
            return self.error_response(400, "Invalid import")

        grade_import = GradeImport(
            section_id=section_url_token(self.section, self.instructor),
            term_id=self.section.term.term_label(),
            imported_by=self.user.uwregid,
            source=source,
            source_id=source_id)

        try:
            grade_import.grades_for_section(self.section, self.instructor)
        except Exception as ex:
            logger.exception(ex)
            return self.error_response(500, "%s" % ex)

        return self.response_content(grade_import)

    def response_content(self, grade_import):
        return_data = grade_import.json_data()
        return_data["section_name"] = display_section_name(self.section)

        # Create a new list of imported grades, including only students who are
        # actually on the graderoster
        imported_grades = return_data.pop("imported_grades", [])
        return_data["students"] = []

        secondary_section = getattr(self.graderoster, "secondary_section",
                                    None)
        for item in self.sorted_students():
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                # Filtering by secondary section
                continue

            # Find the grade data for each graderoster item
            grade = next((g for g in imported_grades if (
                g["student_reg_id"] == item.student_uwregid)), None)

            if grade is not None:
                item_id = "-".join([grade_import.section_id,
                                    item.student_label(separator="-")])
                grade["item_id"] = clean_section_id(item_id)
                grade["section_id"] = self.section.section_id
                grade["student_firstname"] = item.student_first_name
                grade["student_lastname"] = item.student_surname
                grade["student_number"] = item.student_number
                grade["is_auditor"] = item.is_auditor
                grade["is_withdrawn"] = item.date_withdrawn is not None
                return_data["students"].append(grade)

        return self.json_response({"grade_import": return_data})
