# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import TestCase, RequestFactory, override_settings
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from userservice.user import UserServiceMiddleware
from course_grader.views.decorators import xhr_login_required
import mock


@method_decorator(xhr_login_required, name='dispatch')
class XHRLoginRequiredView(View):
    def get(request, *args, **kwargs):
        return HttpResponse('OK')


@override_settings(LOGIN_URL='/login')
class XHRLoginRequiredDecoratorTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/api/test')
        self.request.user = User()
        self.request.session = {}
        UserServiceMiddleware().process_request(self.request)
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(self.request)
        self.request.session.save()

        headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        self.xhr_request = RequestFactory().get('/api/test', **headers)
        self.xhr_request.user = User()
        self.xhr_request.session = {}
        UserServiceMiddleware().process_request(self.xhr_request)
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(self.xhr_request)
        self.xhr_request.session.save()

    def test_xhr_login_required_noheader_noauth(self):
        self.request.user = AnonymousUser()
        view_instance = XHRLoginRequiredView.as_view()
        response = view_instance(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual('/login?next=/api/test', response.url)

    def test_xhr_login_required_noauth(self):
        self.xhr_request.user = AnonymousUser()
        view_instance = XHRLoginRequiredView.as_view()
        response = view_instance(self.xhr_request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b'Invalid session')

    def test_xhr_login_required_auth(self):
        self.xhr_request.user = User()
        view_instance = XHRLoginRequiredView.as_view()
        response = view_instance(self.xhr_request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'OK')
