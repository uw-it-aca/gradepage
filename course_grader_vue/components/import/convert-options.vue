<template>
  <div v-if="errorResponse">
    TODO: {{ errorResponse }}
  </div>
  <div v-else-if="gradeImport.has_valid_percentages" class="d-grid gap-2">
    <p>{{ gettext("import_conversion_required") }}</p>
    <p>{{ gettext("import_conversion_required_select") }}</p>
    <BButton v-for="scale in calculatorStore.availableScales"
      variant="outline-secondary"
      @click="convertGrades(scale)">
      {{ gettext("conversion_scale_" + scale) }}
    </BButton>
  </div>
  <div v-else>
    <p>
      To continue, click <strong>{{ gettext("import_save_grades") }}</strong>.
      <br /><small><em>You will have a chance to enter, adjust, and review grades on the next screen.</em></small>
    </p>
    <p>To select a different file, click <strong>Cancel</strong>.</p>
    <div>
      <BButton variant="primary" @click="saveGrades">
        {{ gettext("import_save_grades") }}
      </BButton>
    </div>
  </div>
</template>

<script>
import { saveImportedGrades } from "@/utils/data";
import { useWorkflowStateStore } from "@/stores/state";
import { useCalculatorStore } from "@/stores/calculator";
import { BButton } from "bootstrap-vue-next";

export default {
  components: {
    BButton,
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
    gradeImport: {
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
      errorResponse: null,
    };
  },
  methods: {
    convertGrades: function (scale) {
      this.calculatorStore.$reset();
      this.calculatorStore.setScale(scale);
      this.appState.setGradeImport(this.gradeImport);
      this.appState.convertImport();
    },
    saveGrades: function () {
      let url = this.section.import_url + "/" + this.gradeImport.id;
      this.saveImportedGrades(url, {})
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.errorResponse = null;
        })
        .catch((error) => {
          this.errorResponse = error.response;
        });
    },
  },
};
</script>
