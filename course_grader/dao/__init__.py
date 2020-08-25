from django.conf import settings
from django.utils.timezone import (
    get_default_timezone, localtime, is_naive, make_aware)
from datetime import datetime
from uw_sws import SWS_DAO


def __update_get(self, url, response):
    pass


# Replace the SWS _update_get method to prevent tampering with mocked resources
SWS_DAO._update_get = __update_get


def current_datetime():
    override_dt = getattr(settings, "CURRENT_DATETIME_OVERRIDE", None)
    if override_dt is not None:
        now_dt = datetime.strptime(override_dt, "%Y-%m-%d %H:%M:%S")
    else:
        now_dt = datetime.now()
    return datetime_aware(now_dt)


def datetime_aware(dt):
    if is_naive(dt):
        return make_aware(dt, get_default_timezone())
    return localtime(dt)


def display_datetime(dt):
    if is_naive(dt):
        dt = make_aware(dt, get_default_timezone())
    else:
        dt = localtime(dt)
    return dt.strftime("%B %d at %l:%M %p %Z")
