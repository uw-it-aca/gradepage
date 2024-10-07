<template>
  <div class="pull-left gp-min-sign" aria-hidden="true">
    <span v-if="last">&lt;</span>
    <span v-else>≥</span>
  </div>
  <div v-if="last">
    <span class="sr-only">{{ gettext("grade_scale_limit_pre") }}</span>
    <span class="pull-left col-xs-4 gp-calc-percentage"></span>
    <span class="sr-only">{{ gettext("grade_scale_limit_post") }}{{ grade }}.</span>
  </div>
  <div v-else>
    <span class="pull-left col-xs-4 gp-calc-percentage">
      <input
        type="text"
        :id="`min-percentage-${index}`"
        name="min-percentage"
        :value="minPercentage"
        :title="gettext('grade_scale_input_title') + grade"
        class="form-control gp-calc-input-percentage"
        required />
      <label for="`min-percentage-${index}`" class="calculator-err">
        <span class="sr-only"></span>
        <span class="pull-left gp-calc-err"></span>
      </label>
    </span>
  </div>
  <div class="gp-scale-row-grade">
    <span class="gp-percent-sign" aria-hidden="true">%</span>
    <div style="display:inline;">
      <span class="gp-calc-equals" aria-hidden="true">=</span>
      <span class="gp-calc-grade" aria-hidden="true">{{ grade }}</span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    minPercentage: {
      type: Number,
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
};
</script>
