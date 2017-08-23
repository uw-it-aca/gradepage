from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from course_grader.models import SubmittedGradeRoster, Grade, GradeImport
from course_grader.dao.graderoster import graderoster_for_section
from course_grader.dao.section import (
    section_from_param, is_grader_for_section, section_display_name)
from course_grader.dao.person import person_from_user, person_from_request
from course_grader.dao.term import all_viewable_terms
from course_grader.dao.term import submission_deadline_warning
from course_grader.views import (
    section_status_params, clean_section_id, url_for_section,
    url_for_grading_status)
from course_grader.views.api import (
    GradeFormHandler, graderoster_status_params, item_is_submitted,
    sorted_students, sorted_grades)
from course_grader.exceptions import *
from userservice.user import UserService
from datetime import datetime
import json
import logging
import re


logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class GradeRoster(GradeFormHandler):
    def _authorize(self, request, *args, **kwargs):
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

            if (re.match(r"(PATCH|PUT|POST)", request.method)):
                self.valid_user_override()

            if (re.match(r"(GET|PUT|POST)", request.method)):
                self.graderoster = graderoster_for_section(
                    self.section, self.instructor, self.user)

        except (InvalidUser, GradingNotPermitted, OverrideNotPermitted) as ex:
            logger.info("Grading for %s not permitted for %s" % (
                section_id, UserService().get_original_user()))
            return self.error_response(403, "%s" % ex)
        except (SecondaryGradingEnabled, GradingPeriodNotOpen,
                InvalidTerm, InvalidSection, MissingInstructorParam) as ex:
            return self.error_response(400, "%s" % ex)
        except ReceiptNotFound as ex:
            return self.error_response(404, "%s" % ex)
        except Exception as ex:
            logger.error("GET graderoster error: %s" % ex)
            err = ex.msg if hasattr(ex, "msg") else ex
            return self.error_response(500, "%s" % err)

    def get(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        section_id = kwargs.get("section_id")

        if self.section.is_grading_period_open():
            kwargs["saved_grades"] = self.saved_grades(section_id)

        content = self.response_content(**kwargs)
        return self.json_response(content)

    def patch(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        section_id = kwargs.get("section_id")

        try:
            grade_data = json.loads(request.body)
            grade = self.save_grade(section_id, grade_data)
        except Exception as ex:
            logger.error("PATCH grade failed for %s: %s" % (section_id, ex))
            return self.error_response(500)

        # PATCH does not return a full graderoster resource
        return self.json_response(grade.json_data())

    def put(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        section_id = kwargs.get("section_id")
        saved_grades = {}
        try:
            for data in json.loads(request.body):
                grade = self.save_grade(section_id, data)
                saved_grades[data["student_id"]] = grade

        except Exception as ex:
            logger.error("PUT grade failed for %s %s" % (section_id, ex))
            return self.error_response(500)

        secondary_section = getattr(self.graderoster, "secondary_section",
                                    None)
        status = 200
        for item in self.graderoster.items:
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                continue

            if (item_is_submitted(item) or item.is_auditor or
                    item.date_withdrawn is not None):
                continue

            student_id = item.student_label(separator="-")
            if not self.validate_grade(item,
                                       saved_grades.get(student_id, None)):
                status = 409

        kwargs["saved_grades"] = saved_grades
        content = self.response_content(**kwargs)
        return self.json_response(content, status=status)

    def post(self, request, *args, **kwargs):
        error = self._authorize(request, *args, **kwargs)
        if error is not None:
            return error

        section_id = kwargs.get("section_id")
        saved_grades = self.saved_grades(section_id)
        secondary_section = getattr(self.graderoster, "secondary_section",
                                    None)

        status = 200
        unsubmitted_count = 0
        for item in self.graderoster.items:
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                continue

            if (item_is_submitted(item) or item.is_auditor or
                    item.date_withdrawn is not None):
                continue

            unsubmitted_count += 1
            student_id = item.student_label(separator="-")
            saved_grade = saved_grades.get(student_id, None)
            if self.validate_grade(item, saved_grade):
                item.no_grade_now = saved_grade.no_grade_now
                item.grade = "" if (
                    item.no_grade_now is True) else saved_grade.grade
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

            self.graderoster = graderoster_for_section(
                self.section, self.instructor, self.user)

        kwargs["saved_grades"] = saved_grades

        content = self.response_content(**kwargs)
        content["graderoster"]["is_submission_confirmation"] = True
        return self.json_response(content, status=status)

    def validate_grade(self, graderoster_item, saved_grade):
        if saved_grade is None:
            return False

        if (saved_grade.is_incomplete and
                (saved_grade.no_grade_now or saved_grade.grade == "N" or
                    saved_grade.grade == "CR")):
            return False

        if saved_grade.no_grade_now:
            return True

        for choice in graderoster_item.grade_choices:
            if (choice is not None and choice != "" and
                    choice == saved_grade.grade):
                return True

        return False

    def saved_grades(self, section_id):
        grade_lookup = {}
        for grade in Grade.objects.get_by_section_id_and_person(
                section_id, self.user.uwregid):
            student_id = grade.student_label()
            grade_lookup[student_id] = grade

        return grade_lookup

    def response_content(self, **kwargs):
        section_id = kwargs.get("section_id")
        saved_grades = kwargs.get("saved_grades", {})
        grading_period_open = self.section.is_grading_period_open()
        allows_writing_credit = self.graderoster.allows_writing_credit
        sources = dict(GradeImport.SOURCE_CHOICES)

        data = {"section_id": section_id,
                "section_name": section_display_name(self.section),
                "students": [],
                "import_choices": [],
                "grade_choices": [],
                "submissions": [],
                "is_writing_section": not allows_writing_credit,
                "has_duplicate_codes": False,
                "has_successful_submissions": False,
                "has_failed_submissions": False,
                "failed_submission_count": 0,
                "has_inprogress_submissions": False,
                "has_grade_imports": False,
                "grade_import_count": 0}

        secondary_section = getattr(self.graderoster, "secondary_section",
                                    None)

        submissions = getattr(self.graderoster, "submissions", {})
        for key in sorted(submissions.iterkeys()):
            sid = key if key != self.graderoster.section.section_id else None
            submission_status = graderoster_status_params(
                self.graderoster, secondary_section_id=sid)
            submission_status["section_id"] = sid
            if submission_status["accepted_date"] is None:
                data["has_inprogress_submissions"] = True
            if submission_status["grade_import"] is not None:
                data["has_grade_imports"] = True
                data["grade_import_count"] += 1
            data["submissions"].append(submission_status)

        if grading_period_open:
            for choice in GradeImport.SOURCE_CHOICES:
                data["import_choices"].append({"value": choice[0],
                                               "label": choice[1]})

        grade_lookup = {}
        for item in sorted_students(self.graderoster.items):
            if (secondary_section is not None and
                    secondary_section.section_id != item.section_id):
                # Filtering by secondary section
                continue

            student_id = item.student_label(separator="-")
            item_id = "-".join([section_id, student_id])
            is_submitted = item_is_submitted(item)
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
                        sorted_grades(item.grade_choices))
                    grade_choices_index = len(data["grade_choices"]) - 1
                    grade_lookup[grade_choices_csv] = grade_choices_index

                # Use saved grade data if it exists
                try:
                    saved_grade = saved_grades[student_id]
                    grade = saved_grade.grade
                    if saved_grade.no_grade_now is True:
                        grade = ""
                    no_grade_now = saved_grade.no_grade_now
                    has_incomplete = saved_grade.is_incomplete
                    has_writing_credit = saved_grade.is_writing
                    if saved_grade.import_grade is not None:
                        import_source = sources[saved_grade.import_source]
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
                "allows_incomplete": (item.allows_incomplete and
                                      not is_submitted),
                "has_incomplete": has_incomplete,
                "is_writing_section": not allows_writing_credit,
                "allows_writing_credit": (allows_writing_credit and
                                          not is_submitted),
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


@method_decorator(never_cache, name='dispatch')
class GradeRosterStatus(GradeFormHandler):
    def get(self, request, *args, **kwargs):
        try:
            self.user = person_from_user()
            self.submitted_graderosters_only = False
        except InvalidUser as ex:
            try:
                self.user = person_from_request(request)
                self.submitted_graderosters_only = True
            except InvalidUser as ex:
                return self.error_response(403, "Invalid user: %s" % ex)

        try:
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

            self.graderoster = graderoster_for_section(
                self.section, self.instructor, self.user,
                submitted_graderosters_only=self.submitted_graderosters_only)

        except GradingNotPermitted as ex:
            logger.info("Grading status for %s not permitted for %s" % (
                ex.section, ex.person))
            return self.error_response(403, "%s" % ex)
        except (InvalidSection, InvalidUser, MissingInstructorParam) as ex:
            return self.error_response(400, "%s" % ex)
        except (GradingPeriodNotOpen, SecondaryGradingEnabled,
                ReceiptNotFound, InvalidTerm) as ex:
            data = section_status_params(self.section, self.instructor)
            if data["grading_status"] is None:
                data["grading_status"] = "%s" % ex
            return self.json_response({"grading_status": data})
        except Exception as ex:
            logger.error("GET graderoster error: %s" % ex)
            err = ex.msg if hasattr(ex, "msg") else ex
            return self.error_response(500, "%s" % err)

        data = section_status_params(self.section, self.instructor)

        section = self.section
        if section.is_primary_section and not section.allows_secondary_grading:
            # Handle secondary sections in this request if appropriate
            data.update(graderoster_status_params(self.graderoster))
            data["secondary_sections"] = []
            for linked_url in section.linked_section_urls:
                secondary_data = self.secondary_section_status(linked_url)
                data["secondary_sections"].append(secondary_data)
        elif (not section.is_primary_section and
                not section.allows_secondary_grading):
            data.update(graderoster_status_params(
                self.graderoster, secondary_section_id=section.section_id))
        else:
            data.update(graderoster_status_params(self.graderoster))

        return self.json_response({"grading_status": data})

    def secondary_section_status(self, section_url):
        section = self.section
        # Avoiding an SWS request for this section
        secondary_section_id = section_url.split("/")[-1].split(".")[0]
        section_id = "-".join([str(section.term.year), section.term.quarter,
                              section.curriculum_abbr, section.course_number,
                              secondary_section_id, self.instructor.uwregid])

        data = section_status_params(section, self.instructor)
        data.update(graderoster_status_params(
            self.graderoster, secondary_section_id=secondary_section_id))

        data["section_id"] = clean_section_id(section_id)
        data["section_url"] = url_for_section(section_id)
        data["display_name"] = " ".join([section.curriculum_abbr,
                                        section.course_number,
                                        secondary_section_id])

        if self.submitted_graderosters_only:
            data["status_url"] = url_for_grading_status(section_id)
        else:
            data["status_url"] = None

        return data
