from django.conf import settings
from django.urls import re_path
from django.views.generic import TemplateView
from course_grader.views.chooser import home
from course_grader.views.section import section
from course_grader.views.support.status import status
from course_grader.views.support.search import graderosters, grade_imports
from course_grader.views.api.sections import Sections
from course_grader.views.api.graderoster import (
    GradeRoster, GradeRosterStatus, GradeRosterExport)
from course_grader.views.api.importgrades import ImportGrades
from course_grader.views.api.conversionscales import ConversionScales
from course_grader.views.api.submitted_graderoster import (
    SubmissionsByTerm, SubmittedGradeRoster)


urlpatterns = [
    re_path(r'^$', home),
    re_path(r'^section/(?P<url_token>[^/]*)$', section),
    re_path(r'^api/v1/sections/(?P<term_id>[^/]*)$', Sections.as_view()),
    re_path(
        r'^api/v1/graderoster/(?P<section_id>[^/]*)$',
        GradeRoster.as_view()),
    re_path(
        r'^api/v1/graderoster/(?P<section_id>[^/]*)/export$',
        GradeRosterExport.as_view()),
    re_path(
        r'^api/v1/grading_status/(?P<section_id>[^/]*)$',
        GradeRosterStatus.as_view()),
    re_path(r'^api/v1/import/(?P<section_id>[^/]*)$', ImportGrades.as_view()),
    re_path(
        r'^api/v1/import/(?P<section_id>[^/]*)/(?P<import_id>[\d]*)$',
        ImportGrades.as_view()),
    re_path(
        r'^api/v1/conversion_scales/(?P<scale>[a-z]*)$',
        ConversionScales.as_view()),

    # support urls
    re_path(r'^support/status/?$', status, name='gradepage_status'),
    re_path(r'^support/search/?$', graderosters, name='search_graderosters'),
    re_path(r'^support/imports/?$', grade_imports, name='grade_imports'),
    re_path(
        r'^api/v1/submitted_graderosters/(?P<term_id>[^/]*)$',
        SubmissionsByTerm.as_view(), name="term_submissions"),
    re_path(
        r'^api/v1/submitted_graderoster/(?P<graderoster_id>[\d]*)$',
        SubmittedGradeRoster.as_view(), name='submitted_graderoster'),
]

# debug routes for developing error pages
if settings.DEBUG:
    urlpatterns.extend([
        re_path(r'^404$', TemplateView.as_view(template_name='404.html')),
        re_path(r'^500$', TemplateView.as_view(template_name='500.html')),
    ])
