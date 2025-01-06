# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.utils.decorators import method_decorator
from course_grader.views.decorators import xhr_login_required
from course_grader.dao.person import person_from_user
from course_grader.dao.term import all_viewable_terms
from course_grader.models import GradeImport, ImportConversion
from course_grader.views.api import GradeFormHandler
from course_grader.exceptions import *
from logging import getLogger

logger = getLogger(__name__)


@method_decorator(xhr_login_required, name='dispatch')
class ConversionScales(GradeFormHandler):
    def get(self, request, *args, **kwargs):
        try:
            self.user = person_from_user()
            self.all_terms = all_viewable_terms()
            self.scale = ImportConversion.valid_scale(
                kwargs.get("scale", "").strip())
        except InvalidUser as ex:
            return self.error_response(401, "{}".format(ex))
        except InvalidGradingScale as ex:
            return self.error_response(400, "{}".format(ex))
        except Exception as ex:
            logger.error("GET terms failed: {}".format(ex))
            return self.error_response(500, "{}".format(ex))

        return self.response_content()

    def response_content(self):
        imports = GradeImport.objects.get_imports_by_person(self.user)

        section_ids = set()
        return_data = []
        for term in self.all_terms:
            conversions_in_term = []
            for grade_import in imports:
                if grade_import.term_id != term.term_label():
                    # Wrong term
                    continue

                if grade_import.import_conversion is None:
                    # Missing conversion data
                    continue

                conversion_data = grade_import.import_conversion.json_data()

                if (self.scale is not None and
                        self.scale != conversion_data["scale"]):
                    # Wrong scale type
                    continue

                if grade_import.section_id not in section_ids:
                    section_ids.add(grade_import.section_id)

                    conversion_data["section_id"] = grade_import.section_id

                    parts = grade_import.section_id.split("-")
                    conversion_data["section"] = " ".join(parts[2:5])

                    conversions_in_term.append(conversion_data)

            if len(conversions_in_term):
                return_data.append({
                    "quarter": term.get_quarter_display(),
                    "year": term.year,
                    "conversion_scales": conversions_in_term,
                })

        return self.json_response({"terms": return_data, "scale": self.scale})
