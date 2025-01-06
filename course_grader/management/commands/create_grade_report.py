# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import localtime
from uw_sws_graderoster.models import GradeRoster
from uw_sws_graderoster import DataFailureException
from uw_sws.models import Section
from course_grader.models import SubmittedGradeRoster
from course_grader.dao.person import person_from_regid
from lxml import etree
import csv


class Command(BaseCommand):
    help = "Create a report containing submitted grades by term"

    def add_arguments(self, parser):
        parser.add_argument('term_id', help='Term ID: YYYY,quarter')

    def get_submitted_by_term(self, term_id):
        return SubmittedGradeRoster.objects.filter(
            term_id=term_id, accepted_date__isnull=False
        ).order_by('submitted_date').values_list('id', flat=True)

    def get_graderoster_by_id(self, id):
        return SubmittedGradeRoster.objects.values_list(
            'section_id', 'document', 'submitted_by', 'submitted_date').get(
                pk=id)

    def handle(self, *args, **options):
        term_id = options.get('term_id')

        outpath = f'{term_id.replace(",", "-")}-submitted-grades.csv'
        outfile = open(outpath, 'w')
        csv.register_dialect('unix_newline', lineterminator='\n')
        writer = csv.writer(outfile, dialect='unix_newline')
        writer.writerow([
            'section', 'submitted_date', 'submitted_by',
            'student_number', 'student_name', 'section_id', 'duplicate_code',
            'date_withdrawn', 'student_credits', 'is_auditor',
            'allows_writing_credit', 'allows_incomplete',
            'allows_grade_change', 'has_writing_credit', 'has_incomplete',
            'no_grade_now', 'grade'])

        submitted_ids = self.get_submitted_by_term(term_id)
        print(f'Total sections submitted: {len(submitted_ids)}')

        for (idx, id) in enumerate(submitted_ids):
            (section_id, document, submitted_by, submitted_date) = (
                self.get_graderoster_by_id(id))

            try:
                root = etree.fromstring(document.strip())
                submitter = person_from_regid(submitted_by)
            except etree.XMLSyntaxError as ex:
                continue
            except DataFailureException as ex:
                continue

            graderoster = GradeRoster.from_xhtml(
                root, section=Section(), instructor=submitter)

            for item in graderoster.items:
                writer.writerow([
                    section_id,
                    localtime(submitted_date).strftime(
                        '%Y-%m-%d %H:%M:%S'),
                    submitter.uwnetid,
                    item.student_number,
                    ' '.join([item.student_first_name,
                              item.student_surname]).strip(),
                    item.section_id,
                    item.duplicate_code,
                    item.date_withdrawn,
                    item.student_credits,
                    'y' if item.is_auditor else 'n',
                    'y' if graderoster.allows_writing_credit else 'n',
                    'y' if item.allows_incomplete else 'n',
                    'y' if item.allows_grade_change else 'n',
                    'y' if item.has_writing_credit else 'n',
                    'y' if item.has_incomplete else 'n',
                    'y' if item.no_grade_now else 'n',
                    'X' if item.no_grade_now else item.grade,
                ])

        outfile.close()
