<template>
  <div>
    <!-- TODO: what is this? -->
    <div v-if="student.is_override_grade" class="small">
      Override grade imported from Canvas Gradebook
    </div>
    <div class="d-flex align-items-center">
      <div class="border fs-2 text-center" style="width: 100px">
        {{ student.imported_grade }}%
      </div>
      <div class="mx-2 fs-4">
        <span class="visually-hidden">converted to</span>
        <i class="bi bi-arrow-right"></i>
      </div>
      <div class="border fs-2 fw-bold text-center" style="width: 100px">
        {{ student.converted_grade }}
      </div>
    </div>
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
