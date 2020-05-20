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
            b'Student Grade Change List,,,\nINSTRUCTIONS:,,,\nComplete this '
            b'spreadsheet and upload the file using the UW Registrar\'s Online'
            b' Change of Grade Request Form.,,,\n'
            b'https://apps.registrar.washington.edu/grade-change/pages/change.'
            b'php,,,\nDO NOT EMAIL this spreadsheet'
            b' with student grade information.,,,\n,,,\nINSTRUCTORS NAME AND'
            b' EMAIL:,"Jamesy McJamesy",javerage@uw.edu,\n,,,\nCOURSE PREFIX'
            b' AND NUMBER (AND SECTION):,TRAIN,101,A\n,,,\nQUARTER AND YEAR:'
            b',spring,2013,\n,,,\n,,,\n,,,\nSTUDENT NUMBER,"STUDENT NAME ('
            b'LAST, FIRST)",GRADE FROM,GRADE TO\n000000,"Average, J",4.0,\n')
        )
