# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging

from django.core.management.base import BaseCommand

from course_grader.cache import RestClientsCache

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Clear the GradePage cache"

    def handle(self, *args, **options):
        client = RestClientsCache()
        status = client.flush_all()
        logger.info(f"Cache cleared: {status}")
