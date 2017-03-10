from django.conf import settings
from django.template import loader
from django.utils.translation import ungettext, ugettext
from django.contrib.humanize.templatetags.humanize import apnumber
from course_grader.dao.section import section_url_token, section_display_name
from course_grader.dao.person import person_display_name
from course_grader.dao import current_datetime, display_datetime


def submission_message(graderoster, submitter):
    section = getattr(graderoster, "secondary_section", None)
    if section is None:
        section = graderoster.section

    section_id = section_url_token(section, graderoster.instructor)
    section_name = section_display_name(section)
    submitter_name = person_display_name(submitter)

    success_count = 0
    error_count = 0
    for item in graderoster.items:
        if (not item.is_auditor and item.date_withdrawn is None and
                item.status_code is not None):
            if item.status_code != "200":
                error_count += 1
            else:
                success_count += 1

    if success_count > 0 and error_count > 0:
        subject = ugettext(
            "email_subject_submission_failure %(section)s"
        ) % {"section": section_name}
        text_template = "email/partial.txt"
        html_template = "email/partial.html"
    elif success_count == 0 and error_count > 0:
        subject = ugettext(
            "email_subject_submission_failure %(section)s"
        ) % {"section": section_name}
        text_template = "email/failure.txt"
        html_template = "email/failure.html"
    elif success_count > 0 and error_count == 0:
        subject = ungettext(
            "email_subject_submission_success %(name)s %(count)s %(section)s",
            "email_subject_submissions_success %(name)s %(count)s %(section)s",
            success_count) % {"count": apnumber(success_count),
                              "name": submitter_name,
                              "section": section_name}
        text_template = "email/success.txt"
        html_template = "email/success.html"
    else:
        raise Exception("No grades were submitted")

    gradepage_host = getattr(settings, "GRADEPAGE_HOST", "http://localhost")
    params = {
        "submitted_by": submitter_name,
        "submitted_date": display_datetime(current_datetime()),
        "submitted_count": success_count + error_count,
        "success_count": success_count,
        "failure_count": error_count,
        "section_name": section_name,
        "gradepage_url": gradepage_host,
        "section_url": "%s/section/%s" % (gradepage_host, section_id),
        "grading_window_open": section.term.is_grading_period_open(),
    }

    if params["grading_window_open"]:
        deadline = section.term.grade_submission_deadline
        params["grade_submission_deadline"] = display_datetime(deadline)

    return (subject,
            loader.render_to_string(text_template, params),
            loader.render_to_string(html_template, params))
