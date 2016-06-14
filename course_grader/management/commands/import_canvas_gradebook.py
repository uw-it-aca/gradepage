from django.core.management.base import BaseCommand, CommandError
from course_grader.dao.section import section_from_param
from course_grader.dao.canvas import grades_for_section
from restclients.exceptions import DataFailureException
import sys
import json


class Command(BaseCommand):
    args = "<section_param>"
    help = "Imports grades from a Canvas GradeBook."

    def handle(self, *args, **options):
        if not len(args):
            raise CommandError("section_param is required")

        section_id = args[0]
        try:
            (section, user) = section_from_param(section_id)
        except Exception as ex:
            print ex
            sys.exit()

        try:
            grade_import = grades_for_section(section, user)
            print json.dumps(grade_import, indent=4)
            print "%s grades imported" % len(grade_import['grades'])
        except DataFailureException as ex:
            print ex
