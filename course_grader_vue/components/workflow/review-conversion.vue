<template>
  <Errors v-if="errorResponse" :error-response="errorResponse" />

  <template v-if="isLoading">
    <BAlert variant="success" :model-value="true" class="small">
      <span
        class="spinner-border spinner-border-sm me-1"
        aria-hidden="true"
      ></span>
      Importing grades...
    </BAlert>
  </template>

  <h1 class="fs-1 fw-bold">Review Grade Conversion</h1>

  <div class="mb-4">
    <SectionHeader :section="section" title="Review Grade Conversion" />
  </div>
  <template v-if="appState.gradeImport">
    <table v-if="appState.graderoster.students" class="table table-striped">
      <thead class="table-body-secondary">
        <tr>
          <th scope="col">Student</th>
          <th scope="col">Section</th>
          <th scope="col">Imported Percentage</th>
          <th scope="col">Converted Grade</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="student in appState.gradeImport.students"
          :key="student.item_id"
        >
          <Student :student="student" />
        </tr>
      </tbody>
    </table>
  </template>

  <template v-if="!isLoading && !errorResponse">
    <div class="text-nowrap">
      <BButton variant="outline-primary" @click="editConversion"
        >Back to calculator</BButton
      >
      <BButton
        variant="primary"
        title="Import grades to GradePage"
        class="ms-2"
        @click="saveGrades"
        >Import Grades</BButton
      >
    </div>
  </template>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import Errors from "@/components/errors.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { useCalculatorStore } from "@/stores/calculator";
import { BButton } from "bootstrap-vue-next";
import { saveImportedGrades } from "@/utils/data";

export default {
  components: {
    SectionHeader,
    Student,
    Errors,
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
    const calculatorStore = useCalculatorStore();
    return {
      appState,
      calculatorStore,
      saveImportedGrades,
    };
  },
  data() {
    return {
      isLoading: false,
      errorResponse: null,
    };
  },
  methods: {
    editConversion: function () {
      this.appState.convertImport();
    },
    saveGrades: function () {
      let url = this.section.import_url + "/" + this.appState.gradeImport.id,
        put_data = {};

      put_data.conversion_scale = this.calculatorStore.conversionData;
      put_data.converted_grades = this.appState.convertedGradeData;

      this.isLoading = true;
      this.saveImportedGrades(url, put_data)
        .then((response) => {
          this.appState.$reset();
        })
        .catch((error) => {
          this.errorResponse = error.data;
          this.isLoading = false;
        });
    },
  },
};
</script>
