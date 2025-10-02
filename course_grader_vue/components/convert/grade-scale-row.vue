<template>
  <tr :class="highlightRow ? 'table-primary' : ''">
    <td v-if="last" class="py-3">{{ gradeScaleLimitText }}</td>
    <td v-else>
      <div>
        <label
          :for="`min-percentage-${index}`"
          class="form-label visually-hidden"
          >Enter grade</label
        >
        <div class="input-group has-validation">
          <span :id="`ge-addon2-${index}`" class="input-group-text">&ge;</span>
          <input
            :id="`min-percentage-${index}`"
            type="text"
            class="form-control"
            :class="rowData.minPercentageError !== '' ? 'is-invalid' : ''"
            name="min-percentage"
            :value="rowData.minPercentage"
            :title="gradeScaleTitle"
            required
            aria-describedby="percent-addon2"
            @change="minPercentageChanged($event.target.value)"
          />
          <span :id="`percent-addon2-${index}`" class="input-group-text"
            >&percnt;</span
          >
          <span class="invalid-feedback">
            {{ rowData.minPercentageError }}
          </span>
        </div>
      </div>
    </td>
    <td class="p-3">&equals;</td>
    <td class="py-3">{{ rowData.grade }}</td>
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
  computed: {
    highlightRow() {
      return !this.last &&
        this.calculatorStore.calculatorValues.find(
          (c) => c.grade === this.rowData.grade
        )
        ? true
        : false;
    },
    lastMinPercentage() {
      return this.calculatorStore.scaleValues[
        this.calculatorStore.scaleValues.length - 2
      ].minPercentage;
    },
    gradeScaleLimitText() {
      if (this.lastMinPercentage) {
        return interpolate(
          "Final grades below %(min_percentage)s%",
          {
            min_percentage: this.lastMinPercentage,
          },
          true
        );
      }
      return "";
    },
    gradeScaleTitle() {
      return interpolate(
        "Minimum percentage that will result in a %(grade)s",
        this.rowData,
        true
      );
    },
  },
  methods: {
    minPercentageChanged: function (value) {
      this.calculatorStore.updateScalePercentage(this.index, value);
    },
  },
};
</script>
