<template>
  <div class="d-flex justify-content-between">
    <div class="w-50">
      <div class="fs-4 text-uppercase">
        {{ student.student_lastname }}, {{ student.student_firstname }}
      </div>
      <div>
        <span class="visually-hidden">Section:</span> {{ student.section_id }},
        <span v-if="student.student_credits">
          <span class="visually-hidden">Student credits:</span>
          {{ student.student_credits }} CR,
        </span>
        <span class="visually-hidden">Student number:</span>
        {{ student.student_number }}
        <template v-if="student.duplicate_code">
          <BBadge
            variant="secondary"
            pill
            class="text-secondary-emphasis bg-secondary-subtle fw-normal"
            >Duplicate {{ student.duplicate_code }}</BBadge
          >
        </template>
      </div>
    </div>
    <div v-if="appState.editingGrades && student.grade_url" class="w-50">
      <GradeEdit :student="student" :grade-choices="gradeChoices" />
    </div>
    <div v-else-if="appState.reviewingGrades && student.grade_url" class="">
      <GradeReview :student="student" />
    </div>
    <div v-else-if="appState.reviewingConversion" class="">
      <GradeImport :student="student" />
    </div>
    <div v-else class="w-25">
      <GradeConfirm :student="student" />
    </div>
  </div>
</template>

<script>
import GradeEdit from "@/components/grade/edit.vue";
import GradeReview from "@/components/grade/review.vue";
import GradeImport from "@/components/grade/import.vue";
import GradeConfirm from "@/components/grade/confirm.vue";
import { useWorkflowStateStore } from "@/stores/state";

export default {
  name: "StudentComp",
  components: {
    GradeEdit,
    GradeReview,
    GradeConfirm,
    GradeImport,
  },
  props: {
    student: {
      type: Object,
      required: true,
    },
    gradeChoices: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  setup() {
    const appState = useWorkflowStateStore();
    return {
      appState,
    };
  },
};
</script>
