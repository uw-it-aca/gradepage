<template>
  <Errors v-if="errorResponse" :error-response="errorResponse" />

  <h1 class="fs-1 fw-bold">
    <template v-if="appState.graderoster.has_successful_submissions"
      >Change Grades</template
    >
    <template v-else>Enter Grades</template>
  </h1>

  <div class="d-flex justify-content-between align-items-start mb-4">
    <SectionHeader
      v-if="appState.graderoster.has_successful_submissions"
      :section="section"
      title="Change Grades"
      :status="appState.graderoster.has_successful_submissions"
    />
    <SectionHeader v-else :section="section" title="Enter Grades" />
    <template v-if="section">
      <GradeImportOptions
        :section="section"
        :expected-grade-count="appState.graderoster.gradable_student_count"
      />
    </template>
  </div>

  <template v-if="appState.graderoster">
    <!-- submission inline status -->
    <template v-if="appState.graderoster.has_successful_submissions">
      <BCard bg-variant="body-tertiary" class="border-0 mb-4">
        <div v-if="hasSubmittedAndSavedGrades" class="border-bottom mb-2 pb-2">
          <span class="fw-bold"
            ><i class="bi bi-exclamation-triangle-fill text-warning me-2"></i
            >Resubmit to make any changes official.</span
          >
          Otherwise, the most recent grade submission will stand.
        </div>
        <!-- check if secondary section -->
        <div class="d-flex justify-content-between">
          <div>
            <div class="fw-bold ms-4">Course sections submitted: x of x</div>
            <div class="fst-italic small ms-4">
              Submitted grades may differ from official final grade.
              <BLink
                to="https://registrar.washington.edu/staff-faculty/grading-resources/"
                >Learn why</BLink
              >.
            </div>
          </div>
          <div>
            <BButton v-b-toggle.collapse-1 variant="quiet-primary" size="sm"
              >Show sections</BButton
            >
          </div>
        </div>
        <BCollapse id="collapse-1">
          <ul class="list-unstyled mt-2 ms-4">
            <li
              v-for="(submission, index) in appState.graderoster.submissions"
              :key="index"
            >
              <i class="bi bi-check-circle-fill text-success me-2"></i>
              <span v-if="submission.section_id">
                Section {{ submission.section_id }}:
              </span>
              <span v-html="gradesSubmittedText(submission)"></span>
            </li>
          </ul>
        </BCollapse>

        <!-- else primary -->
        <ul class="list-unstyled m-0">
          <li
            v-for="(submission, index) in appState.graderoster.submissions"
            :key="index"
          >
            <i class="bi bi-check-circle-fill text-success me-2"></i>
            <span v-if="submission.section_id">
              Section {{ submission.section_id }}:
            </span>
            <span v-html="gradesSubmittedText(submission)"></span>
          </li>
        </ul>
        <div class="fst-italic small ms-4">
          Submitted grades may differ from official final grade.
          <BLink
            to="https://registrar.washington.edu/staff-faculty/grading-resources/"
            >Learn why</BLink
          >.
        </div>
      </BCard>
    </template>

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
    <div v-else-if="!errorResponse">Loading something....</div>

    <div class="d-flex justify-content-between mb-4">
      <div class="w-75">
        <div v-if="appState.graderoster.is_writing_section">
          <strong>Writing Section:</strong> {{ writingSectionText() }}
        </div>
      </div>
      <div class="w-25 text-end">
        <span class="fw-bold me-1">Status:</span>
        <span v-if="gradesRemainingText" aria-live="polite"
          >{{ gradesRemainingText }}
        </span>
        <span v-else>0 grades missing</span>
      </div>
    </div>

    <BAlert
      v-if="showValidationAlert && !isFormValid"
      :model-value="true"
      variant="danger"
      class="small"
      ><i class="bi-exclamation-octagon-fill me-1"></i>Unable to submit because
      there are
      <span v-if="gradesRemainingText">{{ gradesRemainingText }} </span></BAlert
    >

    <div class="text-end">
      <BButton
        v-if="hasSubmittedAndSavedGrades"
        variant="outline-primary"
        class="me-2"
        @click="discardGrades"
        >Discard Changes</BButton
      >
      <BButton variant="primary" @click="reviewGrades">Review Grades</BButton>
    </div>
  </template>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import Errors from "@/components/errors.vue";
import Links from "@/components/links.vue";
import GradeImportOptions from "@/components/import/source-options.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { useGradeStore } from "@/stores/grade";
import { updateGraderoster, clearSavedGrades } from "@/utils/data";
import {
  gradesSubmittedText,
  duplicateCodeText,
  writingSectionText,
} from "@/utils/grade";
import { BAlert, BButton, BCard, BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    SectionHeader,
    GradeImportOptions,
    Student,
    Errors,
    Links,
    BAlert,
    BButton,
    BCard,
    BPlaceholder,
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
  },
  setup() {
    const appState = useWorkflowStateStore();
    const gradeStore = useGradeStore();
    return {
      appState,
      gradeStore,
      updateGraderoster,
      clearSavedGrades,
      gradesSubmittedText,
      duplicateCodeText,
      writingSectionText,
    };
  },
  data() {
    return {
      errorResponse: null,
      showValidationAlert: false,
    };
  },
  computed: {
    gradesRemainingText() {
      var s = [],
        missing = this.gradeStore.missing,
        invalid = this.gradeStore.invalid;

      if (missing) {
        s.push(missing > 1 ? `${missing} grades missing` : "1 grade missing");
      }
      if (invalid) {
        s.push(invalid > 1 ? `${invalid} grades invalid` : "1 grade invalid");
      }
      return s.join(", ");
    },
    isFormValid() {
      return this.gradeStore.missing === 0 && this.gradeStore.invalid === 0;
    },
    hasSubmittedAndSavedGrades() {
      return (
        this.appState.graderoster.has_successful_submissions &&
        (this.appState.graderoster.has_saved_grades ||
          this.gradeStore.saved > 0)
      );
    },
  },
  methods: {
    reviewGrades: function () {
      if (this.isFormValid) {
        let put_data = { grades: this.gradeStore.grades };
        this.updateGraderoster(this.section.graderoster_url, put_data)
          .then((data) => {
            this.appState.setGraderoster(data.graderoster);
            this.appState.reviewGrades();
          })
          .catch((error) => {
            this.errorResponse = error.data;
          });
      } else {
        this.showValidationAlert = true;
      }
    },
    discardGrades: function () {
      if (confirm("Are you sure you want to discard grade changes?")) {
        this.gradeStore.$reset();
        this.appState.$reset();
        this.clearSavedGrades(this.section.graderoster_url)
          .then((data) => {
            this.appState.setGraderoster(data.graderoster);
            this.errorResponse = null;
          })
          .catch((error) => {
            this.errorResponse = error.data;
          });
      }
    },
  },
};
</script>
