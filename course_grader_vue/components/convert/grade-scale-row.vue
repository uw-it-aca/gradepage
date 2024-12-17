<template>
  <div :class="highlightRow ? 'bg-primary-subtle' : ''">
    <div class="d-flex justify-content-between">
      <div class="me-3">
        <span v-if="last">&lt;</span>
        <span v-else>&ge;</span>
      </div>

      <div v-if="last">
        <span class="visually-hidden">{{ gradeScaleLimitText }}</span>
        <span> {{ lastMinPercentage }} </span>
      </div>
      <div v-else>
        <div class="input-group mb-3">
          <input
            :id="`min-percentage-${index}`"
            type="text"
            class="form-control"
            name="min-percentage"
            :value="rowData.minPercentage"
            :title="gradeScaleTitle"
            required
            aria-describedby="percent-addon2"
            @change="minPercentageChanged($event.target.value)"
          />
          <span id="percent-addon2" class="input-group-text">&percnt;</span>
        </div>
        <label for="`min-percentage-${index}`">
          <span role="alert" class="text-danger invalid-grade small">
            {{ rowData.minPercentageError }}
          </span>
        </label>
      </div>

      <div aria-hidden="true" class="mx-3">&equals;</div>
      <div aria-hidden="true" class="w-50 text-center">{{ rowData.grade }}</div>
    </div>
  </div>
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
      return interpolate(
        "Any final grade below a %(min_percentage)s% will result in a %(grade)s.",
        {
          min_percentage: this.lastMinPercentage,
          grade: this.rowData.grade,
        },
        true
      );
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
