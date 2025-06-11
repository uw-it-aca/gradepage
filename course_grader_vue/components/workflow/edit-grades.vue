<template>
  <div v-if="section">
    <GradeImportOptions
      :section="section"
      :expected-grade-count="appState.graderoster.gradable_student_count"
    />
  </div>

  <SectionHeader
    v-if="hasSubmittedAndSavedGrades"
    :section="section"
    title="Updating grades for"
  />
  <SectionHeader v-else :section="section" title="Enter grades for" />

  <Errors v-if="errorResponse" :error-response="errorResponse" />

  <template v-if="appState.graderoster">
    <!-- submission inline status -->
    <template v-if="appState.graderoster.has_successful_submissions">
      <ul class="list-unstyled text-success small my-5">
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
          <Student
            :student="student"
            :grade-choices="
              appState.graderoster.grade_choices[student.grade_choices_index]
            "
          />
        </tr>
      </tbody>
    </table>
    <ul v-else-if="!errorResponse" class="list-unstyled m-0">
      <li v-for="index in 8" :key="index" class="border-top pt-2 mt-2">
        <BPlaceholder
          class="d-block bg-body-secondary"
          style="height: 60px"
          animation="glow"
        />
      </li>
    </ul>

    <div v-if="appState.graderoster.is_writing_section">
      <strong>Writing Section:</strong>
      Writing credit automatically given to all students with a passing grade in
      this course.
    </div>
    <div v-if="appState.graderoster.has_duplicate_codes">
      <strong>Duplicate:</strong>
      Student dropped this section, and re-added.
    </div>

    <div class="text-end me-2">
      <span v-if="gradesRemainingText" aria-live="polite"
        >Status: {{ gradesRemainingText }}
      </span>
      <span v-else> Status: 0 grades missing</span>
    </div>

    <BAlert
      v-if="!isFormValid"
      :model-value="true"
      variant="danger"
      class="small"
      ><i class="bi-exclamation-octagon-fill me-1"></i>Unable to submit because
      there are
      <span v-if="gradesRemainingText">{{ gradesRemainingText }} </span></BAlert
    >

    <div class="text-end mt-4">
      <BButton
        v-if="hasSubmittedAndSavedGrades"
        variant="outline-primary"
        class="me-2"
        @click="discardGrades"
        >Discard</BButton
      >
      <BButton variant="primary" @click="reviewGrades">Review</BButton>
    </div>
  </template>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import Errors from "@/components/errors.vue";
import GradeImportOptions from "@/components/import/source-options.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { useGradeStore } from "@/stores/grade";
import { updateGraderoster, clearSavedGrades } from "@/utils/data";
import { gradesSubmittedText } from "@/utils/grade";
import { BAlert, BButton, BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    SectionHeader,
    GradeImportOptions,
    Student,
    Errors,
    BAlert,
    BButton,
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
    };
  },
  data() {
    return {
      errorResponse: null,
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
        alert("start validation!");
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
