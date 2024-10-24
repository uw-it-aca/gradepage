<template>
  <BCard class="shadow-sm rounded-3" header-class="p-3" header="Default">
    <template #header>
      <SectionHeader :section="section" :title="gettext('review_import_grades')" />
    </template>

    <template v-if="errorResponse">
      <Errors :error-response="errorResponse" />
    </template>
    <template v-else-if="appState.gradeImport.students">
      <ul class="list-unstyled m-0">
        <li
          v-for="(student, index) in appState.gradeImport.students"
          :key="student.item_id"
          class="border-top pt-2 mt-2"
        >
          <Student :student="student" />
        </li>
      </ul>
    </template>

    <template #footer>
      <div class="d-flex">
        <div class="text-nowrap">
          <BButton variant="outline-primary" @click="editConversion">
            {{ gettext("conversion_back_calc") }}
          </BButton>
          <BButton variant="primary" @click="saveGrades" class="ms-2">
            {{ gettext("import_grades_btn") }}
            <span class="visually-hidden">
              {{ gettext("import_grades_btn_sr") }}
            </span>
          </BButton>
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
import { saveImportedGrades } from "@/utils/data";

export default {
  props: {
    section: {
      type: Object,
      required: true,
    },
  },
  components: {
    SectionHeader,
    Student,
    Errors,
    BButton,
    BCard,
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
      errorResponse: null,
    };
  },
  methods: {
    editConversion: function () {
      this.appState.convertImport();
    },
    saveGrades: function () {
      let url = this.section.import_url + "/" + this.appState.gradeImport.id,
          data = {};

      data.conversion_scale = this.calculatorStore.conversionData;
      data.converted_grades = this.appState.convertedGradeData;

      this.saveImportedGrades(url, JSON.stringify(data))
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.appState.$reset();
        })
        .catch((error) => {
          this.errorResponse = error.response;
        });
    },
  },
};
</script>
