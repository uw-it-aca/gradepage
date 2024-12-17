<template>
  <fieldset>
    <legend class="visually-hidden">
      Relate a Final Score (percentage) to a Grade Point:
    </legend>

    <div class="d-flex justify-content-between">
      <div class="w-50">
        <div class="input-group mb-3">
          <input
            :id="`calculator-percentage-${index}`"
            type="text"
            name="calculator-percentage"
            :value="rowData.percentage"
            class="form-control"
            required
            aria-describedby="percent-addon2"
            @change="percentageChanged($event.target.value)"
          />
          <span id="percent-addon2" class="input-group-text">&percnt;</span>
        </div>
        <label for="`calculator-percentage-${index}`">
          <span v-if="last" class="visually-hidden">
            Lower Limit: Final Score (percentage)
          </span>
          <span v-else-if="first" class="visually-hidden">
            Upper Limit: Final Score (percentage)
          </span>
          <span v-else class="visually-hidden"> Final Score (percentage) </span>
          <span role="alert" class="text-danger invalid-grade small">
            {{ rowData.percentageError }}
          </span>
        </label>
      </div>
      <div class="mx-3">&equals;</div>
      <div class="w-50">
        <input
          :id="`calculator-grade-${index}`"
          type="text"
          name="calculator-grade"
          :value="rowData.grade"
          class="form-control"
          required
          @change="gradeChanged($event.target.value)"
        />
        <label for="`calculator-grade-${index}`">
          <span v-if="last" class="visually-hidden">
            Lower Limit: Grade Point
          </span>
          <span v-else-if="first" class="visually-hidden">
            Upper Limit: Grade Point
          </span>
          <span v-else class="visually-hidden"> Lower Limit: Grade Point </span>
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
