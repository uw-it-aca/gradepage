<template>
  <template v-if="student.is_auditor">
    <span class="text-uppercase fs-5 fw-bold">Auditor</span>
  </template>
  <template v-else-if="student.is_withdrawn">
    <div class="text-uppercase fs-5 fw-bold">
      <span v-if="student.withdrawn_week">
        Withdrawn (week {{ student.withdrawn_week }})
      </span>
      <span v-else>Withdrawn</span>
    </div>
  </template>
  <template v-else>
    <span v-if="student.saved_grade.is_writing" class="me-2">
      <abbr title="Writing credit">W</abbr>
    </span>
    <template v-if="student.saved_grade.is_incomplete">
      <span class="visually-hidden">Review grade:</span>
      <span class="fs-2 fw-bold">I</span>
      <div class="small text-muted">
        (Incomplete) Default: {{ grade }}
      </div>
    </template>
    <template v-else>
      <template v-if="student.saved_grade.no_grade_now">
        <span class="visually-hidden">Review grade:</span>
        <span class="fs-2 fw-bold">X</span>
        <div class="small text-muted">(No grade now)</div>
      </template>
      <template v-else>
        <span class="visually-hidden">Review grade:</span>
        <span class="fs-2 fw-bold">{{ student.saved_grade.grade }}</span>
      </template>
    </template>
    <div v-if="student.date_graded" class="small text-muted">
      Submitted {{ priorGrade }} on {{ student.date_graded }}
    </div>
    <div v-if="student.grade_status" class="small text-muted">
      <span v-if="hasGradeError">Submitted with error: </span>
      {{ student.grade_status }}
    </div>
  </template>
</template>

<script>
import { useWorkflowStateStore } from "@/stores/state";

export default {
  name: "GradeReview",
  props: {
    student: {
      type: Object,
      required: true,
    },
  },
  setup() {
    const appState = useWorkflowStateStore();
    return {
      appState,
    };
  },
  computed: {
    hasGradeError() {
      return (this.student.grade_status_code !== '200');
    },
    showDateGraded() {
      return this.appState.graderoster.gradable_student_count > 0 ? true : false;
    },
    priorGrade() {
      if (this.student.date_graded) {
        if (this.student.no_grade_now) {
          return "X (No grade now)";
        } else if (this.student.has_incomplete) {
          return "Incomplete (Default " + this.student.grade + ")";
        } else {
          return this.student.grade;
        }
      }
    },
  },
};
</script>
