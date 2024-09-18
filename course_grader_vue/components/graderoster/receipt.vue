<template>
  <template v-if="graderoster.is_submission_confirmation">
    <template v-if="graderoster.has_failed_submissions">
      <!-- warning -->
      <BAlert
        v-if="graderoster.has_successful_submissions"
        variant="warning"
        :model-value="true"
        class="small"
      >
        <i class="bi bi-exclamation-triangle-fill me-1"></i>
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
      </BAlert>

      <!-- danger -->
      <BAlert v-else variant="danger" :model-value="true" class="small">
        <i class="bi bi-exclamation-octagon-fill me-1"></i>
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
      </BAlert>
    </template>

    <!-- success -->
    <BAlert v-else variant="success" :model-value="true" class="small">
      <i class="bi bi-check-circle-fill me-1"></i>
      {{ gettext("grade_submission_successful") }}
    </BAlert>
  </template>

  <!-- success -->
  <BAlert
    v-for="submission in graderoster.submissions"
    variant="success"
    :model-value="true"
    class="small"
  >
    <i class="bi bi-check-circle-fill me-1"></i>
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
