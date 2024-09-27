<template>
  <Layout :page-title="pageTitle">
    <template #content>
      <!-- grade submission in progress -->
      <BAlert
        v-if="graderoster.has_inprogress_submissions"
        variant="info"
        :model-value="true"
        class="small d-flex align-items-center"
      >
        <div class="flex-fill me-3">
          <i class="bi bi-exclamation-circle-fill me-1"></i>
          {{ gettext("grade_submission_inprogress") }}.
          {{ gettext("in_progress_submission_email") }}
        </div>
        <div>
          <BLink
            class="btn btn-info btn-sm rounded-3 text-nowrap"
            :href="section.term_url"
            >Return to class list</BLink
          >
        </div>
      </BAlert>

      <!-- graderoster header -->
      <BCard class="shadow-sm rounded-3" header-class="p-3" header="Default">
        <template #header>
          <!-- section actions dropdown -->
          <template v-if="studentsLoaded && !reviewing && !editing">
            <BDropdown
              v-model="showSectionOptions"
              size="sm"
              variant="outline-secondary"
              no-caret
              class="float-end d-inline-block"
              toggle-class="rounded-2"
            >
              <template #button-content>
                <i class="bi bi-three-dots"></i
              ></template>
              <BDropdownItem :href="section.export_url">
                <i class="bi bi-download me-2 text-body-tertiary"></i>Download Change of Grade
              </BDropdownItem>
              <BDropdownItem href="javascript:window.print()">
                <i class="bi bi-printer me-2 text-body-tertiary"></i>Print this page
              </BDropdownItem>
              <BDropdownDivider />
              <BDropdownItem
                href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
                target="_blank"
                title="Information on assigning and submitting grades"
                ><i class="bi bi-question-circle me-2 text-body-tertiary"></i>GradePage Help
              </BDropdownItem>
            </BDropdown>
          </template>

          <template v-if="editing">
            <GradeImportOptions
              :section="section"
              :expected-grade-count="unsubmitted"
            />
          </template>

          <SectionHeader :section="section" :title="headerTitle" />

          <div
            v-if="
              !graderoster.is_submission_confirmation ||
              graderoster.is_writing_section
            "
            class="bg-body-secondary p-3 rounded-3"
          >
            <!-- submission disclaimer -->
            <div
              v-if="!graderoster.is_submission_confirmation"
              class="small"
              role="status"
            >
              {{ gettext("confirmation_alert_warning") }}
              <BLink
                href="https://registrar.washington.edu/staffandfaculty/grading-resources/#faqs"
                target="_blank"
                class="d-print-none"
                >More info.
              </BLink>
            </div>
            <!-- writing credit disclaimer -->
            <div
              v-if="graderoster.is_writing_section"
              class="small"
              role="status"
            >
              {{ gettext("writing_course_note_receipt") }}
            </div>
          </div>
        </template>

        <!-- Row zero contains errors, information and import action -->
        <template v-if="errorResponse">
          <Errors :error-response="errorResponse" />
        </template>
        <template v-else-if="studentsLoaded">
          <div v-if="reviewing">
            {{ gettext("please_review_grades") }}
          </div>
          <template v-else>
            <Receipt :section="section" :graderoster="graderoster" />
          </template>

          <div
            v-if="graderoster.has_duplicate_codes"
            class="mb-2 pb-2 small text-muted border-bottom"
          >
            {{ gettext("duplicate_code") }}
            <i class="bi bi-circle-fill text-secondary"></i>
          </div>
        </template>

        <!-- Student roster -->
        <ul v-if="graderoster.students" class="list-unstyled m-0">
          <li
            v-for="(student, index) in graderoster.students"
            :key="student.item_id"
            class="bpt-2 mt-2"
            :class="index != 0 ? 'border-top' : ''"
          >
            <Student
              :student="student"
              :gradeChoices="
                graderoster.grade_choices[student.grade_choices_index]
              "
              :reviewing="reviewing"
              :last="index === graderoster.students.length - 1"
              v-model:studentsLoaded="studentsLoaded"
            />
          </li>
        </ul>
        <ul v-else-if="!errorResponse" class="list-unstyled m-0">
          <li v-for="index in 10" class="border-top pt-2 mt-2">
            <BPlaceholder
              class="d-block bg-light-gray"
              style="height: 60px"
              animation="glow"
            />
          </li>
        </ul>

        <!-- Grade edit/review actions -->
        <template #footer v-if="reviewing">
          <div class="d-flex">
            <div class="flex-fill align-self-center text-end me-2 small">
              {{ gettext("review_warning") }}
            </div>
            <div class="text-nowrap">
              <BButton
                :title="`Go back and edit grades for ${section.section_name}`"
                variant="outline-primary"
                @click="loadGraderoster"
                >{{ gettext("btn_review_back") }}
              </BButton>
              <BButton variant="primary" @click="submitGrades" class="ms-2"
                >{{ gettext("btn_submit_grades") }}
              </BButton>
            </div>
          </div>
        </template>
        <template #footer v-else-if="studentsLoaded && editing">
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
            >
              {{ gettext("btn_review_submit") }}
            </BButton>
          </div>
        </template>
      </BCard>
    </template>
  </Layout>
</template>

<script>
import Layout from "@/layouts/default.vue";
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/graderoster/student.vue";
import GradeImportOptions from "@/components/section/import-options.vue";
import Receipt from "@/components/graderoster/receipt.vue";
import Errors from "@/components/errors.vue";
import { useGradeStore } from "@/stores/grade";
import {
  getSection,
  getGraderoster,
  updateGraderoster,
  submitGraderoster,
} from "@/utils/data";
import {
  BAlert,
  BButton,
  BCard,
  BDropdown,
  BDropdownItem,
  BLink,
  BPlaceholder,
} from "bootstrap-vue-next";
import { ref } from "vue";

export default {
  components: {
    Layout,
    SectionHeader,
    Student,
    GradeImportOptions,
    Receipt,
    Errors,
    BAlert,
    BButton,
    BCard,
    BDropdown,
    BDropdownItem,
    BLink,
    BPlaceholder,
  },
  setup() {
    const gradeStore = useGradeStore();
    const showSectionOptions = ref(false);
    return {
      gradeStore,
      getSection,
      getGraderoster,
      updateGraderoster,
      submitGraderoster,
      showSectionOptions,
    };
  },
  data() {
    return {
      studentsLoaded: false,
      isLoading: true,
      section: {},
      graderoster: {},
      reviewing: false,
      pageTitle: "Course Section",
      errorResponse: null,
    };
  },
  computed: {
    unsubmitted() {
      return this.graderoster.students.filter((s) => s.grade_url !== null)
        .length;
    },
    editing() {
      return this.unsubmitted > 0;
    },
    headerTitle() {
      return this.studentsLoaded
        ? this.reviewing
          ? gettext("review_submit_grades")
          : this.editing
          ? gettext("enter_grades")
          : gettext("submitted_grades_for")
        : this.errorResponse
        ? ""
        : "Loading...";
    },
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
    loadGraderoster: function () {
      if (this.section.graderoster_url) {
        this.getGraderoster(this.section.graderoster_url)
          .then((response) => {
            return response.data;
          })
          .then((data) => {
            this.reviewing = false;
            this.gradeStore.$reset();
            this.graderoster = data.graderoster;
          })
          .catch((error) => {
            this.errorResponse = error.response;
          })
          .finally(() => {
            this.isLoading = false;
          });
      } else {
        this.isLoading = false;
      }
    },
    reviewGrades: function () {
      this.isLoading = true;
      this.updateGraderoster(
        this.section.graderoster_url,
        this.gradeStore.grades
      )
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.reviewing = true;
          this.graderoster = data.graderoster;
          this.isLoading = false;
        })
        .catch((error) => {
          this.errorResponse = error.response;
        });
    },
    submitGrades: function () {
      if (this.reviewing) {
        this.isLoading = true;
        this.submitGraderoster(this.section.graderoster_url, {})
          .then((response) => {
            return response.data;
          })
          .then((data) => {
            this.reviewing = false;
            this.graderoster = data.graderoster;
            this.isLoading = false;
          })
          .catch((error) => {
            this.errorResponse = error.response;
          });
      }
    },
    loadSection: function () {
      let section_id = this.$route.params.id;
      this.getSection("/api/v1/section/" + section_id)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.section = data.section;
          // this.pageTitle = this.section.section_name;
          // document.title = this.pageTitle + " - GradePage";
          document.title = this.section.section_name + " - GradePage";
          this.loadGraderoster();
        })
        .catch((error) => {
          this.errorResponse = error.response;
          this.isLoading = false;
        });
    },
  },
  created() {
    this.loadSection();
  },
};
</script>
