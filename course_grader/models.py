# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.db import models
from django.db.models import Q
from restclients_core.exceptions import DataFailureException
from uw_sws_graderoster.models import GradingScale
from course_grader.dao.gradesubmission import submit_grades
from course_grader.dao.notification import notify_grade_submitters
from course_grader.exceptions import InvalidGradingScale
from importlib import import_module
from datetime import datetime, timedelta, timezone
from logging import getLogger
from decimal import Decimal
import json

logger = getLogger(__name__)


class SubmittedGradeRosterManager(models.Manager):
    def get_by_section(self, section, instructor, secondary_section=None):
        kwargs = {'section_id': section.section_label()}
        if secondary_section is not None:
            args = (Q(secondary_section_id=secondary_section.section_label()) |
                    Q(secondary_section_id__isnull=True))
        else:
            args = ()
            if section.is_independent_study:
                kwargs['instructor_id'] = instructor.uwregid

        return super().get_queryset().filter(*args, **kwargs).order_by(
            'secondary_section_id')

    def resubmit_failed(self):
        compare_dt = datetime.now(timezone.utc) - timedelta(minutes=10)
        fails = super().get_queryset().filter(
            Q(status_code__isnull=False) | Q(submitted_date__lt=compare_dt),
            accepted_date__isnull=True
        ).order_by('submitted_date')

        for roster in fails:
            roster.submit()

    def get_status_by_term(self, term):
        return super().get_queryset().filter(
            term_id=term.term_label()
        ).order_by('submitted_date').values(
            'section_id', 'secondary_section_id', 'submitted_date',
            'submitted_by', 'status_code')

    def get_all_terms(self):
        return super().get_queryset().values_list(
            'term_id', flat=True).distinct()


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

    class Meta:
        indexes = [
            models.Index(fields=["secondary_section_id"]),
            models.Index(fields=["section_id"]),
            models.Index(fields=["term_id"]),
            models.Index(fields=["accepted_date"]),
        ]

    def submission_id(self):
        if self.secondary_section_id is not None:
            return self.secondary_section_id.split("/")[-1]
        else:
            return self.section_id.split("/")[-1]

    def submit(self):
        try:
            graderoster = submit_grades(self)
        except Exception as ex:
            logger.error((
                "PUT graderoster failed: {}, Section: {}, "
                "Instructor: {}").format(
                    ex, self.section_id, self.instructor_id))
            self.status_code = getattr(ex, "status", 500)
            self.save()
            return

        self.status_code = 200
        self.accepted_date = datetime.now(timezone.utc)
        self.document = graderoster.xhtml()
        self.save()

        notify_grade_submitters(graderoster, self.submitted_by)


class GradeManager(models.Manager):
    def get_by_section_id_and_person(self, section_id, person_id):
        return super().get_queryset().filter(
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
    is_override_grade = models.BooleanField(default=False)
    comment = models.CharField(max_length=1000, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=32)

    objects = GradeManager()

    @property
    def student_label(self):
        if self.student_reg_id is None or not len(self.student_reg_id):
            raise AttributeError("Missing student_reg_id")

        if self.duplicate_code is not None and len(self.duplicate_code):
            return "-".join([self.student_reg_id, self.duplicate_code])
        else:
            return self.student_reg_id

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
                "is_override_grade": self.is_override_grade,
                "comment": self.comment,
                "last_modified": self.last_modified.isoformat() if (
                    self.last_modified is not None) else None,
                "modified_by": self.modified_by}

    class Meta:
        unique_together = ("section_id", "student_reg_id", "duplicate_code",
                           "modified_by")
        indexes = [
            models.Index(fields=["section_id", "modified_by"]),
        ]


class ImportConversion(models.Model):
    """ Represents a grade import conversion scale.
    """
    scale = models.CharField(max_length=5, choices=GradingScale.SCALE_CHOICES)
    grade_scale = models.TextField()
    calculator_values = models.TextField(null=True)
    lowest_valid_grade = models.CharField(max_length=5, null=True)
    grading_scheme_id = models.IntegerField(null=True)
    grading_scheme_name = models.CharField(max_length=50, null=True)
    course_id = models.IntegerField(null=True)
    course_name = models.CharField(max_length=50, null=True)

    def json_data(self):
        return {
            "id": self.pk,
            "scale": self.scale,
            "grade_scale": json.loads(self.grade_scale),
            "calculator_values": json.loads(self.calculator_values),
            "lowest_valid_grade": self.lowest_valid_grade,
            "grading_scheme_id": self.grading_scheme_id,
            "grading_scheme_name": self.grading_scheme_name,
            "course_id": self.course_id,
            "course_name": self.course_name,
        }

    @staticmethod
    def valid_scale(scale):
        scale = scale.lower()
        if scale in dict(GradingScale.SCALE_CHOICES):
            return scale
        raise InvalidGradingScale()

    @staticmethod
    def decimal_to_percentage(value):
        return float(Decimal(str(value))*100)

    @staticmethod
    def leading_zero(value):
        return "0" + value if value.startswith(".") else value

    @staticmethod
    def from_grading_scheme(data):
        ic = ImportConversion()

        grade_scale = []
        for item in data.get("grading_scheme", []):
            if item["value"] > 0:
                grade_scale.append({
                    "grade": ic.leading_zero(item["name"]),
                    "min_percentage": ic.decimal_to_percentage(item["value"]),
                })
        grade_scale.sort(key=lambda x: x.get("min_percentage"), reverse=True)

        grades = [x['grade'] for x in grade_scale]
        ic.scale = GradingScale().is_any_scale(grades)
        if not ic.scale:
            raise InvalidGradingScale()

        ic.grade_scale = json.dumps(grade_scale)
        ic.calculator_values = json.dumps([])
        ic.lowest_valid_grade = 0.0
        ic.grading_scheme_id = data.get("id")
        ic.grading_scheme_name = data.get("title")
        ic.course_id = data.get("course_id")
        ic.course_name = data.get("course_name")
        return ic


class GradeImportManager(models.Manager):
    def get_last_import_by_section_id(self, section_id):
        return super().get_queryset().filter(
            section_id=section_id,
            accepted_date__isnull=False,
            status_code='200'
        ).order_by('-imported_date')[0:1].get()

    def get_imports_by_person(self, person):
        return super().get_queryset().filter(
            imported_by=person.uwregid,
            accepted_date__isnull=False,
            status_code='200'
        ).order_by('section_id', '-imported_date')

    def get_import_sources_by_term(self, term):
        return super().get_queryset().filter(
            term_id=term.term_label(),
            accepted_date__isnull=False,
            status_code='200'
        ).order_by('imported_date').values(
            'section_id', 'imported_date', 'source')

    def clear_prior_imports_for_section(self, grade_import):
        super().get_queryset().filter(
            section_id=grade_import.section_id
        ).exclude(pk=grade_import.pk).delete()

    def get_all_terms(self):
        return super().get_queryset().values_list(
            'term_id', flat=True).distinct()


class GradeImport(models.Model):
    """ Represents a grade import.
    """
    CANVAS_SOURCE = "canvas"
    CATALYST_SOURCE = "catalyst"
    CSV_SOURCE = "csv"

    SOURCE_CHOICES = (
        (CANVAS_SOURCE, "Canvas Gradebook"),
        (CATALYST_SOURCE, "Catalyst Gradebook"),
        (CSV_SOURCE, "CSV File"),
    )

    _IMPORT_CLASSES = {
        CANVAS_SOURCE: "course_grader.dao.canvas.GradeImportCanvas",
        CSV_SOURCE: "course_grader.dao.csv.GradeImportCSV",
    }

    section_id = models.CharField(max_length=100)
    term_id = models.CharField(max_length=20)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_id = models.CharField(max_length=10, null=True)
    status_code = models.CharField(max_length=3, null=True)
    file_name = models.CharField(max_length=100, null=True)
    file_path = models.CharField(max_length=200, null=True)
    document = models.TextField()
    imported_date = models.DateTimeField(auto_now=True)
    imported_by = models.CharField(max_length=32)
    import_conversion = models.ForeignKey(
        ImportConversion, on_delete=models.CASCADE, null=True)
    accepted_date = models.DateTimeField(null=True)

    objects = GradeImportManager()

    class Meta:
        indexes = [
            models.Index(fields=["term_id"]),
        ]

    def grades_for_section(self, section, instructor, fileobj=None):
        module = self._IMPORT_CLASSES[self.source]
        module_name, class_name = module.rsplit(".", 1)
        _class = getattr(import_module(module_name), class_name)
        grade_source = _class()

        try:
            data = grade_source.grades_for_section(
                section, instructor, source_id=self.source_id, fileobj=fileobj)

            self.document = json.dumps(data)
            self.status_code = 200
            self.file_path = grade_source.get_filepath()
        except DataFailureException as ex:
            self.status_code = ex.status

        self.save()

    def save_conversion_data(self, data):
        if data is not None:
            import_conversion = ImportConversion(
                scale=data.get("scale"),
                grade_scale=json.dumps(data.get("grade_scale")),
                calculator_values=json.dumps(data.get("calculator_values")),
                lowest_valid_grade=data.get("lowest_valid_grade")
            )
            import_conversion.save()
            self.import_conversion = import_conversion
        self.accepted_date = datetime.now(timezone.utc)
        self.save()

    def json_data(self):
        try:
            grade_data = json.loads(self.document)
        except Exception as ex:
            grade_data = {}

        grades = []
        for grade in grade_data.get("grades", []):
            student_reg_id = grade.get("student_reg_id")
            student_number = grade.get("student_number")
            imported_grade = grade.get("grade")
            is_override_grade = False
            has_unposted_grade = False
            comment = None

            if self.source == self.CATALYST_SOURCE:
                student_reg_id = grade["person_id"]
                imported_grade = grade["class_grade"]
                comment = grade["notes"]

            elif self.source == self.CANVAS_SOURCE:
                student_reg_id = grade["sis_user_id"]
                imported_grade = grade["current_score"]

                if ("override_score" in grade and
                        grade["override_score"] is not None):
                    imported_grade = grade["override_score"]
                    is_override_grade = True

                if ("unposted_current_score" in grade and
                        grade["unposted_current_score"] !=
                        grade["current_score"]):
                    has_unposted_grade = True

            if student_reg_id or student_number:
                grades.append({
                    "student_reg_id": student_reg_id,
                    "student_number": student_number,
                    "imported_grade": imported_grade,
                    "is_override_grade": is_override_grade,
                    "has_unposted_grade": has_unposted_grade,
                    "comment": comment,
                    "is_incomplete": grade.get("is_incomplete", False),
                    "is_writing": grade.get("is_writing", False),
                })

        course_grading_schemes = []
        for scheme in grade_data.get("course_grading_schemes", []):
            try:
                conversion = ImportConversion.from_grading_scheme(scheme)
                course_grading_schemes.append(conversion.json_data())
            except InvalidGradingScale:
                pass

        return {"id": self.pk,
                "source": self.source,
                "source_name": dict(self.SOURCE_CHOICES)[self.source],
                "status_code": self.status_code,
                "file_name": self.file_name,
                "file_path": self.file_path,
                "accepted_date": self.accepted_date.isoformat() if (
                    self.accepted_date is not None) else None,
                "imported_date": self.imported_date.isoformat(),
                "imported_by": self.imported_by,
                "imported_grades": grades,
                "import_conversion": self.import_conversion.json_data() if (
                    self.import_conversion is not None) else None,
                "course_grading_schemes": course_grading_schemes}
