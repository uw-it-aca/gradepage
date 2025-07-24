<template>
  <div>
    <span class="fs-2 fw-bold">{{ student.converted_grade }}</span>
  </div>
  <div v-if="student.is_override_grade" class="small">
    Override grade imported from Canvas Gradebook
  </div>
</template>

<script>
export default {
  name: "GradeImport",
  props: {
    student: {
      type: Object,
      required: true,
    },
  },
};
</script>
