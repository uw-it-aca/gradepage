from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import translation
from course_grader.models import SubmittedGradeRoster


class Command(BaseCommand):
    help = "Submits failed graderosters"

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        models = SubmittedGradeRoster.objects.filter(
            accepted_date__isnull=True,
            status_code__isnull=False).order_by("submitted_date")

        for model in models:
            model.submit()
