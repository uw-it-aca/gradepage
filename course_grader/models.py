from django.db import models
from django.db.models import Q
from django.utils import timezone
from restclients_core.exceptions import DataFailureException
from course_grader.dao.canvas import grades_for_section as canvas_grades
from course_grader.dao.catalyst import grades_for_section as catalyst_grades
from course_grader.dao.gradesubmission import submit_grades
from course_grader.dao.notification import notify_grade_submitters
from logging import getLogger
import json

logger = getLogger(__name__)


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

        return super(SubmittedGradeRosterManager, self).get_queryset().filter(
            *args, **kwargs).order_by('secondary_section_id')

    def get_status_by_term(self, term):
        return super(SubmittedGradeRosterManager, self).get_queryset().filter(
            term_id=term.term_label()
        ).order_by('submitted_date').values(
            'section_id', 'secondary_section_id', 'submitted_date',
            'submitted_by', 'status_code')

    def get_all_terms(self):
        return super(SubmittedGradeRosterManager, self).get_queryset(
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
        self.accepted_date = timezone.now()
        self.document = graderoster.xhtml()
        self.save()

        notify_grade_submitters(graderoster, self.submitted_by)


class GradeManager(models.Manager):
    def get_by_section_id_and_person(self, section_id, person_id):
        return super(GradeManager, self).get_queryset().filter(
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

    def student_label(self):
        label = self.student_reg_id
        if self.duplicate_code is not None and len(self.duplicate_code):
            label += "-{}".format(self.duplicate_code)
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
                "is_override_grade": self.is_override_grade,
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
        return super(GradeImportManager, self).get_queryset().filter(
            section_id=section_id,
            import_conversion__isnull=False,
            status_code='200'
        ).order_by('-imported_date')[0:1].get()

    def get_imports_by_person(self, person):
        return super(GradeImportManager, self).get_queryset().filter(
            imported_by=person.uwregid,
            import_conversion__isnull=False,
            status_code='200'
        ).order_by('section_id', '-imported_date')

    def get_import_sources_by_term(self, term):
        return super(GradeImportManager, self).get_queryset().filter(
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
    import_conversion = models.ForeignKey(
        ImportConversion, on_delete=models.CASCADE, null=True)

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
            student_reg_id = None
            imported_grade = None
            is_override_grade = False
            comment = None

            if self.source == self.CATALYST_SOURCE:
                student_reg_id = grade["person_id"]
                imported_grade = grade["class_grade"]
                comment = grade["notes"]

            elif self.source == self.CANVAS_SOURCE:
                student_reg_id = grade["sis_user_id"]
                imported_grade = grade["current_score"]

                if grade["override_score"] is not None:
                    imported_grade = grade["override_score"]
                    is_override_grade = True

            if student_reg_id is not None:
                grades.append({"student_reg_id": student_reg_id,
                               "imported_grade": imported_grade,
                               "is_override_grade": is_override_grade,
                               "comment": comment})

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
                "warnings": grade_data.get("warnings", [])}
