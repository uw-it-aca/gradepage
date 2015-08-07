from django.core.management.base import BaseCommand, CommandError
from course_grader.dao.person import person_from_username
from course_grader.dao.catalyst import grades_for_section
from restclients.exceptions import DataFailureException
import json
import sys


class Command(BaseCommand):
    args = "<gradebook_id> <login>"
    help = "Imports grades from Catalyst GradeBook."

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError("gradebook_id and login are required")

        gradebook_id = args[0]
        login = args[1]
        try:
            user = person_from_username(login)
        except Exception as ex:
            print ex
            sys.exit()

        try:
            grade_import = grades_for_section(None, user, gradebook_id)
            print len(json.loads(grade_import))
            print grade_import
        except DataFailureException as ex:
            print ex
