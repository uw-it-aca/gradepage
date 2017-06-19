from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from course_grader.dao import display_datetime
from course_grader.dao.person import person_display_name
from course_grader.dao.section import section_url_token, section_display_name
from course_grader.dao.term import submission_deadline_warning
import re


def user_login(request):
    return HttpResponseRedirect(request.GET.get('next', '/'))


def clean_section_id(section_id):
    """ Returns a section_id suitable for use in html ids and jquery selectors.
    """
    return re.sub(r"[\s&]", "_", section_id)


def url_for_term(term):
    return "/?term=%s-%s" % (term.year, term.quarter)


def url_for_section(section_id):
    return "%s/section/%s" % (
        getattr(settings, "GRADEPAGE_HOST", ""), section_id)


def url_for_grading_status(section_id):
    return "%s/api/v1/grading_status/%s" % (
        getattr(settings, "GRADEPAGE_HOST", ""), section_id)


def section_status_params(section, instructor):
    section_id = section_url_token(section, instructor)
    grading_period_open = section.is_grading_period_open()
    submission_deadline = section.term.grade_submission_deadline.isoformat()

    if section.is_independent_study:
        display_name = section_display_name(section, instructor)
    else:
        display_name = section_display_name(section)

    data = {
        "section_id": clean_section_id(section_id),
        "display_name": display_name,
        "section_url": None,
        "status_url": None,
        "grading_status": None,
        "grading_period_open": grading_period_open,
        "grade_submission_deadline": submission_deadline,
    }

    if (grading_period_open or section.term.is_grading_period_past()):
        if (section.is_primary_section and section.allows_secondary_grading):
            data["grading_status"] = _("secondary_grading_status")
        else:
            data["section_url"] = url_for_section(section_id)
            data["status_url"] = url_for_grading_status(section_id)
    elif section.is_full_summer_term():
        data["grading_status"] = _(
            "summer_full_term_grade_submission_opens %(date)s"
        ) % {
            "date": display_datetime(section.term.grading_period_open)
        }

    return data


def grade_submission_deadline_params(term):
    return {
        "deadline_year": term.year,
        "deadline_quarter": term.get_quarter_display(),
        "grade_submission_deadline": term.grade_submission_deadline,
        "deadline_warning": submission_deadline_warning(term),
    }
