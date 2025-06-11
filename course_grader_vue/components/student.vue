<template>
  <td scope="row">
    <div class="fs-4">
      {{ student.student_lastname }}, {{ student.student_firstname }}
    </div>
    <div>
      {{ student.student_number }}
      <template v-if="student.duplicate_code">
        <BBadge
          variant="secondary"
          pill
          class="text-secondary-emphasis bg-secondary-subtle fw-normal"
          >Duplicate Code: {{ student.duplicate_code }}</BBadge
        >
      </template>
    </div>
  </td>
  <td>{{ student.section_id }}</td>
  <td>{{ student.student_credits }}</td>
  <td>
    <template v-if="appState.editingGrades && student.grade_url">
      <GradeEdit :student="student" :grade-choices="gradeChoices" />
    </template>
    <template v-else-if="appState.reviewingGrades && student.grade_url">
      <GradeReview :student="student" />
    </template>
    <template v-else-if="appState.reviewingConversion">
      <GradeImport :student="student" />
    </template>
    <template v-else>
      <GradeConfirm :student="student" />
    </template>
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
  },
  setup() {
    const appState = useWorkflowStateStore();
    return {
      appState,
    };
  },
  computed: {
    gradeChoices() {
      return this.appState.graderoster.grade_choices[
        this.student.grade_choices_index];
    },
  },
};
</script>
