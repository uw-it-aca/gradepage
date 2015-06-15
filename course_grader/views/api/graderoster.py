from django.core.context_processors import csrf
from course_grader.models import SubmittedGradeRoster, Grade, GradeImport
from course_grader.dao.graderoster import graderoster_for_section
from course_grader.dao.section import section_from_param, is_grader_for_section
from course_grader.dao.person import person_from_user
from course_grader.dao.term import all_viewable_terms
from course_grader.views import clean_section_id
from course_grader.views import grade_submission_deadline_params
from course_grader.views import display_section_name, display_person_name
from course_grader.views.api import GradeFormHandler
from course_grader.exceptions import *
from datetime import datetime
import json
import logging
import re


logger = logging.getLogger(__name__)


class GradeRoster(GradeFormHandler):
    def run(self, *args, **kwargs):
        request = args[0]

        try:
            self.user = person_from_user()

            (section, instructor) = section_from_param(kwargs.get("section_id"))
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

            if (re.match(r"(PATCH|PUT|POST)", request.method)):
                self.valid_user_override()

            if (re.match(r"(GET|PUT|POST)", request.method)):
                self.graderoster = graderoster_for_section(section, instructor)

        except GradingNotPermitted as ex:
            logger.info("Grading for %s not permitted for %s" % (
                ex.section, ex.person))
            return self.error_response(403, "%s" % ex)
        except (SecondaryGradingEnabled, GradingPeriodNotOpen,
                InvalidTerm, InvalidUser, OverrideNotPermitted) as ex:
            return self.error_response(403, "%s" % ex)
        except (InvalidSection, ReceiptNotFound) as ex:
            return self.error_response(404, "%s" % ex)
        except Exception as ex:
            logger.exception(ex)
            err = ex.msg if hasattr(ex, "msg") else ex
            return self.error_response(500, "%s" % err)

        return self.run_http_method(*args, **kwargs)

    def GET(self, request, **kwargs):
        section_id = kwargs.get("section_id")
        is_status = True if request.GET.get("status", "") else False

        if is_status:
            content = self.status_response_content(**kwargs)

        else:
            if self.section.is_grading_period_open():
                kwargs["saved_grades"] = self.saved_grades(section_id)

            content = self.response_content(**kwargs)

        return self.json_response(content)

    def PATCH(self, request, **kwargs):
        section_id = kwargs.get("section_id")

        try:
            grade_data = json.loads(request.body)
            grade = self.save_grade(section_id, grade_data)
        except Exception as ex:
            logger.exception(ex)
            return self.error_response(500)

        # PATCH does not return a full graderoster resource
        return self.json_response(grade.json_data())

    def PUT(self, request, **kwargs):
        section_id = kwargs.get("section_id")
        saved_grades = {}
        try:
            for data in json.loads(request.body):
                grade = self.save_grade(section_id, data)
                saved_grades[data["student_id"]] = grade

        except Exception as ex:
            logger.exception(ex)
            return self.error_response(500)

        secondary_section = getattr(self.graderoster, "secondary_section", None)
        status = 200
        for item in self.graderoster.items:
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                continue

            if (self.is_submitted(item) or item.is_auditor or
                    item.date_withdrawn is not None):
                continue

            student_id = item.student_label(separator="-")
            if not self.validate_grade(item, saved_grades.get(student_id, None)):
                status = 409

        kwargs["saved_grades"] = saved_grades
        content = self.response_content(**kwargs)
        return self.json_response(content, status=status)

    def POST(self, request, **kwargs):
        section_id = kwargs.get("section_id")
        saved_grades = self.saved_grades(section_id)
        secondary_section = getattr(self.graderoster, "secondary_section", None)

        status = 200
        unsubmitted_count = 0
        for item in self.graderoster.items:
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                continue

            if (self.is_submitted(item) or item.is_auditor or
                    item.date_withdrawn is not None):
                continue

            unsubmitted_count += 1
            student_id = item.student_label(separator="-")
            saved_grade = saved_grades.get(student_id, None)
            if self.validate_grade(item, saved_grade):
                item.no_grade_now = saved_grade.no_grade_now
                item.grade = "" if item.no_grade_now is True else saved_grade.grade
                item.has_incomplete = saved_grade.is_incomplete
                item.has_writing_credit = saved_grade.is_writing
                item.grade_submitter_person = self.user
            else:
                status = 409

        if status == 200 and unsubmitted_count:
            section = self.graderoster.section
            model = SubmittedGradeRoster(
                section_id=section.section_label(),
                instructor_id=self.graderoster.instructor.uwregid,
                term_id=section.term.term_label(),
                submitted_by=self.user.uwregid,
                document=self.graderoster.xhtml())

            if secondary_section is not None:
                model.secondary_section_id = secondary_section.section_label()

            model.save()
            model.submit()

            self.graderoster = graderoster_for_section(self.section,
                                                       self.instructor)

        kwargs["saved_grades"] = saved_grades

        content = self.response_content(**kwargs)
        content["graderoster"]["is_submission_confirmation"] = True
        return self.json_response(content, status=status)

    def validate_grade(self, graderoster_item, saved_grade):
        if saved_grade is None:
            return False

        if (saved_grade.is_incomplete and (saved_grade.no_grade_now or
                saved_grade.grade == "N" or saved_grade.grade == "CR")):
            return False

        if saved_grade.no_grade_now:
            return True

        for choice in graderoster_item.grade_choices:
            if (choice is not None and choice != "" and
                    choice == saved_grade.grade):
                return True

        return False

    def saved_grades(self, section_id):
        grades = Grade.objects.filter(section_id=section_id,
                                      modified_by=self.user.uwregid)

        grade_lookup = {}
        for grade in grades:
            student_id = grade.student_label()
            grade_lookup[student_id] = grade

        return grade_lookup

    def response_content(self, **kwargs):
        section_id = kwargs.get("section_id")
        saved_grades = kwargs.get("saved_grades", {})
        grading_period_open = self.section.is_grading_period_open()
        allows_writing_credit = self.graderoster.allows_writing_credit
        import_sources = dict(GradeImport.SOURCE_CHOICES)

        data = {"section_id": section_id,
                "section_name": display_section_name(self.section),
                "students": [],
                "import_choices": [],
                "grade_choices": [],
                "submissions": [],
                "has_duplicate_codes": False,
                "has_successful_submissions": False,
                "has_failed_submissions": False,
                "failed_submission_count": 0,
                "has_inprogress_submissions": False}

        secondary_section = getattr(self.graderoster, "secondary_section", None)

        submissions = getattr(self.graderoster, "submissions", {})
        for key in sorted(submissions.iterkeys()):
            sid = key if key != self.graderoster.section.section_id else None
            submission_status = self.status_by_section(sid)
            submission_status["section_id"] = sid
            if submission_status["accepted_date"] is None:
                data["has_inprogress_submissions"] = True
            data["submissions"].append(submission_status)

        if grading_period_open:
            for choice in GradeImport.SOURCE_CHOICES:
                data["import_choices"].append({"value": choice[0],
                                               "label": choice[1]})

        grade_lookup = {}
        for item in self.sorted_students():
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                # Filtering by secondary section
                continue

            student_id = item.student_label(separator="-")
            item_id = "-".join([section_id, student_id])
            is_submitted = self.is_submitted(item)
            grade_choices_index = None
            grade_url = None
            grade = "" if item.no_grade_now is True else item.grade
            no_grade_now = item.no_grade_now
            has_incomplete = item.has_incomplete
            has_writing_credit = item.has_writing_credit
            date_graded = None
            withdrawn_week = None
            import_source = None
            import_grade = None

            if item.duplicate_code is not None:
                data["has_duplicate_codes"] = True

            if is_submitted:
                if has_incomplete and grade.lower() == "i":
                    grade = ""

                if item.date_graded is not None:
                    date = datetime.strptime(item.date_graded, "%Y-%m-%d")
                    date_graded = date.strftime("%m/%d/%Y")

                if item.status_code is not None:
                    if item.status_code == "200":
                        data["has_successful_submissions"] = True
                    else:
                        data["has_failed_submissions"] = True
                        data["failed_submission_count"] += 1

            elif item.date_withdrawn:
                if grade is not None:
                    m = re.match(r"^W(?P<week>[\d])$", grade)
                    if m is not None and m.group("week"):
                        withdrawn_week = m.group("week")
                    grade = ""

            elif grading_period_open and not item.is_auditor:
                grade_url = "/api/v1/graderoster/%s" % section_id

                # Use an existing grade_choices list, or add this one
                grade_choices_csv = ",".join(item.grade_choices)
                try:
                    grade_choices_index = grade_lookup[grade_choices_csv]
                except KeyError:
                    data["grade_choices"].append(
                        self.sorted_grades(item.grade_choices))
                    grade_choices_index = len(data["grade_choices"]) - 1
                    grade_lookup[grade_choices_csv] = grade_choices_index

                # Use saved grade data if it exists
                try:
                    saved_grade = saved_grades[student_id]
                    grade = "" if saved_grade.no_grade_now is True else saved_grade.grade
                    no_grade_now = saved_grade.no_grade_now
                    has_incomplete = saved_grade.is_incomplete
                    has_writing_credit = saved_grade.is_writing
                    if saved_grade.import_grade is not None:
                        import_source = import_sources[saved_grade.import_source]
                        import_grade = saved_grade.import_grade
                except KeyError:
                    pass

            student_data = {
                "item_id": clean_section_id(item_id),
                "student_id": student_id,
                "student_firstname": item.student_first_name,
                "student_lastname": item.student_surname,
                "student_number": item.student_number,
                "student_credits": item.student_credits,
                "section_id": item.section_id,
                "is_auditor": item.is_auditor,
                "is_withdrawn": item.date_withdrawn is not None,
                "withdrawn_week": withdrawn_week,
                "date_graded": date_graded,
                "allows_incomplete": item.allows_incomplete and not is_submitted,
                "has_incomplete": has_incomplete,
                "is_writing_section": not allows_writing_credit,
                "allows_writing_credit": allows_writing_credit and not is_submitted,
                "has_writing_credit": has_writing_credit,
                "no_grade_now": no_grade_now,
                "duplicate_code": item.duplicate_code,
                "grade": grade,
                "grade_choices_index": grade_choices_index,
                "grade_url": grade_url,
                "grade_status": item.status_message,
                "import_source": import_source,
                "import_grade": import_grade,
            }
            data["students"].append(student_data)

        return {"graderoster": data}

    def status_response_content(self, **kwargs):
        section_id = kwargs.get("section_id")
        section = self.section

        data = self.status_by_section()
        data["section_id"] = clean_section_id(section_id)

        # Handle secondary sections in this request if appropriate
        if section.is_primary_section and not section.allows_secondary_grading:
            data["secondary_sections"] = []
            for linked_url in section.linked_section_urls:
                secondary_section_id = linked_url.split("/")[-1].split(".")[0]
                secondary_data = self.status_by_section(secondary_section_id)
                secondary_data["section_id"] = clean_section_id(
                    "-".join([str(section.term.year), section.term.quarter,
                              section.curriculum_abbr, section.course_number,
                              secondary_section_id, self.instructor.uwregid]))
                data["secondary_sections"].append(secondary_data)

        return {"graderoster_status": data}

    def status_by_section(self, secondary_section_id=None):
        data = {}
        total_count = 0
        submitted_count = 0
        for item in self.graderoster.items:
            if (secondary_section_id is not None and
                    secondary_section_id != item.section_id):
                continue

            if item.is_auditor or item.date_withdrawn:
                continue

            total_count += 1
            if self.is_submitted(item):
                submitted_count += 1

        unsubmitted_count = total_count - submitted_count
        is_grading_period_open = self.graderoster.section.is_grading_period_open()
        if is_grading_period_open and unsubmitted_count:
            deadline_params = grade_submission_deadline_params(self.section.term)
            data["deadline_warning"] = deadline_params["deadline_warning"]

        if hasattr(self.graderoster, "submissions"):
            submission = self.graderoster.submissions.get(secondary_section_id, None)
            if submission is None:
                submission = self.graderoster.submissions.get(
                    self.graderoster.section.section_id, None)

            if submission is not None:
                submitted_date = submission["submitted_date"]
                submitted_by = submission["submitted_by"]
                accepted_date = submission["accepted_date"]
                data["submitted_date"] = submitted_date.isoformat()
                data["accepted_date"] = accepted_date.isoformat() if (
                    accepted_date is not None) else None
                data["submitted_by"] = display_person_name(submitted_by)

        data["submitted_count"] = submitted_count
        data["unsubmitted_count"] = unsubmitted_count
        data["grading_period_open"] = is_grading_period_open

        return data

    def is_submitted(self, item):
        if (item.is_auditor or item.date_withdrawn is not None):
            return False

        # Old receipts do not include date_graded, so also check for the
        # existence of a grade
        if (item.date_graded is not None or
                item.grade is not None or item.no_grade_now):
            return True
        else:
            return False
