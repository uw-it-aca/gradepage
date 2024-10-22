<template>
  <div :style="highlightRow ? 'background-color:lavender;' : ''">
    <div class="d-flex justify-content-between">
      <div class="me-3">
        <span v-if="last">&lt;</span>
        <span v-else>&ge;</span>
      </div>

      <div v-if="last">
        <span class="visually-hidden">
          {{ gettext("grade_scale_limit_pre") }} {{ lastMinPercentage }}
          {{ gettext("grade_scale_limit_post") }} {{ rowData.grade }}.
        </span>
        <span> {{ lastMinPercentage }} </span>
      </div>
      <div v-else>
        <div class="input-group mb-3">
          <input
            type="text"
            :id="`min-percentage-${index}`"
            class="form-control"
            name="min-percentage"
            :value="rowData.minPercentage"
            :title="gettext('grade_scale_input_title') + rowData.grade"
            @change="minPercentageChanged($event.target.value)"
            required
            aria-describedby="percent-addon2"
          />
          <span class="input-group-text" id="percent-addon2">&percnt;</span>
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
  },
  methods: {
    minPercentageChanged: function (value) {
      this.calculatorStore.updateScalePercentage(this.index, value);
    },
  },
};
</script>
