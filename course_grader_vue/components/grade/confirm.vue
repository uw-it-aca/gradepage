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
    <span v-if="student.has_writing_credit" class="me-2">
      <abbr title="Writing credit">W</abbr>
    </span>
    <template v-if="student.has_incomplete">
      <span class="visually-hidden">Submitted grade:</span>
      <span class="fs-2 fw-bold">I</span>
      <div class="small">(Incomplete) Default: {{ student.grade }}</div>
    </template>
    <template v-else>
      <template v-if="student.no_grade_now">
        <span class="visually-hidden">Submitted grade:</span>
        <span class="fs-2 fw-bold">X</span>
        <div class="small">(No grade now)</div>
      </template>
      <template v-else>
        <span class="visually-hidden">Submitted grade:</span>
        <span class="fs-2 fw-bold">{{ student.grade }}</span>
      </template>
    </template>
    <div v-if="hasChangedGrade" class="small">
      TODO: {{ student.grade_status }}
    </div>
    <div v-if="hasGradeError" class="small">
      Submitted with error: {{ student.grade_status }}
    </div>
  </template>
</template>

<script>
import { useWorkflowStateStore } from "@/stores/state";

export default {
  name: "GradeConfirm",
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
      return this.student.grade_status_code === null ||
        this.student.grade_status_code === "" ||
        this.student.grade_status_code === "200" ||
        this.student.grade_status_code === "220"
        ? false
        : true;
    },
    hasChangedGrade() {
      return (
        this.student.date_graded && this.student.grade_status_code === "220"
      );
    },
  },
};
</script>
