<template>
  <fieldset>
    <legend class="visually-hidden">{{ gettext("calculator_legend") }}</legend>
    <span class="col-xs-4 gp-calc-percentage">
      <input
        type="text"
        :id="`calculator-percentage-${index}`"
        name="calculator-percentage"
        :value="percentage"
        class="form-control gp-calc-input-percentage"
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
        <span class="pull-left gp-calc-err"></span>
      </label>
    </span>
    <span aria-hidden="true">&percnt;</span>
    <span aria-hidden="true">&equals;</span>
    <span class="col-xs-4 gp-calc-grade">
      <input
        type="text"
        :id="`calculator-grade-${index}`"
        name="calculator-grade"
        :value="grade"
        class="form-control gp-calc-input"
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
        <span class="pull-right gp-calc-err"></span>
      </label>
    </span>
  </fieldset>
</template>

<script>
export default {
  props: {
    percentage: {
      type: String,
      default: "",
    },
    grade: {
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
};
</script>
