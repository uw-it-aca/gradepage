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
    <div v-if="student.grade_url && !reviewing" class="text-end">
      <GradeInput :student="student" :gradeChoices="gradeChoices"></GradeInput>
    </div>
    <div v-else class="text-end">
      <GradeStatic :student="student"></GradeStatic>
    </div>
  </div>
</template>

<script>
import GradeStatic from "@/components/graderoster/grade/static.vue";
import GradeInput from "@/components/graderoster/grade/input.vue";

export default {
  components: {
    GradeStatic,
    GradeInput,
  },
  props: {
    student: {
      type: Object,
      required: true,
    },
    gradeChoices: {
      type: Array,
      required: true,
    },
    reviewing: {
      type: Boolean,
      required: true,
      default: false,
    },
    last: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      studentsLoaded: false,
    };
  },
  mounted() {
    if (this.last) {
      // Let the parent know we are loaded
      this.$emit('update:studentsLoaded', true);
    }
  },
};
</script>
