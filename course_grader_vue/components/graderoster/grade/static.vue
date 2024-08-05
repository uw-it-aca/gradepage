<template>
  <template v-if="student.is_auditor">
    <span class="text-uppercase fs-5 fw-bold">Auditor</span>
  </template>
  <template v-else-if="student.is_withdrawn">
    <div class="text-uppercase fs-5 fw-bold">Withdrawn</div>
    <div v-if="student.withdrawn_week"> Week {{ student.withdrawn_week }}</div>
  </template>
  <template v-else>
    <span v-if="student.has_writing_credit" class="me-2"><abbr title="Writing credit">W</abbr></span>
    <template v-if="student.has_incomplete">
      <span class="visually-hidden">Submitted grade:</span>
      <span class="fs-2 fw-bold">I</span>
      <div class="small text-muted">(Incomplete) Default: {{ student.grade }}</div>
    </template>
    <template v-else>
      <template v-if="student.no_grade_now">
        <span class="visually-hidden">Submitted grade:</span>
        <span class="fs-2 fw-bold">X</span>
        <div class="small text-muted">(No grade now)</div>
      </template>
      <template v-else>
        <span class="visually-hidden">Submitted grade:</span>
        <span class="fs-2 fw-bold">{{ student.grade }}</span>
      </template>
    </template>
    <div v-if="student.date_graded" class="small text-muted">
      Submitted {{ student.date_graded }}
    </div>
    <div v-if="student.grade_status" class="small text-muted">
      Submitted with error: {{ student.grade_status }}
    </div>
  </template>
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
