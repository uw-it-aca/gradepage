<template>
  <div class="pull-left" aria-hidden="true">
    <span v-if="last">&lt;</span>
    <span v-else>&ge;</span>
  </div>
  <div v-if="last">
    <span class="visually-hidden">{{ gettext("grade_scale_limit_pre") }}</span>
    <span class="pull-left"></span>
    <span class="visually-hidden">{{ gettext("grade_scale_limit_post") }}{{ grade }}.</span>
  </div>
  <div v-else>
    <span class="pull-left">
      <input
        type="text"
        :id="`min-percentage-${index}`"
        name="min-percentage"
        :value="minPercentage"
        :title="gettext('grade_scale_input_title') + grade"
        @change="minPercentageChanged($event.target.value)"
        required />
      <label for="`min-percentage-${index}`" class="calculator-err">
        <span class="visually-hidden"></span>
        <span class="pull-left">{{ minPercentageError }}</span>
      </label>
    </span>
  </div>
  <div>
    <span aria-hidden="true">&percnt;</span>
    <div>
      <span aria-hidden="true">&equals;</span>
      <span aria-hidden="true">{{ grade }}</span>
    </div>
  </div>
</template>

<script>
import { useCalculatorStore } from "@/stores/calculator";

export default {
  props: {
    minPercentage: {
      type: String,
      required: true,
    },
    grade: {
      type: String,
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
  data() {
    return {
      minPercentageError: "",
    };
  },
  methods: {
    minPercentageChanged: function (value) {
      this.calculatorStore.updateScalePercentage(this.index, value);
    },
  },
};
</script>
