# Copyright 2026 UWIT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from abc import ABC, abstractmethod
from datetime import datetime

from django.conf import settings
from django.utils.timezone import get_default_timezone, is_naive, localtime, make_aware
from uw_sws import SWS_DAO, sws_now


def __update_get(self, url, response):
    pass


# Replace the SWS _update_get method to prevent tampering with mocked resources
SWS_DAO._update_get = __update_get


def current_datetime():
    override_dt = getattr(settings, "CURRENT_DATETIME_OVERRIDE", None)
    if override_dt is not None:
        return datetime.strptime(override_dt, "%Y-%m-%d %H:%M:%S")  # noqa: DTZ007
    else:
        return sws_now()


def display_datetime(dt):
    if is_naive(dt):
        dt = make_aware(dt, get_default_timezone())
    else:
        dt = localtime(dt)

    return dt.strftime("%B %d at %l:%M %p %Z")


class GradeImportSource(ABC):
    true_values = ["1", "y", "yes", "t", "true"]

    @abstractmethod
    def grades_for_section(self, section, instructor, **kwargs):
        pass

    def is_true(self, val):
        return (val is not None and val.lower() in self.true_values)

    def get_filepath(self):
        return getattr(self, "filepath", None)
