from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.contrib.humanize.templatetags.humanize import apnumber
from course_grader.dao.section import section_url_token, section_display_name
from course_grader.dao.person import person_from_regid, person_display_name
from course_grader.dao import current_datetime, display_datetime
from course_grader.exceptions import GradesNotSubmitted
from logging import getLogger

logger = getLogger(__name__)


def create_recipient_list(people):
    recipients = []
    for person in people.values():
        recipients.append("{}@uw.edu".format(person.uwnetid))
    return recipients


def create_message(graderoster, submitter):
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
        subject = "Failed grade submission attempt for {}".format(section_name)
        text_template = "email/partial.txt"
        html_template = "email/partial.html"
    elif success_count == 0 and error_count > 0:
        subject = "Failed grade submission attempt for {}".format(section_name)
        text_template = "email/failure.txt"
        html_template = "email/failure.html"
    elif success_count > 0 and error_count == 0:
        if success_count == 1:
            subject = "{} submitted {} grade for {}".format(
                submitter_name, apnumber(success_count), section_name)
        else:
            subject = "{} submitted {} grades for {}".format(
                submitter_name, apnumber(success_count), section_name)
        text_template = "email/success.txt"
        html_template = "email/success.html"
    else:
        raise GradesNotSubmitted()

    gradepage_host = getattr(settings, "GRADEPAGE_HOST", "http://localhost")
    params = {
        "submitted_by": submitter_name,
        "submitted_date": display_datetime(current_datetime()),
        "submitted_count": success_count + error_count,
        "success_count": success_count,
        "failure_count": error_count,
        "section_name": section_name,
        "gradepage_url": gradepage_host,
        "section_url": "{host}/section/{section_id}".format(
            host=gradepage_host, section_id=section_id),
        "grading_window_open": section.term.is_grading_period_open(),
    }

    if params["grading_window_open"]:
        deadline = section.term.grade_submission_deadline
        params["grade_submission_deadline"] = display_datetime(deadline)

    return (subject,
            loader.render_to_string(text_template, params),
            loader.render_to_string(html_template, params))


def graderoster_people(graderoster):
    people = {graderoster.instructor.uwregid: graderoster.instructor}

    for person in graderoster.authorized_grade_submitters:
        people[person.uwregid] = person

    for delegate in graderoster.grade_submission_delegates:
        people[delegate.person.uwregid] = delegate.person

    return people


def notify_grade_submitters(graderoster, submitter_regid):
    people = graderoster_people(graderoster)

    if submitter_regid in people:
        submitter = people[submitter_regid]
    else:
        submitter = person_from_regid(submitter_regid)

    (subject, text_body, html_body) = create_message(graderoster, submitter)
    sender = getattr(settings, "EMAIL_NOREPLY_ADDRESS")
    recipients = create_recipient_list(people)

    message = EmailMultiAlternatives(subject, text_body, sender, recipients)
    message.attach_alternative(html_body, "text/html")

    section = getattr(graderoster, "secondary_section", None)
    if section is None:
        section = graderoster.section
    section_id = section.section_label()

    try:
        message.send()
        log_message = "Submission email sent"
    except Exception as ex:
        log_message = "Submission email failed: {}".format(ex)

    for recipient in recipients:
        logger.info("{}, To: {}, Section: {}, Status: {}".format(
            log_message, recipient, section_id, subject))
