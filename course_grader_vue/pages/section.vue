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
          <BLink
            href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
            target="_blank"
            title="Information on assigning and submitting grades"
            class="small float-end"
            >Learn more on assigning and submitting grades
          </BLink>

          <SectionHeader :section="section" :title="headerTitle" />



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

          <!-- grade receipt download and print button -->
          <div
            v-if="studentsLoaded && !reviewing && !editing"
            class="text-end"
          >
            <a
              :href="section.export_url"
              class="btn btn-sm btn-outline-secondary me-2 rounded-2"
              ><i class="bi bi-download"></i> Download Change of Grade
              template</a
            >
            <a
              href="javascript:window.print()"
              class="btn btn-sm btn-outline-primary rounded-2"
            >
              <i class="bi bi-printer"></i> Print this page
            </a>
          </div>

          <div v-if="editing" class="text-end">
            <GradeImport
              :section="section"
              :expected-grade-count="unsubmitted"
            />
          </div>
        </template>

        <!-- Row zero contains errors, information and import action -->
        <div v-if="errorResponse">
          <Errors :error-response="errorResponse" />
        </div>
        <div v-else-if="studentsLoaded">
          <div v-if="reviewing">
            {{ gettext("please_review_grades") }}
          </div>
          <div v-else>
            <Receipt :section="section" :graderoster="graderoster" />
          </div>

          <div
            v-if="graderoster.has_duplicate_codes"
            class="mb-2 small text-muted"
          >
            {{ gettext("duplicate_code") }}
            <i class="bi bi-circle-fill text-secondary"></i>
          </div>
        </div>

        <!-- Student roster -->
        <ul v-if="graderoster.students" class="list-unstyled m-0">
          <li
            v-for="(student, index) in graderoster.students"
            :key="student.item_id"
            class="border-top pt-2 mt-2"
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
import GradeImport from "@/components/graderoster/import.vue";
import Receipt from "@/components/graderoster/receipt.vue";
import Errors from "@/components/errors.vue";
import { useGradeStore } from "@/stores/grade";
import {
  getSection,
  getGraderoster,
  updateGraderoster,
  submitGraderoster,
} from "@/utils/data";
import { BButton, BCard, BLink, BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    Layout,
    SectionHeader,
    Student,
    GradeImport,
    Receipt,
    Errors,
    BButton,
    BCard,
    BLink,
    BPlaceholder,
  },
  setup() {
    const gradeStore = useGradeStore();
    return {
      gradeStore,
      getSection,
      getGraderoster,
      updateGraderoster,
      submitGraderoster,
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
          this.pageTitle = this.section.section_name;
          document.title = this.pageTitle + " - GradePage";
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
