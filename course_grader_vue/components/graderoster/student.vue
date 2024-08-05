<template>
  <div class="d-flex justify-content-between">
    <div>
      <div class="fs-4 text-uppercase">{{ student.student_lastname }}, {{ student.student_firstname }}</div>
      <div>
        <span class="offcanvas">Section:</span> {{ student.section_id }},
        <span v-if="student.student_credits">
          <span class="offcanvas">Student credits:</span>
          {{ student.student_credits }} CR,
        </span>
        <span class="offcanvas">Student number:</span>
        {{ student.student_number }}
        <span v-if="student.duplicate_code">
          <span class="offcanvas">Duplicate code:</span>
          {{ student.duplicate_code }}
        </span>
      </div>
    </div>
    <div>
      <template v-if="student.grade">{{ student.grade }}</template>
      <template v-if="student.is_writing_section"><abbr title="Writing Credit">W</abbr></template>
      <template v-if="student.is_auditor">AUDITOR</template>
      <template v-if="student.is_withdrawn">WITHDRAWN</template>
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
