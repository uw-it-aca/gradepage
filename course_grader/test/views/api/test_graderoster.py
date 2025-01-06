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
            b',,,\nStudent Grade Change List,,,\nINSTRUCTIONS:,,,\nComplete '
            b'this spreadsheet and upload the file using the UW Registrar\'s '
            b'Online Change of Grade Request Form.,,,\nhttps://apps.registrar.'
            b'washington.edu/grade-change/pages/change.php,,,\nDO NOT EMAIL '
            b'this spreadsheet with student grade information.,,,\n,,,\n'
            b'INSTRUCTOR NAME AND EMAIL:,,,\n"Jamesy McJamesy",javerage@uw.edu'
            b',,\n,,,\nCOURSE PREFIX AND NUMBER (AND SECTION):,,,\n"TRAIN 101 '
            b'A",,,\n,,,\nQUARTER AND YEAR:,,,\nSpring 2013,,,\n,,,\n,,,\n,,,'
            b'\nSTUDENT NUMBER,"STUDENT NAME (LAST, FIRST)",GRADE FROM,GRADE '
            b'TO\n000000,"AVERAGE, J",4.0,\n'
        ))
