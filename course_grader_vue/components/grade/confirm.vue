<template>
  <template v-if="student.is_auditor">
    <div class="d-flex align-items-center">
      <div class="border fs-2 fw-bold me-2 text-center">Auditor</div>
      <div>
        <div>&nbsp;</div>
      </div>
    </div>
  </template>
  <template v-else-if="student.date_withdrawn">
    <div class="d-flex align-items-center">
      <div class="border fs-2 fw-bold me-2 text-center">
        {{ withdrawnLabel }}
      </div>
      <div>
        <div>&nbsp;</div>
      </div>
    </div>
  </template>
  <template v-else-if="hasGradeError">
    <div class="d-flex align-items-center">
      <div v-if="student.grade_status" class="small">
        {{ student.grade_status }}
      </div>
      <div>
        <div>&nbsp;</div>
      </div>
    </div>
  </template>
  <template v-else>
    <template v-if="student.has_incomplete">
      <div class="d-flex align-items-center">
        <div class="border fs-2 fw-bold me-2 text-center" style="width: 50px">
          I
        </div>
        <div>
          <div>Incomplete (Default: {{ student.grade }})</div>
          <div v-if="student.has_writing_credit">Writing</div>
        </div>
      </div>
    </template>
    <template v-else>
      <template v-if="student.no_grade_now">
        <div class="d-flex align-items-center">
          <div class="border fs-2 fw-bold me-2 text-center" style="width: 50px">
            X
          </div>
          <div>
            <div>(No grade now)</div>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="d-flex align-items-center">
          <div class="border fs-2 fw-bold me-2 text-center" style="width: 50px">
            {{ student.grade }}
          </div>
          <div>
            <div v-if="student.has_writing_credit">Writing</div>
          </div>
        </div>
      </template>
    </template>
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
      return this.student.date_graded &&
        (this.student.grade_status_code === null ||
          this.student.grade_status_code === "" ||
          this.student.grade_status_code === "200" ||
          this.student.grade_status_code === "220")
        ? false
        : true;
    },
  },
};
</script>
