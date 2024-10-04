<template>
  <div class="d-flex justify-content-between">
    <div>
      <div class="fs-4 text-uppercase">{{ student.student_lastname }}, {{ student.student_firstname }}</div>
      <div class="small text-muted">
        <span class="visually-hidden">Section:</span> {{ student.section_id }},
        <span v-if="student.student_credits">
          <span class="visually-hidden">Student credits:</span>
          {{ student.student_credits }} CR,
        </span>
        <span class="visually-hidden">Student number:</span>
        {{ student.student_number }}
        <template v-if="student.duplicate_code">
          <span class="visually-hidden">Duplicate code:</span>
          <abbr title="Duplicate Code" class="badge rounded-pill text-bg-secondary">
          {{ student.duplicate_code }}</abbr>
        </template>
      </div>
    </div>
    <div v-if="appState.editingGrades && student.grade_url" class="text-end">
      <GradeInput :student="student" :gradeChoices="gradeChoices"></GradeInput>
    </div>
    <div v-else-if="appState.reviewingConversion" class="text-end">
      <GradeImport :student="student"></GradeImport>
    </div>
    <div v-else class="text-end">
      <GradeStatic :student="student"></GradeStatic>
    </div>
  </div>
</template>

<script>
import GradeStatic from "@/components/grade/static.vue";
import GradeInput from "@/components/grade/input.vue";
import GradeImport from "@/components/grade/import.vue";
import { useWorkflowStateStore } from "@/stores/state";

export default {
  components: {
    GradeStatic,
    GradeInput,
    GradeImport,
  },
  props: {
    student: {
      type: Object,
      required: true,
    },
    gradeChoices: {
      type: Array,
      default: [],
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
