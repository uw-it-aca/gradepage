<template>
  <span v-if="student.saved_grade.is_writing" class="me-2">
    <abbr title="Writing credit">W</abbr>
  </span>
  <template v-if="student.saved_grade.is_incomplete">
    <div class="d-flex">
      <span class="fs-2 fw-bold">I</span>
      <div class="small">
        Incomplete (Default: {{ student.saved_grade.grade }})
      </div>
    </div>
  </template>
  <template v-else>
    <template v-if="student.saved_grade.no_grade_now">
      <div class="d-flex">
        <span class="fs-2 fw-bold">X</span>
        <div class="small">(No grade now)</div>
      </div>
    </template>
    <template v-else>
      <span class="fs-2 fw-bold">{{ student.saved_grade.grade }}</span>
    </template>
  </template>
  <div v-if="hasGradeError" class="small">
    Submitted with error: {{ student.grade_status }}
  </div>
  <div v-else-if="hasChangedGrade" class="small">
    {{ priorGradeText(student) }}
  </div>
</template>

<script>
import { priorGradeText } from "@/utils/grade";

export default {
  name: "GradeReview",
  props: {
    student: {
      type: Object,
      required: true,
    },
  },
  setup() {
    return {
      priorGradeText,
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
        this.student.date_graded &&
        this.student.grade_status_code === "220" &&
        (this.student.grade !== this.student.saved_grade.grade ||
          this.student.has_incomplete !==
            this.student.saved_grade.is_incomplete ||
          this.student.has_writing_credit !==
            this.student.saved_grade.is_writing)
      );
    },
  },
};
</script>
