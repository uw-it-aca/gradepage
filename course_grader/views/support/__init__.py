# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.conf import settings
from uw_saml.utils import is_member_of_group


def can_override_user(request):
    return is_member_of_group(request, settings.GRADEPAGE_SUPPORT_GROUP)


def can_proxy_restclient(request, service, url):
    return is_member_of_group(request, settings.GRADEPAGE_SUPPORT_GROUP)


def can_manage_persistent_messages(request):
    return is_member_of_group(request, settings.GRADEPAGE_ADMIN_GROUP)
