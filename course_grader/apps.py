from django.apps import AppConfig
from restclients_core.dao import MockDAO
import os


class CourseGraderConfig(AppConfig):
    name = 'course_grader'

    def ready(self):
        mocks = os.path.join(os.path.dirname(__file__), 'resources')
        MockDAO.register_mock_path(mocks)
