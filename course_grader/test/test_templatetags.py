# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


import re
from django.test import TestCase
from course_grader.templatetags.vite import vite_styles, vite_scripts


class ViteTestClass(TestCase):
    def test_vite_styles(self):
        entries = ("course_grader_vue/main.js",)
        link = vite_styles(*entries)
        pattern = re.compile(
            '<link rel="stylesheet" href="/static/course_grader/assets/'
            'main[\\d\\w-]*.css" />'
        )
        self.assertTrue(pattern.match(link))

    def test_vite_scripts(self):
        entries = ("course_grader_vue/main.js",)
        script = vite_scripts(*entries)
        pattern = re.compile(
            '<script type="module" src="/static/course_grader/assets/'
            'main[\\d\\w-]*.js"></script>'
        )
        self.assertTrue(pattern.match(script))
