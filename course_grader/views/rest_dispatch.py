from django.http import HttpResponse
from django.views import View
import json
import re


class RESTDispatch(View):
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
