# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse


def xhr_login_required(view_func):
    """
    A login_required decorator for API views that handle
    asynchronous requests.
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        requested_with = request.META.get('HTTP_X_REQUESTED_WITH', '')
        if requested_with == 'XMLHttpRequest':
            return HttpResponse(content='Invalid session', status=403)

        return redirect_to_login(request.path)

    return wrapper
