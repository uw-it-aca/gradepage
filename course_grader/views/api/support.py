# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.conf import settings
from django.utils.decorators import method_decorator
from uw_saml.decorators import group_required
from userservice.user import UserService
from course_grader.views.rest_dispatch import RESTDispatch
from logging import getLogger

logger = getLogger(__name__)


@method_decorator(group_required(settings.GRADEPAGE_SUPPORT_GROUP),
                  name='dispatch')
class UserOverride(RESTDispatch):
    def post(self, request, *args, **kwargs):
        if "clear_override" in request.data:
            us = UserService()
            logger.info("{} is ending impersonation of {}".format(
                        us.get_original_user(), us.get_override_user()))
            us.clear_override()
        return self.json_response({})
