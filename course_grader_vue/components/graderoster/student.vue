<template>
  <div>
    <h3>{{ student.student_lastname }}, {{ student.student_firstname }}</h3>
    <div>
      <span class="offcanvas">Section:</span> {{ student.section_id }},
      <span v-if="student.student_credits">
        <span class="offcanvas">Student credits:</span> {{ student.student_credits }} CR,
      </span>
      <span class="offcanvas">Student number:</span> {{ student.student_number }}
      <span v-if="student.duplicate_code">
        <span class="offcanvas">Duplicate code:</span> {{ student.duplicate_code }}
      </span>
    </div>
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
