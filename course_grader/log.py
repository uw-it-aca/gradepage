# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from logging import Filter


class UserFilter(Filter):
    """ Add user information to each log entry. """

    def filter(self, record):
        try:
            from userservice.user import UserService
            user_service = UserService()
            record.user = user_service.get_original_user() or "-"
            record.actas = (user_service.get_user() or "-").lower()
        except Exception as ex:
            record.user = "-"
            record.actas = "-"

        return True
