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
      Grade submission in progress. You will receive an email once grades are
      submitted to Registrar.
    </div>
    <div>
      <BLink
        class="btn btn-info btn-sm rounded-3 text-nowrap"
        :href="section.term_url"
        >Return to the list of classes you can grade.
      </BLink>
    </div>
  </BAlert>

  <BDropdown
    v-model="showSectionOptions"
    size="sm"
    variant="subdued-primary"
    no-caret
    class="float-end d-inline-block"
    toggle-class="rounded-2"
  >
    <template #button-content> <i class="bi bi-three-dots"></i></template>
    <BDropdownItem
      v-if="appState.graderoster.gradable_student_count > 0"
      @click.prevent="editGrades()"
      ><i class="bi bi-pencil me-2 text-body-tertiary"></i>
      Edit Grades and Resubmit
    </BDropdownItem>
    <BDropdownItem :href="section.export_url">
      <i class="bi bi-download me-2 text-body-tertiary"></i>
      Download Change of Grade
    </BDropdownItem>
    <BDropdownItem href="javascript:window.print()">
      <i class="bi bi-printer me-2 text-body-tertiary"></i>
      Print this page
    </BDropdownItem>
    <BDropdownDivider />
    <BDropdownItem
      href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
      target="_blank"
      title="Information on assigning and submitting grades"
      ><i class="bi bi-question-circle me-2 text-body-tertiary"></i>
      GradePage Help
    </BDropdownItem>
  </BDropdown>

  <SectionHeader :section="section" title="Grade Receipt for" />

  <BAlert
    v-if="!appState.graderoster.is_submission_confirmation"
    variant="info"
    :model-value="true"
    class="small d-flex align-items-center"
  >
    Submitted grade may differ from official final grade.
    <BLink
      href="https://registrar.washington.edu/staff-faculty/grading-resources/"
      target="_blank"
      class="d-print-none"
      >More info
    </BLink>
  </BAlert>

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
        <span v-html="partialGradeErrorText"></span>
      </BAlert>

      <!-- danger -->
      <BAlert v-else variant="danger" :model-value="true" class="small">
        <i class="bi bi-exclamation-octagon-fill me-1"></i>
        <span v-html="allGradeErrorText"></span>
      </BAlert>
    </template>

    <!-- success -->
    <BAlert v-else variant="success" :model-value="true" class="small">
      <i class="bi bi-check-circle-fill me-1"></i>
      <span>Grade submission successful!</span>
    </BAlert>
  </template>

  <!-- success -->
  <BAlert
    v-if="appState.graderoster.submissions.length > 0"
    variant="success"
    :model-value="true"
    class="small"
  >
    <ul class="list-unstyled">
      <li
        v-for="(submission, index) in appState.graderoster.submissions"
        :key="index"
      >
        <i class="bi bi-check-circle-fill me-1"></i>
        <span v-if="submission.section_id">
          Section {{ submission.section_id }}:
        </span>
        <span v-html="gradesSubmittedText(submission)"></span>
      </li>
    </ul>
    <div>
      <BLink
        v-if="appState.graderoster.gradable_student_count > 0"
        title="Edit Grades and Resubmit"
        @click.prevent="editGrades()"
        >Change submitted grades
      </BLink>
      <BLink
        v-else
        href="https://itconnect.uw.edu/learn/tools/gradepage/change-submitted-grades/"
        target="_blank"
        title="Learn how to change submitted grades"
        >Change submitted grades
      </BLink>
    </div>
  </BAlert>

  <div
    v-if="
      appState.graderoster.is_writing_section ||
      appState.graderoster.has_duplicate_codes
    "
    class="mb-2 pb-2 border-bottom"
  >
    <div v-if="appState.graderoster.is_writing_section">
      Writing credit automatically given to all students with a passing grade in
      this course.
    </div>
    <div v-if="appState.graderoster.has_duplicate_codes">
      <span class="visually-hidden">
        In the list below, duplicate listings of the same student are
        differentiated with a
      </span>

      <BBadge
        variant="secondary"
        pill
        class="text-secondary-emphasis bg-secondary-subtle fw-normal"
        >Duplicate code</BBadge
      >
    </div>
  </div>

  <ul v-if="appState.graderoster.students" class="list-unstyled m-0">
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
    <li v-for="index in 8" :key="index" class="border-top pt-2 mt-2">
      <BPlaceholder
        class="d-block bg-body-secondary"
        style="height: 60px"
        animation="glow"
      />
    </li>
  </ul>

  <template v-if="appState.graderoster.has_grade_imports">
    <div v-if="appState.graderoster.grade_import_count > 1">
      Grades calculated using grade conversion scales.
      <label class="visually-hidden">
        Select grade conversion scale to view:
      </label>
      <BDropdown
        v-model="importConversion"
        size="sm"
        variant="outline-secondary"
        no-caret
        class="float-end d-inline-block"
        toggle-class="rounded-2"
      >
        <template #button-content> View Scale </template>
        <template v-if="submission.grade_import.import_conversion">
          <BDropdownItem
            v-for="(submission, index) in appState.graderoster.submissions"
            :key="index"
            :value="submission.grade_import.import_conversion"
          >
            <i class="me-2 text-body-tertiary"></i>
            Section {{ submission.section_id }}
          </BDropdownItem>
        </template>
      </BDropdown>
    </div>
    <div v-else-if="!importConversion">
      Grades calculated using a grade conversion scale.
      <BLink
        title="Show the grade conversion scale that was used"
        @click.prevent="showImportConversion()"
        >View scale
      </BLink>
    </div>

    <div v-if="importConversion">
      <h2 class="visually-hidden">Grade Conversion Scale</h2>
      <ol>
        <li v-for="(row, index) in importConversion.grade_scale" :key="index">
          <span v-if="index === importConversion.grade_scale.length - 1">
            <span
              >&lt; <span>{{ row.min_percentage }}&percnt;</span> &equals;
            </span>
            <span>{{ importConversion.lowest_valid_grade }}</span>
          </span>
          <span v-else>
            <span
              >&ge; <span>{{ row.min_percentage }}&percnt;</span> &equals;
            </span>
            <span>{{ row.grade }}</span>
          </span>
        </li>
      </ol>
      <BLink
        title="Hide grade conversion scale"
        @click.prevent="hideImportConversion()"
        >Hide scale
      </BLink>
    </div>
  </template>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import Errors from "@/components/errors.vue";
import { useWorkflowStateStore } from "@/stores/state";
import {
  BAlert,
  BLink,
  BPlaceholder,
  BDropdown,
  BDropdownItem,
  BDropdownDivider,
} from "bootstrap-vue-next";
import { getGraderoster, parseError } from "@/utils/data";
import { gradesSubmittedText } from "@/utils/grade";
import { ref } from "vue";

export default {
  components: {
    SectionHeader,
    Student,
    Errors,
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
      getGraderoster,
      showSectionOptions,
      gradesSubmittedText,
      parseError,
    };
  },
  data() {
    return {
      isLoading: false,
      errorResponse: null,
      importConversion: null,
    };
  },
  computed: {
    partialGradeErrorText() {
      return interpolate(
        ngettext(
          "Grades submitted, but <strong>one</strong> grade had an error.",
          "Grades submitted, but <strong>%(failed_submission_count)s</strong> grades had errors.",
          this.appState.graderoster.failed_submission_count
        ),
        this.appState.graderoster,
        true
      );
    },
    allGradeErrorText() {
      return interpolate(
        ngettext(
          "Grade submitted with error.",
          "Grades submitted with errors.",
          this.appState.graderoster.failed_submission_count
        ),
        this.appState.graderoster,
        true
      );
    },
  },
  methods: {
    editGrades: function () {
      this.isLoading = true;
      this.getGraderoster(this.section.graderoster_url)
        .then((data) => {
          this.appState.setGraderoster(data.graderoster);
          this.appState.editGrades();
        })
        .catch((error) => {
          this.errorResponse = this.parseError(error);
          this.isLoading = false;
        });
    },
    showImportConversion: function () {
      let submission = this.appState.graderoster.submissions[0];
      if (submission && submission.grade_import) {
        this.importConversion = submission.grade_import.import_conversion;
      }
    },
    hideImportConversion: function () {
      this.importConversion = null;
    },
  },
};
</script>
