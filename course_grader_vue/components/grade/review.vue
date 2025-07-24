<template>
  <template v-if="student.saved_grade.is_incomplete">
    <div class="d-flex align-items-center">
      <div class="border fs-2 fw-bold me-2 text-center" style="width:50px;">I</div>
      <div>
        <div>Incomplete (Default: {{ student.saved_grade.grade }})</div>
        <div v-if="student.saved_grade.is_writing">Writing</div>
      </div>
    </div>
  </template>
  <template v-else>
    <template v-if="student.saved_grade.no_grade_now">
      <div class="d-flex align-items-center">
        <div class="border fs-2 fw-bold me-2 text-center" style="width:50px;">X</div>
        <div>
          <div>(No grade now)</div>
          <div v-if="student.saved_grade.is_writing">Writing</div>
        </div>
      </div>
    </template>
    <template v-else>
      <div class="d-flex align-items-center">
        <div class="border fs-2 fw-bold me-2 text-center" style="width:50px;">{{ student.saved_grade.grade }}</div>
        <div>
          <div v-if="student.saved_grade.is_writing">Writing</div>
        </div>
      </div>
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
