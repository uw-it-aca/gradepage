from django.core.management.base import BaseCommand, CommandError
from course_grader.models import SubmittedGradeRoster


class Command(BaseCommand):
    help = "Submits failed graderosters"

    def handle(self, *args, **options):
        models = SubmittedGradeRoster.objects.filter(
            accepted_date__isnull=True,
            status_code__isnull=False).order_by("submitted_date")

        for model in models:
            model.submit()
