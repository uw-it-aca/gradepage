<template>
  <!-- grade submission in progress -->
  <BAlert
    v-if="appState.graderoster.has_inprogress_submissions"
    variant="info"
    :model-value="true"
    class="small d-flex align-items-center"
  >
    <div class="flex-fill me-3">
      <i class="bi bi-exclamation-circle-fill me-1"></i>
      {{ gettext("grade_submission_inprogress") }}.
      {{ gettext("in_progress_submission_email") }}
    </div>
    <div>
      <BLink
        class="btn btn-info btn-sm rounded-3 text-nowrap"
        v-text="gettext('return_classes_to_grade')"
        :href="section.term_url"
        >
      </BLink>
    </div>
  </BAlert>

  <BCard class="shadow-sm rounded-3" header-class="p-3" header="Default">
    <template #header>
      <BDropdown
        v-model="showSectionOptions"
        size="sm"
        variant="outline-secondary"
        no-caret
        class="float-end d-inline-block"
        toggle-class="rounded-2"
      >
        <template #button-content>
          <i class="bi bi-three-dots"></i
        ></template>
        <BDropdownItem :href="section.export_url">
          <i class="bi bi-download me-2 text-body-tertiary"></i>
          {{ gettext("btn_download_cog") }}
        </BDropdownItem>
        <BDropdownItem href="javascript:window.print()">
          <i class="bi bi-printer me-2 text-body-tertiary"></i>
          {{ gettext("btn_print_page") }}
        </BDropdownItem>
        <BDropdownDivider />
        <BDropdownItem
          href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
          target="_blank"
          :title="gettext('help_btn_title')"
          ><i class="bi bi-question-circle me-2 text-body-tertiary"></i>
         {{ gettext("help_btn") }}
        </BDropdownItem>
      </BDropdown>

      <SectionHeader :section="section" :title="gettext('submitted_grades_for')" />

      <div
        v-if="!appState.graderoster.is_submission_confirmation"
        class="small"
        role="status"
      >
        {{ gettext("confirmation_alert_warning") }}
        <BLink
          href="https://registrar.washington.edu/staffandfaculty/grading-resources/#faqs"
          target="_blank"
          class="d-print-none"
          v-text="gettext('more_info')"
        >
        </BLink>
      </div>
    </template>

    <template v-if="appState.graderoster.is_submission_confirmation">
      <template v-if="appState.graderoster.has_failed_submissions">
        <!-- warning -->
        <BAlert
          v-if="appState.graderoster.has_successful_submissions"
          variant="warning"
          :model-value="true"
          class="small"
        >
          <i class="bi bi-exclamation-triangle-fill me-1"></i>
          {{ partialGradeErrorText }}
        </BAlert>

        <!-- danger -->
        <BAlert v-else variant="danger" :model-value="true" class="small">
          <i class="bi bi-exclamation-octagon-fill me-1"></i>
          {{ allGradeErrorText }}
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
      v-for="submission in appState.graderoster.submissions"
      variant="success"
      :model-value="true"
      class="small"
    >
      <i class="bi bi-check-circle-fill me-1"></i>
      <span v-if="submission.section_id">
        {{ gettext("section") }} {{ submission.section_id }}:
      </span>
      <span v-html="gradesSubmittedText(submission)"></span>
      <BLink
        href="https://itconnect.uw.edu/learn/tools/gradepage/change-submitted-grades/"
        target="_blank"
        :title="gettext('change_submitted_grades')"
        >{{ gettext("change_submitted_grades") }}?
      </BLink>
    </BAlert>

    <div v-if="appState.graderoster.is_writing_section || appState.graderoster.has_duplicate_codes"
      class="mb-2 pb-2 small text-muted border-bottom"
    >
      <div v-if="appState.graderoster.is_writing_section">
        {{ gettext("writing_course_note_receipt") }}
      </div>
      <div v-if="appState.graderoster.has_duplicate_codes">
        {{ gettext("duplicate_code") }}
        <i class="bi bi-circle-fill text-secondary"></i>
      </div>
    </div>

    <ul v-if="appState.graderoster.students"
      class="list-unstyled m-0">
      <li
        v-for="(student, index) in appState.graderoster.students"
        :key="student.item_id"
        class="bpt-2 mt-2"
        :class="index != 0 ? 'border-top' : ''"
      >
        <Student :student="student" />
      </li>
    </ul>
    <ul v-else class="list-unstyled m-0">
      <li v-for="index in 8" class="border-top pt-2 mt-2" :key="index">
        <BPlaceholder
          class="d-block bg-body-secondary"
          style="height: 60px"
          animation="glow"
        />
      </li>
    </ul>

    <template #footer v-if="appState.graderoster.has_grade_imports">
      <div v-if="appState.graderoster.grade_import_count > 1">
        {{ gettext("multi_conversion_scale_msg") }}
        <label class="visually-hidden">
          {{ gettext("multi_conversion_scale_view") }}
        </label>
        <BDropdown
          v-model="importConversion"
          size="sm"
          variant="outline-secondary"
          no-caret
          class="float-end d-inline-block"
          toggle-class="rounded-2"
        >
          <template #button-content>
            {{ gettext("multi_conversion_scale_option_view") }}
          </template>
          <BDropdownItem
            v-for="(submission, index) in appState.graderoster.submissions"
            v-if="submission.grade_import.import_conversion"
            :value="submission.grade_import.import_conversion"
          >
            <i class="me-2 text-body-tertiary"></i>
            {{ gettext("section") }} {{ submission.section_id }}
          </BDropdownItem>
        </BDropdown>
      </div>
      <div v-else-if="!importConversion">
        {{ gettext("conversion_scale_msg") }}
        <BLink
          :title="gettext('conversion_scale_view_title')"
          v-text="gettext('conversion_scale_view')"
          @click.prevent="showImportConversion()"
        >
        </BLink>
      </div>

      <div v-if="importConversion">
        <h2 class="visually-hidden">{{ gettext("conversion_scale_header") }}</h2>
        <ol>
          <li v-for="(row, index) in importConversion.grade_scale">
            <span v-if="index === importConversion.grade_scale.length - 1">
              <span>&lt; <span>{{ row.min_percentage }}&percnt;</span> &equals; </span>
              <span>{{ importConversion.lowest_valid_grade }}</span>
            </span>
            <span v-else>
              <span>&ge; <span>{{ row.min_percentage }}&percnt;</span> &equals; </span>
              <span>{{ row.grade }}</span>
            </span>
          </li>
        </ol>
        <BLink
          :title="gettext('conversion_scale_hide_title')"
          v-text="gettext('conversion_scale_hide')"
          @click.prevent="hideImportConversion()"
        >
        </BLink>
      </div>
    </template>
  </BCard>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import { useWorkflowStateStore } from "@/stores/state";
import {
  BCard,
  BAlert,
  BLink,
  BPlaceholder,
  BDropdown,
  BDropdownItem,
  BDropdownDivider,
} from "bootstrap-vue-next";
import { formatLongDateTime } from "@/utils/dates";
import { ref } from "vue";

export default {
  components: {
    SectionHeader,
    Student,
    BCard,
    BAlert,
    BLink,
    BPlaceholder,
    BDropdown,
    BDropdownItem,
    BDropdownDivider,
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
  },
  setup() {
    const showSectionOptions = ref(false);
    const appState = useWorkflowStateStore();
    return {
      appState,
      formatLongDateTime,
      showSectionOptions,
    };
  },
  data() {
    return {
      importConversion: null,
    };
  },
  computed: {
    partialGradeErrorText() {
      return interpolate(ngettext(
        "Grades submitted, but one grade had an error.",
        "Grades submitted, but %(failed_submission_count)s grades had errors.",
        this.appState.graderoster.failed_submission_count
      ), this.appState.graderoster, true);
    },
    allGradeErrorText() {
      return interpolate(ngettext(
        "Grade submitted with error.",
        "Grades submitted with errors.",
        this.appState.graderoster.failed_submission_count
      ), this.appState.graderoster, true);
    },
  },
  methods: {
    gradesSubmittedText(submission) {
      return interpolate(ngettext(
        "<strong>One</strong> grade submitted to the Registrar by <strong>%(submitted_by)s</strong> on %(submitted_date)s.",
        "<strong>%(submitted_count)s</strong> grades submitted to the Registrar by <strong>%(submitted_by)s</strong> on %(submitted_date)s.",
        submission.submitted_count), {
          submitted_count: submission.submitted_count,
          submitted_by: submission.submitted_by,
          submitted_date: formatLongDateTime(submission.submitted_date),
        }, true);
    },
    showImportConversion () {
      let submission = this.appState.graderoster.submissions[0];
      if (submission && submission.grade_import) {
        this.importConversion = submission.grade_import.import_conversion;
      }
    },
    hideImportConversion () {
      this.importConversion = null;
    },
  },
};
</script>
