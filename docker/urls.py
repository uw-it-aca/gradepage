from .base_urls import *
from django.urls import include, re_path
from django.views.i18n import JavaScriptCatalog

urlpatterns += [
    re_path(r'^', include('course_grader.urls')),
    re_path(r'^support/?', include('userservice.urls')),
    re_path(r'^restclients/', include('rc_django.urls')),
    re_path(r'^persistent_message/', include('persistent_message.urls')),
    re_path(r'^jsi18n/$', JavaScriptCatalog.as_view(packages=[
                'grade_conversion_calculator', 'course_grader']),
            name='javascript-catalog'),
]
