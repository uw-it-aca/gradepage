<template>
  <BCard class="shadow-sm rounded-3" header-class="p-3" header="Default">
    <template #header>
      <div v-if="section">
        <GradeImportOptions
          :section="section"
          :expected-grade-count="appState.unsubmitted"
        />
      </div>

      <SectionHeader :section="section" :title="gettext('enter_grades')" />

      <div
        v-if="appState.graderoster.is_writing_section"
        class="bg-body-secondary p-3 rounded-3"
      >
        <div class="small" role="status">
          {{ gettext("writing_course_note_receipt") }}
        </div>
      </div>
    </template>

    <template v-if="errorResponse">
      <Errors :error-response="errorResponse" />
    </template>
    <template v-else-if="appState.graderoster">
      <div v-if="appState.graderoster.has_duplicate_codes"
        class="mb-2 pb-2 small text-muted border-bottom"
      >
        {{ gettext("duplicate_code") }}
        <i class="bi bi-circle-fill text-secondary"></i>
      </div>
    </template>

    <ul v-if="appState.graderoster.students" class="list-unstyled m-0">
      <li
        v-for="(student, index) in appState.graderoster.students"
        :key="student.item_id"
        class="bpt-2 mt-2"
        :class="index != 0 ? 'border-top' : ''"
      >
        <Student
          :student="student"
          :gradeChoices="appState.graderoster.grade_choices[student.grade_choices_index]"
        />
      </li>
    </ul>
    <ul v-else-if="!errorResponse" class="list-unstyled m-0">
      <li v-for="index in 8" class="border-top pt-2 mt-2" :key="index">
        <BPlaceholder
          class="d-block bg-body-secondary"
          style="height: 60px"
          animation="glow"
        />
      </li>
    </ul>

    <template #footer>
      <div class="d-flex">
        <div class="flex-fill align-self-center text-end me-2 small">
          <span v-if="gradesRemainingText">{{ gradesRemainingText }} </span>
          <span v-else class="visually-hidden">
            All grades entered. Click Review button to continue.
          </span>
        </div>
        <BButton
          :disabled="reviewDisabled"
          variant="primary"
          @click="reviewGrades"
        >{{ gettext("btn_review_submit") }}
        </BButton>
      </div>
    </template>
  </BCard>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import Errors from "@/components/errors.vue";
import GradeImportOptions from "@/components/import/source-options.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { useGradeStore } from "@/stores/grade";
import { updateGraderoster } from "@/utils/data";
import { BCard, BButton, BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    SectionHeader,
    GradeImportOptions,
    Student,
    Errors,
    BCard,
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
    const gradeStore = useGradeStore();
    return {
      appState,
      gradeStore,
      updateGraderoster,
    };
  },
  data() {
    return {
      errorResponse: null,
    };
  },
  computed: {
    gradesRemainingText() {
      var s = [],
        missing = this.gradeStore.missing,
        invalid = this.gradeStore.invalid;

      if (missing) {
        s.push(missing > 1 ? `${missing} grades missing` : "1 grade missing");
      }
      if (invalid) {
        s.push(invalid > 1 ? `${invalid} grades invalid` : "1 grade invalid");
      }
      return s.join(", ");
    },
    reviewDisabled() {
      return this.gradeStore.missing > 0 || this.gradeStore.invalid > 0
        ? true
        : false;
    },
  },
  methods: {
    reviewGrades: function () {
      this.updateGraderoster(
        this.section.graderoster_url, this.gradeStore.grades
      )
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.appState.setGraderoster(data.graderoster);
          this.appState.reviewGrades();
        })
        .catch((error) => {
          this.errorResponse = error.response;
        });
    },
  },
};
</script>
