# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.conf import settings
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.utils import timezone
from uw_saml.decorators import group_required
from uw_sws.models import Term
from course_grader.models import SubmittedGradeRoster, GradeImport
from course_grader.dao.term import (
    term_from_param, current_term, current_datetime)
from datetime import datetime, timedelta
from logging import getLogger
import json

logger = getLogger(__name__)


@group_required(settings.GRADEPAGE_SUPPORT_GROUP)
@never_cache
def status(request):
    try:
        curr_term = current_term()
    except Exception as ex:
        logger.error("GET current term failed: {}".format(ex))
        raise

    term_id = request.GET.get("term", "").strip()
    try:
        selected_term = term_from_param(term_id)
    except Exception as ex:
        selected_term = curr_term

    graderosters = SubmittedGradeRoster.objects.get_status_by_term(
        selected_term)

    grade_imports = GradeImport.objects.get_import_sources_by_term(
        selected_term)

    if selected_term.quarter == Term.SUMMER:
        grading_period_open = selected_term.aterm_grading_period_open
    else:
        grading_period_open = selected_term.grading_period_open

    start_date = timezone.make_aware(grading_period_open,
                                     timezone.get_default_timezone())
    end_date = timezone.make_aware(selected_term.grade_submission_deadline,
                                   timezone.get_default_timezone())
    epoch = timezone.make_aware(datetime(1970, 1, 1),
                                timezone.get_default_timezone())

    chart_data = {
        "submissions": {
            "plot_lines": [],
            "grading_period_open": get_total_milliseconds(start_date - epoch),
            "data": []
        },
        "grade_imports": {
            "catalyst": [],
            "canvas": [],
            "csv": [],
        }
    }

    while start_date < end_date:
        if start_date.strftime("%a") == "Mon":
            chart_data["submissions"]["plot_lines"].append({
                "value": get_total_milliseconds(start_date - epoch),
                "color": "#707070",
                "width": 1,
                "dashStyle": "ShortDot"
            })
        start_date = start_date + timedelta(days=1)

    for index, graderoster in enumerate(graderosters):
        chart_data["submissions"]["data"].append([
            get_total_milliseconds(graderoster["submitted_date"] - epoch),
            index + 1
        ])

    for grade_import in grade_imports:
        chart_data["grade_imports"][grade_import["source"]].append([
            get_total_milliseconds(grade_import["imported_date"] - epoch),
            len(chart_data["grade_imports"][grade_import["source"]]) + 1
        ])

    params = {
        "graderosters": graderosters,
        "selected_year": selected_term.year,
        "selected_quarter": selected_term.get_quarter_display(),
        "grading_period_open": grading_period_open,
        "grade_submission_deadline": selected_term.grade_submission_deadline,
        "current_datetime": current_datetime(),
        "chart_data": json.dumps(chart_data),
        "term_id": f"{selected_term.year}-{selected_term.quarter}",
    }
    return render(request, "support/status.html", params)


def get_total_milliseconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e3
