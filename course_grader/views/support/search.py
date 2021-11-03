# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from django.urls import reverse
from uw_saml.decorators import group_required
from uw_sws import QUARTER_SEQ
from uw_sws.term import get_term_by_year_and_quarter
from uw_sws.models import Term
from restclients_core.exceptions import DataFailureException, InvalidNetID
from course_grader.models import SubmittedGradeRoster, GradeImport
from course_grader.dao.person import (
    person_from_netid, person_from_regid, person_display_name)
from logging import getLogger
import re

logger = getLogger(__name__)


@group_required(settings.GRADEPAGE_SUPPORT_GROUP)
@never_cache
def grade_imports(request):
    all_terms = find_all_terms()
    selected_term = term_from_param(request, all_terms)

    opt_terms = []
    for opt_term in all_terms:
        opt_terms.append({
            "quarter": opt_term.get_quarter_display(),
            "year": opt_term.year,
            "value": "{year}-{quarter}".format(
                year=opt_term.year, quarter=opt_term.quarter),
            "is_selected": opt_term == selected_term,
        })

    curr_abbr = request.GET.get("curriculum_abbr", "").strip().upper()
    course_num = request.GET.get("course_num", "").strip()
    submitter_netid = request.GET.get("submitter", "").strip().lower()

    params = {
        "grade_imports": [],
        "terms": opt_terms,
        "selected_year": selected_term.year,
        "selected_quarter": selected_term.get_quarter_display(),
        "grading_period_open": selected_term.grading_period_open,
        "grade_submission_deadline": selected_term.grade_submission_deadline,
        "curriculum_abbr": curr_abbr,
        "course_num": course_num,
        "submitter": submitter_netid,
        "errors": {},
    }

    template = "support/imports.html"
    if not len(request.GET):
        return render(request, template, params)

    args = ()
    kwargs = {"term_id": selected_term.term_label()}
    if re.match(r"^[\w& ]+$", curr_abbr):
        s_filter = [str(selected_term.year), selected_term.quarter, curr_abbr]
        if re.match(r"^\d{3}$", course_num):
            s_filter.append(course_num)
        elif len(course_num):
            params["errors"]["course_num"] = "Invalid"

        kwargs["section_id__startswith"] = "-".join(s_filter)
    elif len(curr_abbr):
        params["errors"]["curriculum_abbr"] = "Invalid"
    else:
        params["errors"]["curriculum_abbr"] = "Required"

    if len(submitter_netid):
        try:
            submitter = person_from_netid(submitter_netid)
            kwargs["imported_by"] = submitter.uwregid
            if not len(curr_abbr):
                params["errors"].pop("curriculum_abbr", None)
        except (DataFailureException, InvalidNetID) as err:
            params["errors"]["submitter"] = err.msg if (
                hasattr(err, "msg")) else err

    if len(params["errors"]):
        return render(request, template, params)

    grade_imports = GradeImport.objects.filter(*args, **kwargs)

    people = {}
    for grade_import in grade_imports:
        data = grade_import.json_data()

        (year, quarter, curriculum_abbr, course_number, section_id,
            instructor_reg_id) = grade_import.section_id.split("-")

        if grade_import.imported_by not in people:
            person = person_from_regid(grade_import.imported_by)
            people[grade_import.imported_by] = person
        if instructor_reg_id not in people:
            person = person_from_regid(instructor_reg_id)
            people[instructor_reg_id] = person

        importer_name = person_display_name(people[grade_import.imported_by])
        instructor_name = person_display_name(people[instructor_reg_id])

        if grade_import.file_path:
            data["file_url"] = reverse("grade-import-file", kwargs={
                "section_id": grade_import.section_id,
                "import_id": grade_import.pk})

        data["section_name"] = " ".join([curriculum_abbr, course_number,
                                         section_id])
        data["importer_name"] = importer_name
        data["importer_netid"] = people[grade_import.imported_by].uwnetid
        data["instructor_name"] = instructor_name
        data["imported_date"] = grade_import.imported_date
        params["grade_imports"].append(data)

    return render(request, template, params)


@group_required(settings.GRADEPAGE_ADMIN_GROUP)
@never_cache
def graderosters(request):
    all_terms = find_all_terms()
    selected_term = term_from_param(request, all_terms)

    opt_terms = []
    for opt_term in all_terms:
        opt_terms.append({
            "quarter": opt_term.get_quarter_display(),
            "year": opt_term.year,
            "value": "{year}-{quarter}".format(
                year=opt_term.year, quarter=opt_term.quarter),
            "is_selected": opt_term == selected_term,
        })

    curr_abbr = request.GET.get("curriculum_abbr", "").strip().upper()
    course_num = request.GET.get("course_num", "").strip()
    submitter_netid = request.GET.get("submitter", "").strip().lower()
    unsubmitted_only = request.GET.get("unsubmitted", False)

    params = {
        "graderosters": [],
        "terms": opt_terms,
        "selected_year": selected_term.year,
        "selected_quarter": selected_term.get_quarter_display(),
        "grading_period_open": selected_term.grading_period_open,
        "grade_submission_deadline": selected_term.grade_submission_deadline,
        "curriculum_abbr": curr_abbr,
        "course_num": course_num,
        "submitter": submitter_netid,
        "unsubmitted": unsubmitted_only,
        "errors": {},
    }

    template = "support/search.html"
    if not len(request.GET):
        return render(request, template, params)

    kwargs = {"term_id": selected_term.term_label()}

    if re.match(r"^[\w& ]+$", curr_abbr):
        s_filter = [str(selected_term.year), selected_term.quarter, curr_abbr]
        if re.match(r"^\d{3}$", course_num):
            s_filter.append(course_num)
        elif len(course_num):
            params["errors"]["course_num"] = "Invalid"

        kwargs["section_id__startswith"] = ",".join(s_filter)
    elif len(curr_abbr):
        params["errors"]["curriculum_abbr"] = "Invalid"
    else:
        params["errors"]["curriculum_abbr"] = "Required"

    if len(submitter_netid):
        try:
            submitter = person_from_netid(submitter_netid)
            args = (Q(submitted_by=submitter.uwregid) |
                    Q(instructor_id=submitter.uwregid),)
            if not len(curr_abbr):
                params["errors"].pop("curriculum_abbr", None)
        except (DataFailureException, InvalidNetID) as err:
            params["errors"]["submitter"] = err.msg if (
                hasattr(err, "msg")) else err
    else:
        args = ()

    if unsubmitted_only:
        # Missing curr_abbr is ok
        if not len(curr_abbr):
            params["errors"].pop("curriculum_abbr", None)
        kwargs["accepted_date__isnull"] = True

    if len(params["errors"]):
        return render(request, template, params)

    graderosters = SubmittedGradeRoster.objects.filter(
        *args, **kwargs).defer("document")

    submitted_dates = {}
    people = {}
    for graderoster in graderosters:
        if graderoster.secondary_section_id is not None:
            sid = graderoster.secondary_section_id
        else:
            sid = graderoster.section_id

        (course_id, section_id) = sid.split("/")
        (year, quarter, curriculum_abbr, course_number) = course_id.split(",")
        section_name = " ".join([curriculum_abbr, course_number, section_id])

        if graderoster.instructor_id not in people:
            person = person_from_regid(graderoster.instructor_id)
            people[graderoster.instructor_id] = person
        if graderoster.submitted_by not in people:
            person = person_from_regid(graderoster.submitted_by)
            people[graderoster.submitted_by] = person

        params["graderosters"].append({
            "id": graderoster.pk,
            "section_id": sid,
            "section_name": section_name,
            "instructor": person_display_name(
                people[graderoster.instructor_id]),
            "submitted_date": graderoster.submitted_date,
            "submitted_by": person_display_name(
                people[graderoster.submitted_by]),
            "submitter_netid": people[graderoster.submitted_by].uwnetid,
            "status_code": graderoster.status_code or "200",
            "chart_data": [],
        })

        submitted_date_str = graderoster.submitted_date.replace(
            minute=0, second=0).isoformat()

        if submitted_date_str in submitted_dates:
            submitted_dates[submitted_date_str] += 1
        else:
            submitted_dates[submitted_date_str] = 1

    chart_data = []
    for k, v in sorted(submitted_dates.items()):
        chart_data.append([k, v])
    params["chart_data"] = chart_data

    return render(request, template, params)


def find_all_terms():
    all_terms = []
    for term in SubmittedGradeRoster.objects.get_all_terms():
        (year, quarter) = term.split(",")
        all_terms.append(Term(year=int(year), quarter=quarter))

    all_terms.sort(key=lambda t: (t.year, QUARTER_SEQ.index(t.quarter)),
                   reverse=True)

    return all_terms


def term_from_param(request, all_terms):
    term_id = request.GET.get("term", "").strip()
    try:
        (year, quarter) = term_id.split("-")
        selected_term = Term(year=int(year), quarter=quarter)
        if selected_term not in all_terms:
            return all_terms[0]
    except Exception:
        return all_terms[0]

    try:
        return get_term_by_year_and_quarter(selected_term.year,
                                            selected_term.quarter)
    except Exception as ex:
        logger.error("GET term failed: {}".format(ex))
        raise
