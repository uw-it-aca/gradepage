from django.conf import settings
from django.conf.urls import url
from django.views.generic import TemplateView
from course_grader.views import user_login
from course_grader.views.chooser import home
from course_grader.views.section import section
from course_grader.views.support.status import status
from course_grader.views.support.search import graderosters, grade_imports
from course_grader.views.api.sections import Sections
from course_grader.views.api.graderoster import GradeRoster, GradeRosterStatus
from course_grader.views.api.importgrades import ImportGrades
from course_grader.views.api.conversionscales import ConversionScales
from course_grader.views.api.submitted_graderoster import (
    SubmissionsByTerm, SubmittedGradeRoster)

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'^$', home),
    url(r'^login/?$', user_login),
    url(r'^section/(?P<url_token>[^/]*)$', section),
    url(r'^api/v1/sections/(?P<term_id>[^/]*)$', Sections().run),
    url(r'^api/v1/graderoster/(?P<section_id>[^/]*)$', GradeRoster().run),
    url(r'^api/v1/grading_status/(?P<section_id>[^/]*)$',
        GradeRosterStatus().run),
    url(r'^api/v1/import/(?P<section_id>[^/]*)$', ImportGrades().run),
    url(r'^api/v1/import/(?P<section_id>[^/]*)/(?P<import_id>[\d]*)$',
        ImportGrades().run),
    url(r'^api/v1/conversion_scales/(?P<scale>[a-z]*)$',
        ConversionScales().run),

    # support urls
    url(r'^support/status/?$', status),
    url(r'^support/search/?$', graderosters),
    url(r'^support/imports/?$', grade_imports),
    url(r'^api/v1/submitted_graderosters/(?P<term_id>[^/]*)$',
        SubmissionsByTerm().run, name="term_submissions"),
    url(r'^api/v1/submitted_graderoster/(?P<graderoster_id>[\d]*)$',
        SubmittedGradeRoster().run, name='submitted_graderoster'),
]

# debug routes for developing error pages
if settings.DEBUG:
    urlpatterns.extend([
        (r'^404$', TemplateView.as_view(template_name='404.html')),
        (r'^500$', TemplateView.as_view(template_name='500.html')),
    ])
