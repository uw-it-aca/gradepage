from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from course_grader.views.api.sections import Sections
from course_grader.views.api.graderoster import GradeRoster
from course_grader.views.api.importgrades import ImportGrades
from course_grader.views.api.conversionscales import ConversionScales

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^/?$', 'course_grader.views.chooser.home'),
    url(r'^section/(?P<url_token>[^/]*)$',
        'course_grader.views.section.section'),
    url(r'^api/v1/sections/(?P<term_id>[^/]*)$', Sections().run),
    url(r'^api/v1/graderoster/(?P<section_id>[^/]*)$', GradeRoster().run),
    url(r'^api/v1/import/(?P<section_id>[^/]*)$', ImportGrades().run),
    url(r'^api/v1/import/(?P<section_id>[^/]*)/(?P<import_id>[\d]*)$',
        ImportGrades().run),
    url(r'^api/v1/conversion_scales/(?P<scale>[a-z]*)$',
        ConversionScales().run),

    # support urls
    url(r'^support/status/?$', 'course_grader.views.support.status.status'),
    url(r'^support/search/?$',
        'course_grader.views.support.search.graderosters'),
    url(r'^support/imports/?$',
        'course_grader.views.support.search.grade_imports'),
    url(r'^support/download/(?P<graderoster_id>[\d]*)$',
        'course_grader.views.support.download.graderoster'),
)

# debug routes for developing error pages
if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^404$', TemplateView.as_view(template_name='404.html')),
        (r'^500$', TemplateView.as_view(template_name='500.html')),
    )
