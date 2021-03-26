# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from course_grader.models import SubmittedGradeRoster, GradeImport, Grade


class Command(BaseCommand):
    help = "Deletes grade data by date"

    def add_arguments(self, parser):
        parser.add_argument(
            "-c", "--commit", action="store_true", dest="commit",
            default=False, help="Actually delete grade data")

    def handle(self, *args, **options):
        commit = options.get("commit")
        retention_date = timezone.localtime(timezone.now()) - relativedelta(
            years=settings.GRADE_RETENTION_YEARS)

        if not commit:
            print("Retention date is: {}".format(retention_date))

        # Saved grades
        grade_count = Grade.objects.filter(
            last_modified__lt=retention_date).count()

        if not commit:
            print("Saved grades found: {}".format(grade_count))

        if grade_count and commit:
            Grade.objects.filter(
                last_modified__lt=retention_date).delete()

        # Grade imports
        grade_import_count = GradeImport.objects.filter(
            imported_date__lt=retention_date).count()

        if not commit:
            print("Grade imports found: {}".format(grade_import_count))

        if grade_import_count and commit:
            GradeImport.objects.filter(
                imported_date__lt=retention_date).delete()

        # Graderosters
        graderoster_count = SubmittedGradeRoster.objects.filter(
            submitted_date__lt=retention_date).defer("document").count()

        if not commit:
            print("Graderoster receipts found: {}".format(graderoster_count))

        if graderoster_count and commit:
            SubmittedGradeRoster.objects.filter(
                submitted_date__lt=retention_date).delete()
