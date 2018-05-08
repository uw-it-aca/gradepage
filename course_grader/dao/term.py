"""
This module encapsulates the access of sws term data
"""

from django.conf import settings
from uw_sws.term import (
    get_term_by_year_and_quarter, get_term_by_date, get_term_before,
    get_term_after)
from course_grader.dao import current_datetime
from course_grader.exceptions import InvalidTerm
from datetime import timedelta
import re


def submission_deadline_warning(term):
    hours = getattr(settings, "SUBMISSION_DEADLINE_WARNING_HOURS", 48)
    warning_start = term.grade_submission_deadline - timedelta(hours=hours)
    return (current_datetime() >= warning_start)


def term_from_param(param):
    valid = re.compile(r"^2\d{3}-(?:winter|spring|summer|autumn)$", re.I)
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
    for i in range(-1, getattr(settings, "PAST_TERMS_VIEWABLE", 4)):
        terms.append(term)
        term = get_term_before(term)
    return terms
