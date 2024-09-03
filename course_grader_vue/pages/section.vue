<template>
  <Layout :page-title="pageTitle">
    <template #content>
      <BLink
        :href="section.term_url"
        :variant="'dark'"
        class="link-dark link-opacity-75 link-opacity-75-hover link-underline-opacity-50 link-underline-opacity-75-hover"
      >
        Back To {{ section.section_year }} {{ section.section_quarter }}
      </BLink>

      <!-- Grade receipt actions -->
      <!--<div v-if="studentsLoaded && !reviewing && !editing" class="text-end">-->
      <div class="text-end">
        <a
          :href="section.export_url"
          class="btn btn-sm btn-outline-secondary me-2 rounded-2"
          ><i class="bi bi-download"></i> Download Change of Grade template</a
        >
        <a
          href="javascript:window.print()"
          class="btn btn-sm btn-outline-secondary rounded-2"
        >
          <i class="bi bi-printer"></i> Print this page
        </a>
      </div>

      <!-- Graderoster header -->
      <BCard
        class="shadow-sm rounded-3 my-3"
        header-class="p-3"
        header="Default"
      >
        <template #header>
          <BLink
            href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
            target="_blank"
            title="Information on assigning and submitting grades"
            class="float-end"
            >Learn more...
          </BLink>
          <div class="fs-5 text-muted fw-light">
            <span v-if="studentsLoaded">{{ graderosterTitle }}</span>
            <span v-else-if="!errorResponse">Loading...</span>
          </div>
          <div v-if="section.section_name">
            <span class="fs-2 m-0 me-3">
              <BPlaceholder
                v-if="!section.section_name"
                class="bg-light-gray"
                width="15"
                animation="glow"
              />{{ section.section_name }}
            </span>
            <span class="small">
              {{ gettext("sln") }}
              <BPlaceholder
                v-if="!section.section_sln"
                class="bg-light-gray"
                width="5"
                animation="glow"
              />{{ section.section_sln }}</span
            >
          </div>
        </template>

        <!-- Row zero contains errors, information and import action -->
        <div v-if="errorResponse">
          <Errors :error-response="errorResponse" />
        </div>
        <div v-else-if="reviewing">
          {{ gettext("please_review_grades") }}
        </div>
        <div v-else-if="studentsLoaded && editing">
          <span
            v-if="graderoster.is_writing_section"
            v-html="gettext('writing_course_note')"
          />
          <div class="text-end">
            <GradeImport
              :section="section"
              :expected-grade-count="unsubmitted"
            />
          </div>
        </div>
        <div v-else>
          <Receipt :section="section" :graderoster="graderoster" />
        </div>

        <!-- Duplicate code legend -->
        <div
          v-if="graderoster && graderoster.has_duplicate_codes"
          class="mb-2 small text-muted"
        >
          {{ gettext("duplicate_code") }}
          <i class="bi bi-circle-fill text-secondary"></i>
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
          <div>{{ gettext("review_warning") }}</div>
          <div class="text-end">
            <BButton
              :title="`Go back and edit grades for {{ section.section_name }}`"
              variant="primary"
              @click="loadGraderoster"
              >{{ gettext("btn_review_back") }} </BButton
            >&nbsp;
            <BButton variant="primary" @click="submitGrades"
              >{{ gettext("btn_submit_grades") }}
            </BButton>
          </div>
        </template>
        <template #footer v-else-if="studentsLoaded && editing">
          <div class="text-end">
            <span v-if="gradesRemainingText">{{ gradesRemainingText }} </span>
            <span v-else class="visually-hidden">
              All grades entered. Click Review button to continue.
            </span>
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
    graderosterTitle() {
      return this.reviewing
        ? gettext("review_submit_grades")
        : this.editing
        ? gettext("enter_grades")
        : gettext("submitted_grades_for");
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
