from django.core.management.base import BaseCommand, CommandError
from course_grader.dao.person import person_from_netid
from course_grader.dao.section import section_from_label
from course_grader.dao.catalyst import grades_for_section
from restclients.exceptions import DataFailureException
import sys
import json


class Command(BaseCommand):
    args = "<section_id> <login>"
    help = "Imports grades from Catalyst GradeBook."

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError("section_id and login are required")

        section_id = args[0]
        login = args[1]
        try:
            user = person_from_netid(login)
        except Exception as ex:
            print ex
            sys.exit()

        try:
            section = section_from_label(section_id)
            grade_import = grades_for_section(section, user, None)
            print json.dumps(grade_import, indent=4)
            print "%s grades imported" % len(grade_import['grades'])
        except DataFailureException as ex:
            print ex
