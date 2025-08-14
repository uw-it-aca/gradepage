<template>
  <Errors v-if="errorResponse" :error-response="errorResponse" />

  <!-- grade submission in progress (not yet accepted) -->
  <BAlert
    v-if="appState.graderoster.has_inprogress_submissions"
    variant="info"
    :model-value="true"
    class="small d-flex align-items-center"
  >
    <i class="bi bi-exclamation-circle-fill me-1"></i>
    Grade submission in progress. You will receive an email once grades are
    submitted to the Office of the University Registrar.
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

  <h1 class="fs-1 fw-bold">Grade Receipt</h1>

  <div class="d-flex justify-content-between align-items-end mb-4">
    <SectionHeader
      :section="section"
      :status="appState.graderoster.has_successful_submissions"
    />
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
    </div>
  </div>

  <!-- submission inline status -->
  <SectionGradingStatus
    v-if="appState.graderoster"
    :graderoster="appState.graderoster"
  />

  <div v-if="appState.graderoster.is_writing_section">
    <strong>Writing Section:</strong> {{ writingSectionText() }}
  </div>

  <table v-if="appState.graderoster.students" class="table table-striped">
    <thead class="table-body-secondary">
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

  <ImportConversions :submissions="appState.graderoster.submissions" />
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import SectionGradingStatus from "@/components/section/grading-status.vue";
import ImportConversions from "@/components/section/import-conversion.vue";
import Student from "@/components/student.vue";
import Errors from "@/components/errors.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { BAlert, BLink, BButton } from "bootstrap-vue-next";
import { getGraderoster } from "@/utils/data";
import {
  gradesSubmittedText,
  writingSectionText,
} from "@/utils/grade";
import { ref } from "vue";

export default {
  components: {
    SectionHeader,
    SectionGradingStatus,
    ImportConversions,
    Student,
    Errors,
    BAlert,
    BLink,
    BButton,
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
      writingSectionText,
    };
  },
  data() {
    return {
      isLoading: false,
      errorResponse: null,
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
  },
};
</script>
