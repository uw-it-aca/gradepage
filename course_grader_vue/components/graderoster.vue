<template>
  <BCard class="shadow-sm rounded-3 my-4" header-class="p-3" header="Default">
    <template #header>
      <div class="">
        <div v-if="studentsLoaded" class="fs-5 text-muted fw-light">
          {{ graderosterTitle }}
        </div>
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
          >{{ gettext("sln") }}
          <BPlaceholder
            v-if="!section.section_sln"
            class="bg-light-gray"
            width="5"
            animation="glow"
          />{{ section.section_sln }}</span
        >
        <div style="float: right">
          <BLink
            href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
            target="_blank"
            title="Information on assigning and submitting grades"
            >Info
          </BLink>
        </div>
      </div>
    </template>

    <!-- Row zero contains information -->
    <div v-if="reviewing">
      {{ gettext("please_review_grades") }}
    </div>
    <div v-else-if="editing">
      <span
        v-if="graderoster.is_writing_section"
        v-html="gettext('writing_course_note')"
      />
    </div>
    <div v-else-if="studentsLoaded">
      <ConfirmationHeader :section="section" :graderoster="graderoster" />
    </div>

    <div class="d-flex justify-content-between">
      <div>
        <template
          v-if="graderoster.has_duplicate_codes"
          class="mb-2 small text-muted"
        >
          {{ gettext("duplicate_code") }}
          <i class="bi bi-circle-fill text-secondary"></i>
        </template>
      </div>
      <div>
        <GradeImport />
      </div>
    </div>

    <!-- Student roster -->
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
          :gradeChoices="graderoster.grade_choices[student.grade_choices_index]"
          :reviewing="reviewing"
          :last="index === graderoster.students.length - 1"
          v-model:studentsLoaded="studentsLoaded"
        />
      </li>
    </ul>

    <template #footer>
      <div v-if="reviewing">
        <span>{{ gettext("review_warning") }}</span>
        <button>{{ gettext("btn_review_back") }}</button>
        <button>{{ gettext("btn_submit_grades") }}</button>
      </div>
      <div v-else-if="editing">
        <span v-if="gradesRemainingText">{{ gradesRemainingText }}</span>
        <span v-else class="visually-hidden">
          All grades entered. Click Review button to continue.
        </span>
        <button
          :disabled="reviewDisabled"
          @click="reviewGrades"
        >{{ gettext("btn_review_submit") }}</button>
      </div>
    </template>
  </BCard>
</template>

<script>
import ConfirmationHeader from "@/components/graderoster/header/confirmation.vue";
import Student from "@/components/graderoster/student.vue";
import GradeImport from "@/components/gradeimport/import.vue";
import { useGradeStore } from "@/stores/grade";
import { updateGraderoster, submitGraderoster } from "@/utils/data";
import { BButton, BCard, BLink, BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    ConfirmationHeader,
    Student,
    GradeImport,
    BButton,
    BCard,
    BLink,
    BPlaceholder,
  },
  setup() {
    const gradeStore = useGradeStore();
    return {
      gradeStore,
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
      reviewing: false,
      studentsLoaded: false,
    };
  },
  computed: {
    editing() {
      return this.unsubmitted > 0;
    },
    graderosterTitle() {
      return this.reviewing
        ? gettext("review_submit_grades")
        : this.unsubmitted
        ? gettext("enter_grades")
        : gettext("submitted_grades_for");
    },
    gradesRemainingText() {
      var s = [],
        missing = this.gradeStore.missing,
        invalid = this.gradeStore.invalid;

      if (missing) {
        s.push((missing > 1) ? `${missing} grades missing` : "1 grade missing");
      }
      if (invalid) {
        s.push((invalid > 1) ? `${invalid} grades invalid` : "1 grade invalid");
      }
      return s.join(", ");
    },
    reviewDisabled() {
      return this.gradeStore.missing || this.gradeStore.invalid;
    },
  },
  methods: {
    reviewGrades: function () {
      if (this.reviewDisabled) {
        return;
      }

      this.updateGraderoster(this.section.graderoster_url,
                             this.gradeStore.grades)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.reviewing = true;
          this.graderoster = data;
        })
        .catch((error) => {
          console.log(error.message);
          this.gradeError = error.message;
        });
    },
    submitGrades: function () {},
  },
  created() {
    this.gradeStore.$reset();
  },
};
</script>
