"""
This module encapsulates the access of sws term data
"""

from django.conf import settings
from restclients.sws.term import get_term_by_year_and_quarter, get_term_by_date
from restclients.sws.term import get_term_before, get_term_after
from course_grader.exceptions import InvalidTerm
from datetime import datetime, timedelta
import re


def current_datetime():
    override_dt = getattr(settings, "CURRENT_DATETIME_OVERRIDE", None)
    if override_dt is not None:
        return datetime.strptime(override_dt, "%Y-%m-%d %H:%M:%S")
    else:
        return datetime.now()


def submission_deadline_warning(term):
    hours = getattr(settings, "SUBMISSION_DEADLINE_WARNING_HOURS", 48)
    warning_start = term.grade_submission_deadline - timedelta(hours=hours)
    return (current_datetime() >= warning_start)


def term_from_param(param):
    valid = re.compile("^2\d{3}-(?:winter|spring|summer|autumn)$")
    if not valid.match(param):
        raise InvalidTerm()
    (year, quarter) = param.split("-")
    return get_term_by_year_and_quarter(year, quarter)


def term_from_date(date):
    return get_term_by_date(date)


def current_term():
    return term_from_date(current_datetime().date())


def next_gradable_term():
    term = current_term()
    if current_datetime() > term.grade_submission_deadline:
        return get_term_after(term)
    else:
        return term


def previous_gradable_term():
    term = current_term()
    if current_datetime() > term.grade_submission_deadline:
        return term
    else:
        return get_term_before(term)


def all_viewable_terms():
    term = current_term()
    terms = []
    for i in range(-1, settings.PAST_TERMS_VIEWABLE):
        terms.append(term)
        term = get_term_before(term)
    return terms
