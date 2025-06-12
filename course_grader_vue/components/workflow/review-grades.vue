<template>
  <template v-if="isLoading">
    <!-- success -->
    <BAlert variant="success" :model-value="true" class="small">
      <span
        class="spinner-border spinner-border-sm me-1"
        aria-hidden="true"
      ></span>
      Please wait, submitting grades to the Registrar
    </BAlert>
  </template>

  <SectionHeader :section="section" title="Review Grades" />

  <Errors v-if="errorResponse" :error-response="errorResponse" />

  <template v-else-if="appState.graderoster">
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
  </template>
  <template v-else>
    <ul class="list-unstyled m-0">
      <li v-for="index in 8" :key="index" class="border-top pt-2 mt-2">
        <BPlaceholder
          class="d-block bg-body-secondary"
          style="height: 60px"
          animation="glow"
        />
      </li>
    </ul>
  </template>

  <div v-if="appState.graderoster.is_writing_section">
    <strong>Writing Section:</strong>
    Writing credit automatically given to all students with a passing grade in
    this course.
  </div>
  <div v-if="appState.graderoster.has_duplicate_codes">
    <strong>Duplicate Code:</strong>
    Student dropped this section, and re-added.
  </div>
  <div>
    <strong>Review:</strong> All grades will be submitted to the Registrar as
    displayed above.
  </div>

  <template v-if="!isLoading && !errorResponse">
    <div v-if="section" class="text-end text-nowrap">
      <BButton
        :title="reviewBackTitle"
        variant="outline-primary"
        @click="editGrades"
        >Edit Grades</BButton
      >
      <BButton variant="primary" class="ms-2" @click="submitGrades"
        >Submit Grades</BButton
      >
    </div>
  </template>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import Errors from "@/components/errors.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { submitGraderoster } from "@/utils/data";
import { BButton, BPlaceholder, BBadge, BAlert } from "bootstrap-vue-next";

export default {
  components: {
    SectionHeader,
    Student,
    Errors,
    BBadge,
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
    return {
      appState,
      submitGraderoster,
    };
  },
  data() {
    return {
      isLoading: false,
      errorResponse: null,
    };
  },
  computed: {
    reviewBackTitle() {
      return "Go back and edit grades for " + this.section.section_name;
    },
  },
  methods: {
    editGrades: function () {
      this.appState.editGrades();
    },
    submitGrades: function () {
      this.isLoading = true;

      setTimeout(() => {
        this.submitGraderoster(this.section.graderoster_url, {})
          .then((data) => {
            this.appState.setGraderoster(data.graderoster);
          })
          .catch((error) => {
            this.errorResponse = error.data;
            this.isLoading = false;
          });
      }, 5000);
    },
  },
};
</script>
