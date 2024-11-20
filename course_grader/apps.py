# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.apps import AppConfig
from django.contrib.staticfiles.apps import StaticFilesConfig
from restclients_core.dao import MockDAO
import os


class CourseGraderFilesConfig(StaticFilesConfig):
    ignore_patterns = ["CVS", "*~"]


class CourseGraderConfig(AppConfig):
    name = "course_grader"

    def ready(self):
        mocks = os.path.join(os.path.dirname(__file__), "resources")
        MockDAO.register_mock_path(mocks)
