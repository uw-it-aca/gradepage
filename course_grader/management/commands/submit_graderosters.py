# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import translation
from course_grader.models import SubmittedGradeRoster


class Command(BaseCommand):
    help = "Submits failed graderosters"

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)
        SubmittedGradeRoster.objects.resubmit_failed()
