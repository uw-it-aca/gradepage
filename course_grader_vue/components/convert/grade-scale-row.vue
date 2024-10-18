<template>
  <div class="pull-left" aria-hidden="true">
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
    <span class="pull-left">
      <input
        type="text"
        :id="`min-percentage-${index}`"
        name="min-percentage"
        :value="rowData.minPercentage"
        :title="gettext('grade_scale_input_title') + rowData.grade"
        @change="minPercentageChanged($event.target.value)"
        required />
      <label for="`min-percentage-${index}`">
        <span role="alert" class="text-danger invalid-grade small">
          {{ rowData.minPercentageError }}
        </span>
      </label>
    </span>
  </div>
  <div>
    <span aria-hidden="true">&percnt;</span>
    <div>
      <span aria-hidden="true">&equals;</span>
      <span aria-hidden="true">{{ rowData.grade }}</span>
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
    lastMinPercentage() {
      return this.calculatorStore.scaleValues[
        this.calculatorStore.scaleValues.length - 2].minPercentage;
    },
  },
  methods: {
    minPercentageChanged: function (value) {
      this.calculatorStore.updateScalePercentage(this.index, value);
    },
  },
};
</script>
