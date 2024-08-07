<template>

  <BCard
    class="shadow-sm rounded-3 my-4"
    header-class="p-3"
    header="Default"
  >
    <template #header>
      <div class="">
        <div class="fs-5 text-muted fw-light">{{ graderosterTitle }}</div>
        <span class="fs-2 m-0 me-3">
          <BPlaceholder
            v-if="!section.section_name"
            class="bg-light-gray"
            width="15"
            animation="glow"
          />{{ section.section_name }}
        </span>
        <span class="small"
          >SLN
          <BPlaceholder
            v-if="!section.section_sln"
            class="bg-light-gray"
            width="5"
            animation="glow"
          />{{ section.section_sln }}</span
        >
      </div>
    </template>

    <div v-if="reviewing">
      Please review grades and submit below.
    </div>
    <div v-if="graderoster.is_writing_section">
      <span v-if="editing">
        <strong>Note:</strong> Writing credit automatically given to all students with a passing grade in this course.
      </span>
      <span v-else>
        Writing credit automatically given to all students with a passing grade in this course.
      </span>
    </div>
    <div v-if="graderoster.has_duplicate_codes" class="mb-2 small text-muted">
      Duplicate Code <i class="bi bi-circle-fill text-secondary"></i>
    </div>

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
        <Student :student="student" :reviewing="reviewing"></Student>
      </li>
    </ul>

    <template v-if="reviewing">
      <div>
        All grades will be submitted to the Registrar as displayed above.
        No further online changes will be possible after submission.
      </div>
      <button>Back</button> <button>Review</button>
    </template>
    <template v-else-if="editing">
      <div class="border-top pt-2 mt-2">
        <span>{{ gradesRemaining }} grades remaining</span>
        <button disabled="disabled">Submit grades</button>
      </div>
    </template>

  </BCard>
</template>

<script>
import Student from "@/components/graderoster/student.vue";
import { BPlaceholder } from "bootstrap-vue-next";
import { updateGraderoster, submitGraderoster } from "@/utils/data";

export default {
  components: {
    Student,
  },
  setup() {
    return {
      updateGraderoster,
      submitGraderoster,
    };
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
    graderoster: {
      type: Object,
      required: true,
    },
    unsubmitted: {
      type: Number,
      required: true,
      default: 0,
    },
  },
  data() {
    return {
      reviewing: false,
    };
  },
  computed: {
    editing() {
      return this.unsubmitted > 0;
    },
    graderosterTitle() {
      return (this.unsubmitted) ? "Enter grades for" : "Grade Receipt for";
    },
    gradesRemaining() {
      return this.unsubmitted;  // TODO: calculate empty inputs
    },
  },
  methods: {
    reviewGrades: function() {
    },
    submitGrades: function() {
    },
  },
};
</script>
