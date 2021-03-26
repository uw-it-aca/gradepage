# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.apps import AppConfig
from restclients_core.dao import MockDAO
import os


class CourseGraderConfig(AppConfig):
    name = 'course_grader'

    def ready(self):
        mocks = os.path.join(os.path.dirname(__file__), 'resources')
        MockDAO.register_mock_path(mocks)
