<template>

  <BCard
    class="shadow-sm rounded-3 my-4"
    header-class="p-3"
    header="Default"
  >
    <template #header>
      <div class="">
        <div v-if="studentsLoaded" class="fs-5 text-muted fw-light">{{ graderosterTitle }}</div>
        <div v-else class="fs-5 text-muted fw-light">Loading...</div>
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
      {{ gettext("please_review_grades") }}
    </div>
    <div v-else-if="editing">
      <span v-if="graderoster.is_writing_section">
        {{ gettext("writing_course_note") }}
      </span>
    </div>
    <div v-else>
      <ConfirmationHeader :section="section" :graderoster="graderoster"></ConfirmationHeader>
    </div>

    <div v-if="graderoster.has_duplicate_codes" class="mb-2 small text-muted">
      {{ gettext("duplicate_code") }} <i class="bi bi-circle-fill text-secondary"></i>
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
        v-for="(student, index) in graderoster.students"
        :key="student.item_id"
        class="border-top pt-2 mt-2"
      >
        <Student
          :student="student"
          :reviewing="reviewing"
          :last="index === graderoster.students.length - 1"
          v-model:studentsLoaded="studentsLoaded"></Student>
      </li>
    </ul>

    <template v-if="reviewing">
      <div>{{ gettext("review_warning") }}</div>
      <button>Back</button> <button>Review</button>
    </template>
    <template v-else-if="editing">
      <div class="border-top pt-2 mt-2">
        <span v-if="gradesRemainingText">{{ gradesRemainingText }}</span>
        <span v-else class="visually-hidden">
          All grades entered. Click Review button to continue.
        </span>
        <button disabled="disabled">Submit grades</button>
      </div>
    </template>

  </BCard>
</template>

<script>
import ConfirmationHeader from "@/components/graderoster/header/confirmation.vue";
import Student from "@/components/graderoster/student.vue";
import { updateGraderoster, submitGraderoster } from "@/utils/data";
import { BCard, BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    ConfirmationHeader,
    Student,
    BCard,
    BPlaceholder
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
      default: null,
    },
  },
  data() {
    return {
      incompleteBlocklist: [gettext("x_no_grade_now"), "N", "CR"],
      missingGrades: 0,
      invalidGrades: 0,
      reviewing: false,
      studentsLoaded: false,
    };
  },
  computed: {
    editing() {
      return this.unsubmitted > 0;
    },
    graderosterTitle() {
      return (this.reviewing) ? gettext("review_submit_grades") : (this.unsubmitted)
        ? gettext("enter_grades") : gettext("submitted_grades_for");
    },
    gradesRemainingText() {
      var s = [];
      if (this.missingGrades) {
        s.push(ngettext("%(missing_grades)s grade missing",
                        "%(missing_grades)s grades missing",
                        {missing_grades: this.missingGrades}));
      }
      if (this.invalidGrades) {
        s.push(ngettext("%(invalid_grades)s grade invalid",
                        "%(invalid_grades)s grades invalid",
                        {invalid_grades: this.invalidGrades}));
      }
      return s.join(", ");
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
