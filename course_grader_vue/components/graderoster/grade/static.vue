<template>
  <div v-if="student.is_auditor">
    <span>Auditor</span>
  </div>
  <div v-else-if="student.is_withdrawn">
    Withdrawn<span v-if="student.withdrawn_week"> {{ student.withdrawn_week }}</span>
  </div>
  <div v-else>
    <span v-if="student.has_writing_credit"><abbr title="Writing credit">W</abbr></span>
    <div v-if="student.has_incomplete">
      <span>Submitted grade:</span>
      <strong><abbr title="Incomplete">I</abbr></strong>
      <div>Default: {{ student.grade }}"</div>
    </div>
    <div v-else>
      <div v-if="student.no_grade_now">
        <span>Submitted grade:</span><strong>X</strong>
        <div>(No grade now)</div>
      </div>
      <div v-else>
        <span>Submitted grade:</span>
        <strong>{{ student.grade }}</strong>
      </div>
    </div>
    <div v-if="student.date_graded">
      Submitted {{ student.date_graded }}
    </div>
    <div v-if="student.grade_status">
      Submitted with error: {{ student.grade_status }}
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
