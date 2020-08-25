"""
This module encapsulates the access of sws term data
"""

from django.conf import settings
from uw_sws.term import (
    get_term_by_year_and_quarter, get_term_by_date, get_term_before,
    get_term_after)
from course_grader.dao import current_datetime, datetime_aware
from course_grader.exceptions import InvalidTerm
from datetime import timedelta
import re


def submission_deadline_warning(term):
    hours = getattr(settings, "SUBMISSION_DEADLINE_WARNING_HOURS", 48)
    deadline = datetime_aware(term.grade_submission_deadline)
    warning_start = deadline - timedelta(hours=hours)
    return (current_datetime() >= warning_start)


def is_grading_period_open(term_or_section):
    return True
    try:
        grade_submission_deadline = (
            term_or_section.term.grade_submission_deadline)
        if term_or_section.is_summer_a_term():
            open_date = term_or_section.term.aterm_grading_period_open
        else:
            open_date = term_or_section.term.grading_period_open
    except AttributeError:  # Term
        grade_submission_deadline = term_or_section.grade_submission_deadline
        if term_or_section.is_summer_quarter():
            open_date = term_or_section.aterm_grading_period_open
        else:
            open_date = term_or_section.grading_period_open
    return (datetime_aware(open_date) <= current_datetime() <= datetime_aware(
        grade_submission_deadline))


def is_grading_period_past(term):
    return (term.grade_submission_deadline is None or
            current_datetime() > datetime_aware(
                term.grade_submission_deadline))


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
    if current_datetime() > datetime_aware(term.grade_submission_deadline):
        return get_term_after(term)
    else:
        return term


def previous_gradable_term():
    term = current_term()
    if current_datetime() > datetime_aware(term.grade_submission_deadline):
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


def is_graderoster_available_for_term(section):
    if is_grading_period_open(section):
        return True

    # Return True if the current date is after term.grade_submission_deadline,
    # but on or before the following term.last_day_instruction
    curr_dt = current_datetime()
    if (curr_dt > datetime_aware(section.term.grade_submission_deadline) and
            curr_dt.date() <= get_term_after(
                section.term).last_day_instruction):
        return True

    return False
