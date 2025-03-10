<template>
  <div v-if="errorResponse">
    {{ errorResponse.error }}
  </div>
  <div
    v-else-if="appState.gradeImport.has_valid_percentages"
    class="d-grid gap-2"
  >
    <p>
      The Office of the Registrar requires submitted grades to follow official
      formatting.
    </p>
    <p>Please select a format to use:</p>

    <BButton
      v-for="(scale, index) in calculatorStore.availableScales"
      :key="index"
      variant="outline-secondary"
      @click="convertGrades(scale)"
      >{{ gettext("conversion_scale_" + scale) }}
    </BButton>
  </div>
  <div v-else>
    <p>
      <span>To continue, click <strong>Import grades</strong>.</span>
      <br />
      <small>
        <em>
          You will have a chance to enter, adjust, and review grades on the next
          screen.
        </em>
      </small>
    </p>
    <p>To select a different file, click <strong>Cancel</strong>.</p>
    <div>
      <BButton variant="primary" @click="saveGrades">Import grades </BButton>
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
        data = { conversion_scale: null, converted_grades: {} };

      this.saveImportedGrades(url, JSON.stringify(data))
        .then((data) => {
          this.appState.$reset();
        })
        .catch((error) => {
          this.errorResponse = error;
        });
    },
  },
};
</script>
