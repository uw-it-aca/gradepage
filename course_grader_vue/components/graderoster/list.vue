<template>
  <ul v-if="!graderoster.students" class="list-unstyled m-0">
    <li v-for="index in 10" class="border-top pt-2 mt-2">
      <BPlaceholder
        class="d-block bg-light-gray"
        style="height: 60px"
        animation="glow"
      />
    </li>
  </ul>
  <ul v-else class="list-unstyled m-0">
    <li
      v-for="student in graderoster.students"
      :key="student.item_id"
      class="border-top pt-2 mt-2"
    >
      <Student :student="student"></Student>
    </li>
  </ul>
</template>

<script>
import Student from "@/components/graderoster/student.vue";
import { BPlaceholder } from "bootstrap-vue-next";

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
