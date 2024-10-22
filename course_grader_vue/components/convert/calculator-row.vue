<template>
  <fieldset>
    <legend class="visually-hidden">{{ gettext("calculator_legend") }}</legend>

    <div class="d-flex justify-content-between">
      <div class="w-50">
        <div class="input-group mb-3">
          <input
            type="text"
            :id="`calculator-percentage-${index}`"
            name="calculator-percentage"
            :value="rowData.percentage"
            class="form-control"
            @change="percentageChanged($event.target.value)"
            required
            aria-describedby="percent-addon2"
          />
          <span class="input-group-text" id="percent-addon2">&percnt;</span>
        </div>
        <label for="`calculator-percentage-${index}`">
          <span v-if="last" class="visually-hidden">
            {{ gettext("calculator_perc_label_lower") }}
          </span>
          <span v-else-if="first" class="visually-hidden">
            {{ gettext("calculator_perc_label_upper") }}
          </span>
          <span v-else class="visually-hidden">
            {{ gettext("calculator_perc_label") }}
          </span>
          <span role="alert" class="text-danger invalid-grade small">
            {{ rowData.percentageError }}
          </span>
        </label>
      </div>
      <div class="mx-3">&equals;</div>
      <div class="w-50">
        <input
          type="text"
          :id="`calculator-grade-${index}`"
          name="calculator-grade"
          :value="rowData.grade"
          class="form-control"
          @change="gradeChanged($event.target.value)"
          required
        />
        <label for="`calculator-grade-${index}`">
          <span v-if="last" class="visually-hidden">
            {{ gettext("calculator_grade_label_lower") }}
          </span>
          <span v-else-if="first" class="visually-hidden">
            {{ gettext("calculator_grade_label_upper") }}
          </span>
          <span v-else class="visually-hidden">
            {{ gettext("calculator_grade_label") }}
          </span>
          <span role="alert" class="text-danger invalid-grade small">
            {{ rowData.gradeError }}
          </span>
        </label>
      </div>
    </div>
  </fieldset>
</template>

<script>
import { useCalculatorStore } from "@/stores/calculator";

export default {
  props: {
    rowData: {
      type: Object,
      required: true,
    },
    first: {
      type: Boolean,
      required: true,
    },
    last: {
      type: Boolean,
      required: true,
    },
    index: {
      type: Number,
      required: true,
    },
  },
  setup() {
    const calculatorStore = useCalculatorStore();
    return {
      calculatorStore,
    };
  },
  methods: {
    percentageChanged: function (value) {
      this.calculatorStore.updateCalculatorPercentage(this.index, value);
    },
    gradeChanged: function (value) {
      this.calculatorStore.updateCalculatorGrade(this.index, value);
    },
  },
};
</script>
