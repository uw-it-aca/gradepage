from django.conf import settings
from django.utils.timezone import (
    get_default_timezone, localtime, is_naive, make_aware)
from datetime import datetime


def current_datetime():
    override_dt = getattr(settings, "CURRENT_DATETIME_OVERRIDE", None)
    if override_dt is not None:
        return datetime.strptime(override_dt, "%Y-%m-%d %H:%M:%S")
    else:
        return datetime.now()


def display_datetime(dt):
    if is_naive(dt):
        dt = make_aware(dt, get_default_timezone())
    else:
        dt = localtime(dt)
    return dt.strftime("%B %d at %l:%M %p %Z")
