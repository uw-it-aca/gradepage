<template>
  <div>
    <span v-if="student.is_override_grade">
      <span class="fa-stack" title="Override grade imported from Canvas Gradebook">
        <i class="fas fa-circle fa-stack-2x" aria-hidden="true"></i>
        <i class="fas fa-marker fa-flip-horizontal fa-stack-1x fa-inverse" aria-hidden="true"></i>
      </span>
    </span>
    {{ student.imported_grade }}%
    <span class="visually-hidden">{{ gettext("conversion_confirm_grade_text") }}</span>
    <i class="fas fa-long-arrow-alt-right"></i>
    <strong>{{ student.converted_grade }}</strong>
  </div>
</template>

<script>
export default {
  props: {
    student: {
      type: Object,
      required: true,
    },
  },
};
</script>
