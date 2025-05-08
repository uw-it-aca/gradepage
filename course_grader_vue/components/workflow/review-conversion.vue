<template>
  <BCard class="shadow-sm rounded-3" header-class="p-3" header="Default">
    <template #header>
      <SectionHeader :section="section" title="Review grades for import to" />
    </template>

    <template v-if="isLoading"> Importing grades... </template>
    <template v-else-if="errorResponse">
      <Errors :error-response="errorResponse" />
    </template>
    <template v-else-if="appState.gradeImport.students">
      <ul class="list-unstyled m-0">
        <li
          v-for="student in appState.gradeImport.students"
          :key="student.item_id"
          class="border-top pt-2 mt-2"
        >
          <Student :student="student" />
        </li>
      </ul>
    </template>

    <template v-if="!isLoading && !errorResponse" #footer>
      <div class="d-flex">
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
      </div>
    </template>
  </BCard>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import Errors from "@/components/errors.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { useCalculatorStore } from "@/stores/calculator";
import { BButton, BCard } from "bootstrap-vue-next";
import { saveImportedGrades, parseError } from "@/utils/data";

export default {
  components: {
    SectionHeader,
    Student,
    Errors,
    BButton,
    BCard,
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
      parseError,
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
          this.errorResponse = this.parseError(error);
          this.isLoading = false;
        });
    },
  },
};
</script>
