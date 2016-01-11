from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from restclients.exceptions import DataFailureException
from restclients.sws.graderoster import update_graderoster
from restclients.sws.graderoster import graderoster_from_xhtml
from restclients.util.retry import retry
from course_grader.dao.section import section_from_label
from course_grader.dao.person import person_from_regid
from course_grader.dao.canvas import grades_for_section as canvas_grades
from course_grader.dao.catalyst import grades_for_section as catalyst_grades
from course_grader.views.email import submission_message
from urllib3.exceptions import SSLError
import logging
import json


logger = logging.getLogger(__name__)


class SubmittedGradeRosterManager(models.Manager):
    def get_by_section(self, section, instructor, secondary_section=None):
        kwargs = {'section_id': section.section_label()}
        if secondary_section is not None:
            args = (Q(secondary_section_id=secondary_section.section_label()) |
                    Q(secondary_section_id__isnull=True),)
        else:
            args = ()
            if section.is_independent_study:
                kwargs['instructor_id'] = instructor.uwregid

        return super(SubmittedGradeRosterManager, self).get_query_set().filter(
            *args, **kwargs).order_by('secondary_section_id')

    def get_submitted_dates_by_term(self, term):
        return super(SubmittedGradeRosterManager, self).get_query_set().filter(
            term_id=term.term_label()
        ).order_by('submitted_date').values('submitted_date')

    def get_all_terms(self):
        return super(SubmittedGradeRosterManager, self).get_query_set(
        ).values_list('term_id', flat=True).distinct()


class SubmittedGradeRoster(models.Model):
    """ Represents a submitted graderoster document.
    """
    section_id = models.CharField(max_length=100)
    secondary_section_id = models.CharField(max_length=100, null=True)
    instructor_id = models.CharField(max_length=32)
    term_id = models.CharField(max_length=20)
    submitted_date = models.DateTimeField(auto_now_add=True)
    submitted_by = models.CharField(max_length=32)
    accepted_date = models.DateTimeField(null=True)
    status_code = models.CharField(max_length=3, null=True)
    document = models.TextField()
    catalyst_gradebook_id = models.IntegerField(null=True)

    objects = SubmittedGradeRosterManager()

    def submission_id(self):
        if self.secondary_section_id is not None:
            return self.secondary_section_id.split("/")[-1]
        else:
            return self.section_id.split("/")[-1]

    def submit(self):

        @retry(SSLError, tries=3, delay=1, logger=logger)
        def _update_graderoster(graderoster):
            return update_graderoster(graderoster)

        try:
            graderoster = graderoster_from_xhtml(
                self.document, section_from_label(self.section_id),
                person_from_regid(self.instructor_id))

            if self.secondary_section_id is not None:
                graderoster.secondary_section = section_from_label(
                    self.secondary_section_id)

            ret_graderoster = _update_graderoster(graderoster)

        except Exception as ex:
            logger.exception(ex)
            self.status_code = getattr(ex, "status", 500)
            self.save()
            return

        # The returned graderoster from PUT omits items for which a grade was
        # not actually submitted, and it lacks secondary section info for each
        # item. To create a saved graderoster receipt, merge the returned
        # graderoster into the submitted graderoster, to capture both the
        # submitted grade and the returned status code/message for each item.
        for item in ret_graderoster.items:
            if item.status_code is None:
                continue

            try:
                idx = graderoster.items.index(item)
                graderoster.items[idx].status_code = item.status_code
                graderoster.items[idx].status_message = item.status_message
                graderoster.items[idx].date_graded = item.date_graded
                graderoster.items[idx].grade_document_id = \
                    item.grade_document_id
                graderoster.items[idx].grade_submitter_source = \
                    item.grade_submitter_source
                self._log_grade(graderoster.items[idx])

            except Exception as ex:
                pass

        # Update model attrs and save
        self.status_code = 200
        self.accepted_date = timezone.now()
        self.document = graderoster.xhtml()
        self.save()

        # Notify submitters
        self._notify_submitters(graderoster)

    def _notify_submitters(self, graderoster):
        people = {graderoster.instructor.uwregid: graderoster.instructor}

        for person in graderoster.authorized_grade_submitters:
            people[person.uwregid] = person

        for delegate in graderoster.grade_submission_delegates:
            people[delegate.person.uwregid] = delegate.person

        submitter = None
        recipients = []
        for person in people.values():
            recipients.append("%s@uw.edu" % person.uwnetid)

            if person.uwregid == self.submitted_by:
                submitter = person

        if submitter is None:
            submitter = person_from_regid(self.submitted_by)

        (subject, text_body, html_body) = submission_message(graderoster,
                                                             submitter)

        message = EmailMultiAlternatives(subject, text_body,
                                         settings.EMAIL_NOREPLY_ADDRESS,
                                         recipients)
        message.attach_alternative(html_body, "text/html")

        secondary_section = getattr(graderoster, "secondary_section", None)
        section_id = graderoster.section.section_label() if (
            secondary_section is None) else secondary_section.section_label()

        try:
            message.send()
            log_message = "Submission email sent"
        except Exception as ex:
            logger.exception(ex)
            log_message = "Submission email failed"

        for recipient in recipients:
            logger.info("%s, To: %s, Section: %s, Status: %s" % (
                log_message, recipient, section_id, subject))

    def _log_grade(self, item):
        if item.is_auditor or item.date_withdrawn:
            return

        if self.secondary_section_id is not None:
            section_id = self.secondary_section_id
        else:
            section_id = self.section_id

        logged_grade = "X" if item.no_grade_now else str(item.grade)
        if item.has_incomplete:
            logged_grade = "I," + logged_grade
        if item.has_writing_credit:
            logged_grade += ",W"

        logger.info("Grade submitted, Student: %s, Section: %s, Grade: %s, " +
                    "Code: %s, Message: %s" % (
                        item.student_label(separator="-"), section_id,
                        logged_grade, item.status_code, item.status_message))


class GradeManager(models.Manager):
    def get_by_section_id_and_person(section_id, person_id):
        return super(GradeManager, self).get_query_set().filter(
            section_id=section_id, modified_by=person_id)


class Grade(models.Model):
    """ Represents a saved grade.
    """
    section_id = models.CharField(max_length=100)
    student_reg_id = models.CharField(max_length=32)
    duplicate_code = models.CharField(max_length=15, default="")
    grade = models.CharField(max_length=100, null=True)
    is_writing = models.BooleanField(default=False)
    is_incomplete = models.BooleanField(default=False)
    no_grade_now = models.BooleanField(default=False)
    import_source = models.CharField(max_length=50, null=True)
    import_grade = models.CharField(max_length=100, null=True)
    comment = models.CharField(max_length=1000, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=32)

    objects = GradeManager()

    def student_label(self):
        label = self.student_reg_id
        if self.duplicate_code is not None and len(self.duplicate_code):
            label += "-%s" % self.duplicate_code
        return label

    def json_data(self):
        return {"section_id": self.section_id,
                "student_reg_id": self.student_reg_id,
                "duplicate_code": self.duplicate_code,
                "grade": self.grade,
                "no_grade_now": self.no_grade_now,
                "is_writing": self.is_writing,
                "is_incomplete": self.is_incomplete,
                "import_source": self.import_source,
                "import_grade": self.import_grade,
                "comment": self.comment,
                "last_modified": self.last_modified.isoformat(),
                "modified_by": self.modified_by}

    class Meta:
        unique_together = ("section_id", "student_reg_id", "duplicate_code",
                           "modified_by")


class ImportConversion(models.Model):
    """ Represents a grade import conversion scale.
    """
    UNDERGRADUATE_SCALE = "ug"
    GRADUATE_SCALE = "gr"
    PASSFAIL_SCALE = "pf"
    CREDIT_SCALE = "cnc"
    HIGHPASSFAIL_SCALE = "hpf"

    SCALE_CHOICES = (
        (UNDERGRADUATE_SCALE, "Undergraduate Scale (4.0-0.7)"),
        (GRADUATE_SCALE, "Graduate Scale (4.0-1.7)"),
        (PASSFAIL_SCALE, "School of Medicine Pass/No Pass"),
        (CREDIT_SCALE, "Credit/No Credit Scale"),
        (HIGHPASSFAIL_SCALE, "Honors/High Pass/Pass/Fail Scale")
    )

    scale = models.CharField(max_length=5, choices=SCALE_CHOICES)
    grade_scale = models.TextField()
    calculator_values = models.TextField(null=True)
    lowest_valid_grade = models.CharField(max_length=5, null=True)

    def json_data(self):
        return {
            "id": self.pk,
            "scale": self.scale,
            "grade_scale": json.loads(self.grade_scale),
            "calculator_values": json.loads(self.calculator_values),
            "lowest_valid_grade": self.lowest_valid_grade,
        }


class GradeImportManager(models.Manager):
    def get_last_import_by_section_id(self, section_id):
        return super(GradeImportManager, self).get_query_set().filter(
            section_id=section_id,
            import_conversion__isnull=False,
            status_code='200'
        ).order_by('-imported_date')[0:1].get()

    def get_imports_by_person(self, person):
        return super(GradeImportManager, self).get_query_set().filter(
            imported_by=person.uwregid,
            import_conversion__isnull=False,
            status_code='200'
        ).order_by('section_id', '-imported_date')

    def get_import_sources_by_term(self, term):
        return super(GradeImportManager, self).get_query_set().filter(
            term_id=term.term_label()
        ).order_by('imported_date').values('imported_date', 'source')


class GradeImport(models.Model):
    """ Represents a grade import.
    """
    CANVAS_SOURCE = "canvas"
    CATALYST_SOURCE = "catalyst"

    SOURCE_CHOICES = (
        (CANVAS_SOURCE, "Canvas Gradebook"),
        (CATALYST_SOURCE, "Catalyst GradeBook"),
    )

    section_id = models.CharField(max_length=100)
    term_id = models.CharField(max_length=20)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_id = models.CharField(max_length=10, null=True)
    status_code = models.CharField(max_length=3, null=True)
    document = models.TextField()
    imported_date = models.DateTimeField(auto_now=True)
    imported_by = models.CharField(max_length=32)
    import_conversion = models.ForeignKey(ImportConversion, null=True)

    objects = GradeImportManager()

    def grades_for_section(self, section, instructor):
        try:
            if self.source == self.CATALYST_SOURCE:
                data = catalyst_grades(section, instructor, self.source_id)
            elif self.source == self.CANVAS_SOURCE:
                data = canvas_grades(section, instructor)
            else:
                return

            self.document = json.dumps(data)
            self.status_code = 200
        except DataFailureException as ex:
            self.status_code = ex.status

        self.save()

    def json_data(self):
        try:
            grade_data = json.loads(self.document)

            # Prior to Winter 2015, imports were stored as a list
            if isinstance(grade_data, list):
                grade_data = {"grades": grade_data}

        except Exception as ex:
            grade_data = {}

        grades = []
        for grade in grade_data.get("grades", []):
            if self.source == self.CATALYST_SOURCE:
                grades.append({"student_reg_id": grade["person_id"],
                               "imported_grade": grade["class_grade"],
                               "comment": grade["notes"]})

            elif self.source == self.CANVAS_SOURCE:
                grades.append({"student_reg_id": grade["sis_user_id"],
                               "imported_grade": grade["current_score"],
                               "comment": None})

            else:
                continue

        if self.import_conversion is not None:
            import_conversion_data = self.import_conversion.json_data()
        else:
            import_conversion_data = None

        return {"id": self.pk,
                "source": self.source,
                "source_name": dict(self.SOURCE_CHOICES)[self.source],
                "status_code": self.status_code,
                "imported_date": self.imported_date.isoformat(),
                "imported_by": self.imported_by,
                "imported_grades": grades,
                "import_conversion": import_conversion_data,
                "muted_assignments": grade_data.get("muted_assignments", [])}
