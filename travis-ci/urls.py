from django.conf.urls import include, url


urlpatterns = [
    url(r'^', include('course_grader.urls')),
]
