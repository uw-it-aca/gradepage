<template>
  <div>
    {{ graderoster.failed_submission_count }}
    <ul>
      <li v-for="student in graderoster.students" :key="student.item_id">
        <Student :student="student"></Student>
      </li>
    </ul>
  </div>
</template>

<script>
import Student from "@/components/graderoster/student.vue";

export default {
  components: {
    Student,
  },
  props: {
    graderoster: {
      type: Object,
      required: true,
    },
  },
  methods: {
  },
};
</script>
