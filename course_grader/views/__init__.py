from django.http import HttpResponseRedirect
from django.utils.timezone import get_default_timezone, localtime
from django.utils.timezone import is_naive, make_aware
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


def grade_submission_deadline_params(term):
    return {
        "deadline_year": term.year,
        "deadline_quarter": term.get_quarter_display(),
        "grade_submission_deadline": term.grade_submission_deadline,
        "deadline_warning": submission_deadline_warning(term),
    }
