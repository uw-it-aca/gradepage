from django.http import HttpResponseRedirect
from django.utils.timezone import (
    get_default_timezone, localtime, is_naive, make_aware)
from django.utils.translation import ugettext as _
from course_grader.dao.term import submission_deadline_warning
from nameparser import HumanName
from datetime import datetime
import re


def user_login(request):
    return HttpResponseRedirect(request.GET.get('next', '/'))


def section_url_token(section, instructor):
    return "-".join([str(section.term.year), section.term.quarter,
                     section.curriculum_abbr, section.course_number,
                     section.section_id, instructor.uwregid])


def clean_section_id(section_id):
    """ Returns a section_id suitable for use in html ids and jquery selectors.
    """
    return re.sub(r"[\s&]", "_", section_id)


def url_for_term(term):
    return "/?term=%s-%s" % (term.year, term.quarter)


def display_datetime(datetime):
    if is_naive(datetime):
        datetime = make_aware(datetime, get_default_timezone())
    else:
        datetime = localtime(datetime)
    return datetime.strftime("%B %d at %l:%M %p %Z")


def display_person_name(person):
    if (person.display_name is not None and len(person.display_name) and
            not person.display_name.isupper()):
        name = person.display_name
    else:
        name = HumanName("%s %s" % (person.first_name, person.surname))
        name.capitalize()
        name.string_format = "{first} {last}"
    return unicode(name)


def display_section_name(section):
    return " ".join([section.curriculum_abbr, section.course_number,
                     section.section_id])


def section_status_params(section, instructor):
    section_id = section_url_token(section, instructor)
    grading_period_open = section.is_grading_period_open()
    submission_deadline = section.term.grade_submission_deadline.isoformat()

    if section.is_independent_study:
        display_name = "%s (%s)" % (display_section_name(section),
                                    display_person_name(instructor))
    else:
        display_name = display_section_name(section)

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
        elif (not section.is_primary_section and not
                section.allows_secondary_grading):
            data["section_url"] = "/section/%s" % section_id
        else:
            data["section_url"] = "/section/%s" % section_id
            data["status_url"] = "/api/v1/grading_status/%s" % section_id
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
