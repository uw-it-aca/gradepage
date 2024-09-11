<template>
  <template v-if="graderoster.is_submission_confirmation">
    <template v-if="graderoster.has_failed_submissions">

      <!-- warning -->
      <div
        v-if="graderoster.has_successful_submissions"
        class="alert alert-warning"
        role="status"
      >
        <span class=""
          ><i class="fas fa-exclamation-circle"></i>
          {{
            interpolate(
              ngettext(
                "Grades submitted, but one grade had an error.",
                "Grades submitted, but %(failed_submission_count)s grades had errors.",
                graderoster.failed_submission_count
              ),
              graderoster,
              true
            )
          }}
        </span>
      </div>

      <!-- danger -->
      <div v-else class="alert alert-danger" role="status">
        <span class=""
          ><i class="fas fa-times-circle"></i>
          {{
            interpolate(
              ngettext(
                "Grade submitted with error.",
                "Grades submitted with errors.",
                graderoster.failed_submission_count
              ),
              graderoster,
              true
            )
          }}
        </span>
      </div>
    </template>

    <!-- success -->
    <BAlert v-else variant="success" :model-value="true" class="small">
      <i class="bi bi-check-circle-fill me-1"></i>
      {{ gettext("grade_submission_successful") }}
    </BAlert>
  </template>

  <!-- info -->
  <BAlert
    v-else-if="graderoster.has_inprogress_submissions"
    variant="info"
    :model-value="true"
    class="small"
  >
    <i class="bi bi-exclamation-circle-fill me-1"></i>
    {{ gettext("grade_submission_inprogress") }}
    <p>{{ gettext("in_progress_submission_email") }}</p>
    <p>
      {{ gettext("more_grades_to_submit") }}
      <BLink :href="section.term_url">
        {{ gettext("return_classes_to_grade") }}
      </BLink>
    </p>
  </BAlert>

  <!-- success -->
  <BAlert
    v-for="submission in graderoster.submissions"
    variant="success"
    :model-value="true"
    class="small"
  >
    <i class="bi bi-check-circl-fill me-1"></i>
    <span v-if="submission.section_id">
      {{ gettext("section") }} {{ submission.section_id }}:
    </span>
    <strong>{{ submission.submitted_count }}</strong>
    {{ gettext("grades_submitted_to_registrar_by") }}
    <strong>{{ submission.submitted_by }}</strong>
    on {{ formatLongDateTime(submission.submitted_date) }}.
    <BLink
      href="https://itconnect.uw.edu/learn/tools/gradepage/change-submitted-grades/"
      target="_blank"
      title="Change submitted grades"
      >Change submitted grades?
    </BLink>
  </BAlert>

  <!-- info -->
  <BAlert
    v-if="graderoster.is_writing_section"
    variant="info"
    :model-value="true"
    class="small"
  >
    <i class="bi bi-exclamation-circle-fill me-1"></i>
    {{ gettext("writing_course_note_receipt") }}
  </BAlert>

  <!-- warning -->
  <BAlert
    v-if="!graderoster.is_submission_confirmation"
    variant="warning"
    :model-value="true"
    class="small"
  >
    <i class="bi bi-exclamation-triangle-fill me-1"></i>
    {{ gettext("confirmation_alert_warning") }}
    <BLink
      href="https://registrar.washington.edu/staffandfaculty/grading-resources/#faqs"
      target="_blank"
      class="d-print-none"
      >More info.
    </BLink>
  </BAlert>
</template>

<script>
import { formatLongDateTime } from "@/utils/dates";
import { BAlert, BLink } from "bootstrap-vue-next";

export default {
  components: { BAlert, BLink },
  props: {
    section: {
      type: Object,
      required: true,
    },
    graderoster: {
      type: Object,
      required: true,
    },
  },
  setup() {
    return {
      formatLongDateTime,
    };
  },
};
</script>
