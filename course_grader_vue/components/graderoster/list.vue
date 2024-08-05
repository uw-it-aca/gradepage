<template>
  <div>
    <ul class="list-unstyled">
      <li v-for="student in graderoster.students" :key="student.item_id" class="mb-3">
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
};
</script>
