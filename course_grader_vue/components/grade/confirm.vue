<template>
  <template v-if="student.is_auditor">
    <span class="text-uppercase fs-5 fw-bold">Auditor</span>
  </template>
  <template v-else-if="student.date_withdrawn">
    <div class="text-uppercase fs-5 fw-bold">
      <span>{{ withdrawnLabel }}</span>
    </div>
  </template>
  <template v-else>
    <span v-if="student.has_writing_credit" class="me-2">
      <abbr title="Writing credit">W</abbr>
    </span>
    <template v-if="student.has_incomplete">
      <div class="d-flex">
        <span class="fs-2 fw-bold">I</span>
        <div class="small">
          Incomplete (Default: {{ student.grade }})
        </div>
      </div>
    </template>
    <template v-else>
      <template v-if="student.no_grade_now">
        <div class="d-flex">
          <span class="fs-2 fw-bold">X</span>
          <div class="small">(No grade now)</div>
        </div>
      </template>
      <template v-else>
        <span class="fs-2 fw-bold">{{ student.grade }}</span>
      </template>
    </template>
    <div v-if="hasGradeError" class="small">
      Submitted with error: {{ student.grade_status }}
    </div>
  </template>
</template>

<script>

export default {
  name: "GradeConfirm",
  props: {
    student: {
      type: Object,
      required: true,
    },
  },
  setup() {
    return {};
  },
  computed: {
    withdrawnLabel() {
      return this.student.grade !== null
        ? "Withdrawn " + "(" + this.student.grade + ")"
        : "Withdrawn";
    },
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
