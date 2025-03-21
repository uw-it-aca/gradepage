# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from course_grader.dao import current_datetime, display_datetime
from course_grader.dao.term import (
    next_gradable_term, previous_gradable_term, submission_deadline_warning,
    is_grading_period_open)
from persistent_message.models import Message


def get_open_grading_messages(term, params={}):
    tags = ["is_open"]
    rel_grade_submission_deadline = ""
    if submission_deadline_warning(term):
        tags.append("just_before_deadline")
        delta = term.grade_submission_deadline - current_datetime()
        seconds_remaining = (delta.days * 24 * 3600) + delta.seconds
        if seconds_remaining < (17 * 3600):
            rel_grade_submission_deadline = "5:00 PM today"
        elif seconds_remaining < (41 * 3600):
            rel_grade_submission_deadline = "5:00 PM tomorrow"

    params.update({
        "year": term.year,
        "quarter": term.get_quarter_display(),
        "grade_submission_deadline": term.grade_submission_deadline,
        "rel_grade_submission_deadline": rel_grade_submission_deadline,
    })
    return _get_persistent_messages(tags, params)


def get_closed_grading_messages(params={}):
    prev_term = previous_gradable_term()
    next_term = next_gradable_term()

    if next_term.quarter == next_term.SUMMER:
        next_open_date = next_term.aterm_grading_period_open
    else:
        next_open_date = next_term.grading_period_open

    params.update({
        "prev_year": prev_term.year,
        "prev_quarter": prev_term.get_quarter_display(),
        "prev_window_close_date": display_datetime(
            prev_term.grade_submission_deadline),
        "next_year": next_term.year,
        "next_quarter": next_term.get_quarter_display(),
        "next_window_open_date": display_datetime(next_open_date),
        "grade_submission_deadline": prev_term.grade_submission_deadline,
    })

    if (next_term.first_day_quarter < current_datetime().date()):
        tags = ["is_closed"]
    else:
        tags = ["just_after_deadline"]

    return _get_persistent_messages(tags, params)


def get_messages_for_term(term, params={}):
    if is_grading_period_open(term):
        return get_open_grading_messages(term, params)
    else:
        return get_closed_grading_messages(params)


def _get_persistent_messages(tags, params):
    ret = {"messages": []}
    for message in Message.objects.active_messages(tags=tags):
        if "message_level" not in ret:
            ret["message_level"] = message.get_level_display().lower()
        ret["messages"].append(message.render(params))
    return ret
