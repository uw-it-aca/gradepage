<template>
  <tr>
    <td>
      <div>
        <label
          :for="`calculator-percentage-${index}`"
          class="form-label visually-hidden"
        >
          <span v-if="last" class="">Lower Limit</span>
          <span v-else-if="first" class="">Upper Limit</span>
          <span v-else class="">Final Score</span>
        </label>
        <div class="input-group has-validation">
          <input
            :id="`calculator-percentage-${index}`"
            type="text"
            name="calculator-percentage"
            :value="rowData.percentage"
            class="form-control"
            :class="rowData.percentageError !== '' ? 'is-invalid' : ''"
            required
            aria-describedby="percent-addon2"
            @change="percentageChanged($event.target.value)"
          />
          <span id="percent-addon2" class="input-group-text">&percnt;</span>
          <span class="invalid-feedback">
            {{ rowData.percentageError }}
          </span>
        </div>
      </div>
    </td>
    <td class="p-3">&equals;</td>
    <td>
      <div>
        <label
          :for="`calculator-grade-${index}`"
          class="form-label visually-hidden"
        >
          <span v-if="last" class="">Lower Limit</span>
          <span v-else-if="first" class="">Upper Limit</span>
          <span v-else class="">Final Score</span>
        </label>
        <input
          :id="`calculator-grade-${index}`"
          type="text"
          name="calculator-grade"
          :value="rowData.grade"
          class="form-control"
          :class="rowData.gradeError !== '' ? 'is-invalid' : ''"
          required
          @change="gradeChanged($event.target.value)"
        />
        <span class="invalid-feedback">
          {{ rowData.gradeError }}
        </span>
      </div>
    </td>
  </tr>
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
