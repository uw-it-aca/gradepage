<template>
  <SectionHeader :section="section" title="Review grades for" />

  <template v-if="isLoading">
    Please wait, submitting grades to the Registrar...
  </template>

  <Errors v-if="errorResponse" :error-response="errorResponse" />

  <template v-else-if="appState.graderoster">
    <div class="mb-2 pb-2 border-bottom">
      <div>Please review grades and submit below.</div>
      <div v-if="appState.graderoster.is_writing_section">
        Writing credit automatically given to all students with a passing grade
        in this course.
      </div>
      <div v-if="appState.graderoster.has_duplicate_codes">
        <span class="visually-hidden">
          In the list below, duplicate listings of the same student are
          differentiated with a
        </span>

        <BBadge
          variant="secondary"
          pill
          class="text-secondary-emphasis bg-secondary-subtle fw-normal"
          >Duplicate code</BBadge
        >
      </div>
    </div>

    <ul v-if="appState.graderoster.students" class="list-unstyled m-0">
      <li
        v-for="(student, index) in appState.graderoster.students"
        :key="student.item_id"
        class="bpt-2 mt-2"
        :class="index != 0 ? 'border-top' : ''"
      >
        <Student :student="student" />
      </li>
    </ul>
  </template>
  <template v-else>
    <ul class="list-unstyled m-0">
      <li v-for="index in 8" :key="index" class="border-top pt-2 mt-2">
        <BPlaceholder
          class="d-block bg-body-secondary"
          style="height: 60px"
          animation="glow"
        />
      </li>
    </ul>
  </template>

  <template v-if="!isLoading && !errorResponse">
    <div class="d-flex mt-4">
      <div class="flex-fill align-self-center text-end me-2">
        All grades will be submitted to the Registrar as displayed above.
      </div>
      <div v-if="section" class="text-nowrap">
        <BButton
          :title="reviewBackTitle"
          variant="outline-primary"
          @click="editGrades"
          >Edit</BButton
        >
        <BButton variant="primary" class="ms-2" @click="submitGrades"
          >Submit</BButton
        >
      </div>
    </div>
  </template>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import Errors from "@/components/errors.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { submitGraderoster } from "@/utils/data";
import { BButton, BPlaceholder, BBadge } from "bootstrap-vue-next";

export default {
  components: {
    SectionHeader,
    Student,
    Errors,
    BBadge,
    BButton,
    BPlaceholder,
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
  },
  setup() {
    const appState = useWorkflowStateStore();
    return {
      appState,
      submitGraderoster,
    };
  },
  data() {
    return {
      isLoading: false,
      errorResponse: null,
    };
  },
  computed: {
    reviewBackTitle() {
      return "Go back and edit grades for " + this.section.section_name;
    },
  },
  methods: {
    editGrades: function () {
      this.appState.editGrades();
    },
    submitGrades: function () {
      this.isLoading = true;
      this.submitGraderoster(this.section.graderoster_url, {})
        .then((data) => {
          this.appState.setGraderoster(data.graderoster);
        })
        .catch((error) => {
          this.errorResponse = error.data;
          this.isLoading = false;
        });
    },
  },
};
</script>
