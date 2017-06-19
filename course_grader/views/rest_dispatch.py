from django.http import HttpResponse
from django.views import View
import json
import re


class RESTDispatch(View):
    def error_response(self, status, message="", content={}):
        content["error"] = message
        return HttpResponse(json.dumps(content),
                            status=status,
                            content_type="application/json")

    def json_response(self, content="", status=200):
        return HttpResponse(json.dumps(content),
                            status=status,
                            content_type="application/json")

    def csv_response(self, status=200, filename="file"):
        response = HttpResponse(status=status,
                                content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="%s.csv"' % (
            re.sub(r"[,/]", "-", filename))
        return response
