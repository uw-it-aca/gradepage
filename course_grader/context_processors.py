# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.conf import settings
from django.urls import reverse
from userservice.user import UserService
from course_grader.dao.person import person_from_user, person_display_name


def user(request):
    try:
        user_fullname = person_display_name(person_from_user())
    except Exception as ex:
        user_fullname = None

    user_service = UserService()
    return {
        "user_login": user_service.get_user(),
        "user_fullname": user_fullname,
        "override_user": user_service.get_override_user(),
        'signout_url': reverse('saml_logout'),
    }


def debug_mode(request):
    return {"debug_mode": settings.DEBUG}
