# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.test import TestCase, override_settings
from uw_pws.util import fdao_pws_override
from uw_sws.util import fdao_sws_override
from course_grader.dao.person import person_from_netid
from course_grader.dao.section import section_from_param
from course_grader.views.api.graderoster import GradeRosterExport


@fdao_sws_override
@fdao_pws_override
class GradeRosterExportTest(TestCase):
    def test_create_response(self):
        view = GradeRosterExport()
        (section, instructor) = section_from_param(
            '2013-spring-TRAIN-101-A-9136CCB8F66711D5BE060004AC494FFE')
        view.section = section
        view.instructor = instructor
        view.user = person_from_netid('javerage')

        mock_content = {'graderoster': {'students': [{
            'student_number': '000000',
            'student_firstname': 'J',
            'student_lastname': 'Average',
            'grade': '4.0',
        }]}}
        response = view.create_response(mock_content)
        self.assertEqual(response.get('Content-Disposition'),
                         'attachment; filename="2013-spring-TRAIN-101-A.csv"')

        self.assertEqual(response.content, (
            b',,,\nStudent Grade Change List'
            b',,,\n'
            b'INSTRUCTIONS:,,,\n'
            b'Complete this spreadsheet and upload the file using the '
            b'Office of the University Registrar\'s Online Change of Grade '
            b'Request Form.,,,\n'
            b'https://apps.registrar.washington.edu/grade-change/pages/change.php'  # noqa
            b',,,\n'
            b'DO NOT EMAIL this spreadsheet with student grade information.'
            b',,,\n,,,\n'
            b'INSTRUCTOR NAME AND EMAIL:,,,\n'
            b'"Jamesy McJamesy",javerage@uw.edu,,\n,,,\n'
            b'COURSE PREFIX AND NUMBER (AND SECTION):,,,\n'
            b'"TRAIN 101 A",,,\n,,,\n'
            b'QUARTER AND YEAR:,,,\nSpring 2013,,,\n,,,\n'
            b'CAMPUS:,,,\nSeattle,,,\n,,,\n,,,\n,,,\n'
            b'STUDENT NUMBER,"STUDENT NAME (LAST, FIRST)",GRADE FROM,GRADE TO'
            b'\n'
            b'000000,"AVERAGE, J",4.0,\n'
        ))
