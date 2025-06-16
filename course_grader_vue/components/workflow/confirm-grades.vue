<template>
  <!-- grade submission in progress (not yet accepted) -->
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

  <div class="d-flex justify-content-between align-items-end mb-4">
    <SectionHeader :section="section" title="Grade Receipt" />

    <div>
      <BButton
        v-if="appState.graderoster.gradable_student_count > 0"
        size="sm"
        variant="outline-primary"
        class="me-2 rounded-2"
        @click.prevent="editGrades()"
        >Change Grades</BButton
      >
      <BLink
        v-else
        class="btn btn-outline-primary btn-sm rounded-2 me-2"
        :href="section.export_url"
        >Download Change of Grade</BLink
      >
      <BLink
        class="btn btn-outline-primary btn-sm rounded-2"
        href="javascript:window.print()"
        >Print</BLink
      >
      <!--<BDropdown
        v-model="showSectionOptions"
        size="sm"
        variant="outline-primary"
        no-caret
        class="float-end d-inline-block"
        toggle-class="rounded-2"
      >
        <template #button-content>
          Options<i class="bi bi-chevron-down ms-1"></i
        ></template>
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
      </BDropdown>-->
    </div>
  </div>

  <!-- submission inline status -->
  <template v-if="appState.graderoster.has_successful_submissions">
    <BCard bg-variant="body-tertiary" class="border-0 mb-3">
      <ul class="list-unstyled text-success small m-0">
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
    </BCard>
  </template>

  <table v-if="appState.graderoster.students" class="table table-striped">
    <thead>
      <tr>
        <th scope="col">Student</th>
        <th scope="col">Section</th>
        <th scope="col">Credits</th>
        <th scope="col">Grade</th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="student in appState.graderoster.students"
        :key="student.item_id"
      >
        <Student :student="student" />
      </tr>
    </tbody>
  </table>
  <ul v-else class="list-unstyled m-0">
    <li v-for="index in 8" :key="index" class="border-top pt-2 mt-2">
      <BPlaceholder
        class="d-block bg-body-secondary"
        style="height: 60px"
        animation="glow"
      />
    </li>
  </ul>

  <div v-if="appState.graderoster.is_writing_section">
    <strong>Writing Section:</strong> {{ writingSectionText }}
  </div>
  <div v-if="appState.graderoster.has_duplicate_codes">
    <strong>Duplicate Code:</strong> {{ duplicateCodeText }}
  </div>
  <div v-if="!appState.graderoster.is_submission_confirmation">
    <strong>Grade receipt:</strong> Submitted grade may differ from official
    final grade.
    <BLink
      href="https://registrar.washington.edu/staff-faculty/grading-resources/"
      target="_blank"
      class="mx-2 d-print-none"
      >More info
    </BLink>
  </div>

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
  BCard,
  BLink,
  BPlaceholder,
  BDropdown,
  BDropdownItem,
  BDropdownDivider,
  BButton,
} from "bootstrap-vue-next";
import { getGraderoster } from "@/utils/data";
import { gradesSubmittedText, duplicateCodeText, writingSectionText } from "@/utils/grade";
import { ref } from "vue";

export default {
  components: {
    SectionHeader,
    Student,
    BAlert,
    BCard,
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
      duplicateCodeText,
      writingSectionText,
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
          this.errorResponse = error.data;
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
