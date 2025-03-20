# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.http import HttpResponse
from django.views import View
import json
import re

timeout_error = ("The request to the student information system has timed "
                 "out. Please try again.")


class RESTDispatch(View):
    @staticmethod
    def data_failure_error(ex):
        status = 404 if ex.status == 404 else 543
        msg = timeout_error if ex.status == 0 else ex.msg
        return (status, msg)

    @staticmethod
    def error_response(status, message="", content={}):
        content["error"] = str(message)
        return HttpResponse(json.dumps(content),
                            status=status,
                            content_type='application/json')

    @staticmethod
    def json_response(content="", status=200):
        return HttpResponse(json.dumps(content, sort_keys=True),
                            status=status,
                            content_type="application/json")

    @staticmethod
    def csv_response(content="", status=200, filename="file"):
        response = HttpResponse(content=content,
                                status=status,
                                content_type="text/csv")

        if not filename.lower().endswith(".csv"):
            filename += ".csv"

        response["Content-Disposition"] = (
            'attachment; filename="{}"').format(re.sub(r"[,/]", "-", filename))

        return response

    @staticmethod
    def xml_response(content="", status=200, filename="file"):
        response = HttpResponse(content=content,
                                status=status,
                                content_type="application/xhtml+xml")

        if not filename.lower().endswith(".xhtml"):
            filename += ".xhtml"

        response["Content-Disposition"] = (
            'attachment; filename="{}"').format(re.sub(r"[,/]", "-", filename))

        return response
