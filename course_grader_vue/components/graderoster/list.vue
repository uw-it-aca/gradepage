<template>
  <div>
    <template v-else>
      <ul>
        <li v-for="student in graderoster.students" :key="student.item_id">
          <Student :student="student"></Student>
        </li>
      </ul>
    </template>
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
  setup() {
    return {
    };
  },
  data() {
    return {
    };
  },
  methods: {
  },
};
</script>
