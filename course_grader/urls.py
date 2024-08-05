# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.urls import re_path
from django.views.generic import TemplateView
from course_grader.views.pages import HomeView
from course_grader.views.support.status import status
from course_grader.views.support.search import graderosters, grade_imports
from course_grader.views.api.sections import Sections, Section
from course_grader.views.api.graderoster import (
    GradeRoster, GradeRosterStatus, GradeRosterExport)
from course_grader.views.api.importgrades import ImportGrades, UploadGrades
from course_grader.views.api.conversionscales import ConversionScales
from course_grader.views.api.submitted_graderoster import (
    SubmissionsByTerm, SubmittedGradeRoster)


urlpatterns = [
    re_path(
        r'^api/v1/sections/(?P<term_id>[^/]*)$',
        Sections.as_view(), name='section-list'),
    re_path(
        r'^api/v1/section/(?P<section_id>[^/]*)$',
        Section.as_view(), name='section'),
    re_path(
        r'^api/v1/graderoster/(?P<section_id>[^/]*)$',
        GradeRoster.as_view(), name='graderoster-edit'),
    re_path(
        r'^api/v1/export/(?P<section_id>[^/]*)$',
        GradeRosterExport.as_view(), name='graderoster-export'),
    re_path(
        r'^api/v1/grading_status/(?P<section_id>[^/]*)$',
        GradeRosterStatus.as_view(), name='grading-status'),
    re_path(
        r'^api/v1/import/(?P<section_id>[^/]*)$',
        ImportGrades.as_view(), name='grade-import'),
    re_path(
        r'^api/v1/import/(?P<section_id>[^/]*)/(?P<import_id>[\d]*)$',
        ImportGrades.as_view(), name='grade-import-id'),
    re_path(
        r'^api/v1/import_file/(?P<section_id>[^/]+)/(?P<import_id>\d+)$',
        UploadGrades.as_view(), name='grade-import-file'),
    re_path(
        r'^api/v1/import_file/(?P<section_id>[^/]*)$',
        UploadGrades.as_view(), name='grade-import-file'),
    re_path(
        r'^api/v1/conversion_scales/(?P<scale>[a-z]*)$',
        ConversionScales.as_view(), name='conversion-scales'),

    # support urls
    re_path(r'^support/status/?$', status, name='gradepage-status'),
    re_path(r'^support/search/?$', graderosters, name='graderoster-search'),
    re_path(r'^support/imports/?$', grade_imports, name='grade-import-search'),
    re_path(
        r'^api/v1/submitted_graderosters/(?P<term_id>[^/]*)$',
        SubmissionsByTerm.as_view(), name='term-submissions'),
    re_path(
        r'^api/v1/submitted_graderoster/(?P<graderoster_id>[\d]*)$',
        SubmittedGradeRoster.as_view(), name='graderoster-download'),

    # vue-router paths
    re_path(
        r"^term/(?P<term_id>[^/]*)$", HomeView.as_view(), name="term-page"),
    re_path(
        r"^section/(?P<section_id>[^/]*)$", HomeView.as_view(),
        name="section-page"),

    # default landing
    re_path(r'^$', HomeView.as_view(), name='home'),
]

# debug routes for developing error pages
if settings.DEBUG:
    urlpatterns.extend([
        re_path(r'^404$', TemplateView.as_view(template_name='404.html')),
        re_path(r'^500$', TemplateView.as_view(template_name='500.html')),
    ])
