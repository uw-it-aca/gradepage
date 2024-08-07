<template>
  <div v-if="graderoster.is_submission_confirmation">
    <div v-if="graderoster.has_failed_submissions">
      <div v-if="graderoster.has_successful_submissions"
        class="alert alert-warning" role="status">
        <span class=""><i class="fas fa-exclamation-circle"></i>
          {{ ngettext("Grades submitted, but one grade had an error.",
                      "Grades submitted, but %(failed_submission_count)s grades had errors.",
                      graderoster.failed_submission_count) }}
        </span>
      </div>
      <div v-else class="alert alert-danger" role="status">
        <span class=""><i class="fas fa-times-circle"></i>
          {{ ngettext("Grade submitted with error.",
                      "Grades submitted with errors.",
                      graderoster.failed_submission_count) }}
        </span>
      </div>
    </div>
    <div v-else class="alert alert-success" role="status">
      <span class=""><i class="fas fa-check-circle"></i>
        {{ gettext("grade_submission_successful") }}
      </span>
    </div>
  </div>
  <div v-else-if="graderoster.has_inprogress_submissions"
    class="alert alert-info" role="status">
    <span><i class="fas fa-refresh"></i>
      {{ gettext("grade_submission_inprogress") }}</span>
      <p>{{ gettext("in_progress_submission_email") }}</p>
  </div>

  <p>{{ gettext("more_grades_to_submit") }}
    <a href="/">{{ gettext("return_classes_to_grade") }}</a>
  </p>

  <div v-for="submission in graderoster.submissions" role="status">
    <span>
      <i class="fas fa-check-circle" style="color:#63AD45;"></i>
      <span v-if="submission.section_id">
        {{ gettext("section") }} {{ submission.section_id }}:
      </span>
      <strong>{{ submission.submitted_count }}</strong>
      {{ gettext("grades_submitted_to_registrar_by") }}
      <strong>{{ submission.submitted_by}}</strong>
      on {{ formatLongDateTime(submission.submitted_date) }}.
    </span>
    <a title="Change submitted grades" target="_blank" href="https://itconnect.uw.edu/learn/tools/gradepage/change-submitted-grades/">Change submitted grades?</a>
  </div>

  <div v-if="graderoster.is_writing_section">
    <span><i class="fas fa-check-circle" style="color:#63AD45;"></i>
      {{ gettext("writing_course_note_receipt") }}
    </span>
  </div>

  <div v-if="!graderoster.is_submission_confirmation">
    <i class="fas fa-exclamation-circle" style="color:#EBDD5A;"></i>
    {{ gettext("confirmation_alert_warning") }}
    <a href="https://registrar.washington.edu/staffandfaculty/grading-resources/#faqs" target="_blank" class="hidden-print">More info.</a>
  </div>
</template>

<script>
import { formatLongDateTime } from "@/utils/dates";

export default {
  props: {
    graderoster: {
      type: Object,
      required: true,
    },
  },
};
</script>
