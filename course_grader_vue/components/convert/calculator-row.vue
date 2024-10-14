<template>
  <fieldset>
    <legend class="visually-hidden">{{ gettext("calculator_legend") }}</legend>
    <span class="col-xs-4">
      <input
        type="text"
        :id="`calculator-percentage-${index}`"
        name="calculator-percentage"
        :value="percentage"
        class="form-control"
        @change="percentageChanged($event.target.value)"
        required />
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
        <span class="pull-left">{{ percentageError }}</span>
      </label>
    </span>
    <span aria-hidden="true">&percnt;</span>
    <span aria-hidden="true">&equals;</span>
    <span class="col-xs-4">
      <input
        type="text"
        :id="`calculator-grade-${index}`"
        name="calculator-grade"
        :value="grade"
        class="form-control"
        @change="gradeChanged($event.target.value)"
        required />
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
        <span class="pull-right">{{ gradeError }}</span>
      </label>
    </span>
  </fieldset>
</template>

<script>
import { useCalculatorStore } from "@/stores/calculator";

export default {
  props: {
    defaultPercentage: {
      type: String,
      default: "",
    },
    defaultGrade: {
      type: String,
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
  data() {
    return {
      percentage: "",
      grade: "",
      percentageError: "",
      gradeError: "",
    };
  },
  methods: {
    percentageChanged: function (percentage) {
    },
    gradeChanged: function (grade) {
    },
    initialize: function () {
      this.percentage = this.defaultPercentage;
      this.grade = this.defaultGrade;
    },
  },
  created() {
    this.initialize();
  }
};
</script>
