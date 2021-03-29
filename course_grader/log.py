# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from logging import Filter


class UserFilter(Filter):
    """ Add user information to each log entry. """

    def filter(self, record):
        from userservice.user import UserService
        user_service = UserService()
        try:
            record.user = user_service.get_original_user() or "-"
            record.actas = (user_service.get_user() or "-").lower()
        except Exception as ex:
            record.user = "-"
            record.actas = "-"

        return True


class InfoFilter(Filter):
    """ Limits log level to INFO only. """

    def filter(self, record):
        return record.levelname == "INFO"
