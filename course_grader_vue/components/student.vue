<template>
  <td scope="row">
    <div class="fs-4 text-uppercase">{{ student.student_lastname }}, {{ student.student_firstname }}</div>
    <div>
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
  </td>
  <td> {{ student.section_id }}</td>
  <td>{{ student.student_credits }}</td>
  <td>
    <div v-if="appState.editingGrades && student.grade_url">
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
  </td>

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
