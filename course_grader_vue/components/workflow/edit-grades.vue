<template>
  <BAlert
    v-if="errorResponse"
    :model-value="true"
    variant="danger"
    class="small"
    ><i class="bi-exclamation-octagon-fill me-1"></i>Unable to submit because
    there are
    <span v-if="gradesRemainingText">{{ gradesRemainingText }} </span></BAlert
  >

  <div v-if="section">
    <GradeImportOptions
      :section="section"
      :expected-grade-count="appState.graderoster.gradable_student_count"
    />
  </div>

  <SectionHeader :section="section" title="Enter grades for" />

  <Errors v-if="errorResponse == 'hide'" :error-response="errorResponse" />

  <template v-if="appState.graderoster">
    <BAlert
      v-if="appState.graderoster.submissions.length > 0"
      variant="success"
      :model-value="true"
      class="small"
    >
      <ul>
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
    </BAlert>

    <div
      v-if="
        appState.graderoster.is_writing_section ||
        appState.graderoster.has_duplicate_codes
      "
      class="mb-2 pb-2 border-bottom"
    >
      <div v-if="appState.graderoster.is_writing_section">
        <strong>Note:</strong>
        Writing credit automatically given to all students with a passing grade
        in this course.
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
  </template>

  <ul v-if="appState.graderoster.students" class="list-unstyled m-0">
    <li
      v-for="(student, index) in appState.graderoster.students"
      :key="student.item_id"
      class="bpt-2 mt-2"
      :class="index != 0 ? 'border-top' : ''"
    >
      <Student
        :student="student"
        :grade-choices="
          appState.graderoster.grade_choices[student.grade_choices_index]
        "
      />
    </li>
  </ul>
  <ul v-else-if="!errorResponse" class="list-unstyled m-0">
    <li v-for="index in 8" :key="index" class="border-top pt-2 mt-2">
      <BPlaceholder
        class="d-block bg-body-secondary"
        style="height: 60px"
        animation="glow"
      />
    </li>
  </ul>

  <div class="d-flex mt-4">
    <div class="flex-fill align-self-center text-end me-2">
      <span v-if="gradesRemainingText">{{ gradesRemainingText }} </span>
      <span v-else class="visually-hidden">
        All grades entered. Click Review to continue.
      </span>
    </div>
    <BButton variant="primary" @click="reviewGrades">Review</BButton>
  </div>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import Errors from "@/components/errors.vue";
import GradeImportOptions from "@/components/import/source-options.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { useGradeStore } from "@/stores/grade";
import { updateGraderoster, parseError } from "@/utils/data";
import { gradesSubmittedText } from "@/utils/grade";
import { BAlert, BBadge, BButton, BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    SectionHeader,
    GradeImportOptions,
    Student,
    Errors,
    BAlert,
    BBadge,
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
      gradesSubmittedText,
      parseError,
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
    reviewDisabled() {
      return this.gradeStore.missing > 0 || this.gradeStore.invalid > 0;
    },
  },
  methods: {
    reviewGrades: function () {
      this.updateGraderoster(
        this.section.graderoster_url,
        this.gradeStore.grades
      )
        .then((data) => {
          this.appState.setGraderoster(data.graderoster);
          this.appState.reviewGrades();
        })
        .catch((error) => {
          this.errorResponse = this.parseError(error);
        });
    },
  },
};
</script>
