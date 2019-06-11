from django.http import HttpResponse
from django.views import View
import json
import re

timeout_error = ("The request to the student information system has timed "
                 "out. Please try again.")


class RESTDispatch(View):
    @staticmethod
    def data_failure_error(ex):
        return (543, timeout_error) if (
            ex.status == 0) else (ex.status, ex.msg)

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
    def csv_response(status=200, filename="file"):
        response = HttpResponse(status=status,
                                content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="{}.csv"').format(
                re.sub(r"[,/]", "-", filename))
        return response
