<template>
  <div v-if="errorResponse">
    {{ errorResponse }}
  </div>
  <div v-else-if="appState.gradeImport.has_valid_percentages" class="d-grid gap-2">
    <p v-html="gettext('import_conversion_required')"></p>
    <p v-html="gettext('import_conversion_required_select')"></p>

    <BButton v-for="scale in calculatorStore.availableScales"
      variant="outline-secondary"
      v-text="gettext('conversion_scale_' + scale)"
      @click="convertGrades(scale)">
    </BButton>
  </div>
  <div v-else>
    <p>
      <span v-html="gettext('import_save_continue')"></span>
      <br /><small><em>{{ gettext("import_save_note") }}</em></small>
    </p>
    <p v-html="gettext('import_select_different_file')"></p>
    <div>
      <BButton
        variant="primary"
        v-text="gettext('import_save_grades_btn')"
        @click="saveGrades"
      >
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
      this.calculatorStore.setScale(scale);
      this.appState.convertImport();
    },
    saveGrades: function () {
      let url = this.section.import_url + "/" + this.appState.gradeImport.id,
          data = {conversion_scale: null, converted_grades: {}};

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
