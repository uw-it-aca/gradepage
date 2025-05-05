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
        Incomplete (Default: {{ student.saved_grade.grade }})
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
    <div v-if="hasChangedGrade(student)" class="small text-muted">
      {{ changedGradeText(student) }}
    </div>
    <div v-if="hasGradeError" class="small text-muted">
      Submitted with error: {{ student.grade_status }}
    </div>
  </template>
</template>

<script>
import { useWorkflowStateStore } from "@/stores/state";
import { hasChangedGrade, changedGradeText } from "@/utils/grade";

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
      hasChangedGrade,
      changedGradeText,
    };
  },
  computed: {
    hasGradeError() {
      return (this.student.grade_status_code === null ||
        this.student.grade_status_code === "" ||
        this.student.grade_status_code === "200" ||
        this.student.grade_status_code === "220") ? false : true;
    },
  },
};
</script>
