<template>
  <div>
    <h3>{{ student.student_lastname }}, {{ student.student_firstname }}</h3>
    <div>
      <span class="offcanvas">Section:</span> {{ student.section_id }},
      <span v-if="student.student_credits">
        <span class="offcanvas">Student credits:</span> {{ student.student_credits }} CR,
      </span>
      <span class="offcanvas">Student number:</span> {{ student.student_number }}
      <span v-if="student.duplicate_code">
        <span class="offcanvas">Duplicate code:</span> {{ student.duplicate_code }}
      </span>
    </div>
    <div v-if="student.grade_url">
      <GradeInput :student="student"></GradeInput>
    </div>
    <div v-else>
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
  },
};
</script>
