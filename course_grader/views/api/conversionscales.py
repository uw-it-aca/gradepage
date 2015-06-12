from django.db.models import Max, F
from django.utils.translation import ugettext as _
from course_grader.dao.person import person_from_user
from course_grader.dao.term import all_viewable_terms
from course_grader.models import GradeImport, ImportConversion
from course_grader.views.api import GradeFormHandler
from course_grader.exceptions import *
import logging


logger = logging.getLogger(__name__)


class ConversionScales(GradeFormHandler):
    def run(self, *args, **kwargs):
        request = args[0]
        try:
            self.user = person_from_user()
            self.all_terms = all_viewable_terms()

        except InvalidUser as ex:
            return self.error_response(403, _("grading_not_permitted"))
        except Exception as ex:
            logger.exception(ex)
            return self.error_response(500, "%s" % ex)

        return self.run_http_method(*args, **kwargs)

    def GET(self, request, **kwargs):
        self.scale = kwargs.get("scale", "").lower()

        if self.scale not in dict(ImportConversion.SCALE_CHOICES):
            return self.error_response(400, "Invalid scale")

        return self.response_content()

    def response_content(self):
        grade_imports = GradeImport.objects.filter(
            imported_by=self.user.uwregid,
            import_conversion__isnull=False,
        ).order_by("section_id", "-imported_date")

        seen_sections = {}
        return_data = []
        for term in self.all_terms:
            conversions_in_term = []
            for grade_import in grade_imports:
                if grade_import.term_id != term.term_label():
                    # Wrong term
                    continue

                conversion_data = grade_import.import_conversion.json_data()

                if (self.scale is not None
                        and self.scale != conversion_data["scale"]):
                    # Wrong scale type
                    continue

                if grade_import.section_id in seen_sections:
                    # Already seen a scale for this section
                    continue

                conversion_data["section_id"] = grade_import.section_id

                parts = grade_import.section_id.split("-")
                conversion_data["section"] = " ".join(parts[2:5])

                seen_sections[grade_import.section_id] = True
                conversions_in_term.append(conversion_data)

            if len(conversions_in_term):
                return_data.append({
                    "quarter": term.get_quarter_display(),
                    "year": term.year,
                    "conversion_scales": conversions_in_term,
                })

        return self.json_response({"terms": return_data, "scale": self.scale})
