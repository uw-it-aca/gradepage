<template>
  <Errors v-if="errorResponse" :error-response="errorResponse" />

  <template v-if="isLoading">
    <!-- please wait.. submitting -->
    <BAlert variant="success" :model-value="true" class="small">
      <span
        class="spinner-border spinner-border-sm me-1"
        aria-hidden="true"
      ></span>
      Grade submission in progress!
    </BAlert>
  </template>

  <h1 class="fs-1 fw-bold">
    <template v-if="isLoading">Submit Grades</template>
    <template v-else>Review Grades</template>
  </h1>

  <div class="mb-5">
    <SectionHeader :section="section" />
  </div>
  <template v-if="appState.graderoster">
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
  </template>

  <div class="mb-5">
    <div>
      <strong>Review:</strong>
      All grades will be submitted to the Office of the University Registrar
      as displayed above.
    </div>

    <div v-if="appState.graderoster.is_writing_section">
      <strong>Writing Section:</strong> {{ writingSectionText() }}
    </div>
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
import { BButton, BAlert } from "bootstrap-vue-next";
import { writingSectionText } from "@/utils/grade";

export default {
  components: {
    SectionHeader,
    Student,
    Errors,
    BAlert,
    BButton,
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
      // duplicateCodeText,
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
      }, 2000);
    },
  },
};
</script>
