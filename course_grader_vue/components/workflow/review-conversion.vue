<template>
  <Errors v-if="errorResponse" :error-response="errorResponse" />

  <h1 class="fs-1 fw-bold">Review Import</h1>

  <div class="mb-5">
    <SectionHeader :section="section" title="Review Grade Import" />
  </div>

  <template v-if="appState.gradeImport">
    <table v-if="appState.gradeImport.students" class="table table-striped">
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
          v-for="student in appState.gradeImport.students"
          :key="student.item_id"
        >
          <Student :student="student" />
        </tr>
      </tbody>
    </table>
    <div v-else>Importing grades...</div>
  </template>

  <div v-if="!isLoading && !errorResponse" class="text-end">
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
