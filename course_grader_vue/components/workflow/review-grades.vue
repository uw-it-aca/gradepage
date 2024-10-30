<template>
  <BCard class="shadow-sm rounded-3" header-class="p-3" header="Default">
    <template #header>
      <SectionHeader :section="section" :title="gettext('review_submit_grades')" />

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
      <div>
        {{ gettext("please_review_grades") }}
      </div>

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
        <Student :student="student" />
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
          {{ gettext("review_warning") }}
        </div>
        <div v-if="section" class="text-nowrap">
          <BButton
            :title="`Go back and edit grades for ${section.section_name}`"
            variant="outline-primary"
            @click="editGrades"
            >{{ gettext("btn_review_back") }}
          </BButton>
          <BButton
            variant="primary"
            @click="submitGrades"
            class="ms-2"
            >{{ gettext("btn_submit_grades") }}
          </BButton>
        </div>
      </div>
    </template>
  </BCard>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import Errors from "@/components/errors.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { submitGraderoster } from "@/utils/data";
import { BCard, BButton, BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    SectionHeader,
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
  methods: {
    editGrades: function () {
      this.appState.editGrades();
    },
    submitGrades: function () {
      this.isLoading = true;
      this.submitGraderoster(this.section.graderoster_url, {})
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.appState.setGraderoster(data.graderoster);
        })
        .catch((error) => {
          this.errorResponse = error.response;
          this.isLoading = false;
        });
    },
  },
};
</script>
