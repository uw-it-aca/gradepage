<template>
  <Layout :page-title="pageTitle">
    <template #content>

      <BLink :href="section.term_url" :variant="'dark'" class="link-dark link-opacity-75 link-opacity-75-hover link-underline-opacity-50 link-underline-opacity-75-hover">
        Back To {{ section.section_year }} {{ section.section_quarter }}
      </BLink>

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
        <div v-else-if="studentsLoaded && editing">
          <span
            v-if="graderoster.is_writing_section"
            v-html="gettext('writing_course_note')"
          />
          <div>
            <GradeImport />
          </div>
        </div>
        <div v-else>
          <ConfirmationHeader :section="section" :graderoster="graderoster" />
        </div>

        <div>
          <template
            v-if="graderoster.has_duplicate_codes"
            class="mb-2 small text-muted"
          >
            {{ gettext("duplicate_code") }}
            <i class="bi bi-circle-fill text-secondary"></i>
          </template>
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
            <div>{{ gettext("review_warning") }}</div>
            <button
              @click="loadGraderoster">{{ gettext("btn_review_back") }}</button>
            <button
              @click="submitGrades">{{ gettext("btn_submit_grades") }}</button>
          </div>
          <div v-else-if="studentsLoaded && editing">
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
  </Layout>
</template>

<script>
import Layout from "@/layouts/default.vue";
import Student from "@/components/graderoster/student.vue";
import GradeImport from "@/components/gradeimport/import.vue";
import ConfirmationHeader from "@/components/graderoster/header/confirmation.vue";
import { useGradeStore } from "@/stores/grade";
import { getSection, getGraderoster, updateGraderoster, submitGraderoster } from "@/utils/data";
import { BButton, BCard, BLink, BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    Layout,
    Student,
    GradeImport,
    ConfirmationHeader,
    BButton,
    BCard,
    BLink,
    BPlaceholder
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
    };
  },
  computed: {
    editing() {
      return this.graderoster.students.filter(
        s => s.grade_url !== null).length > 0;
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
            console.log(error.message);
          })
          .finally(() => {
            this.isLoading = false;
          });
      } else {
        this.isLoading = false;
      }
    },
    reviewGrades: function () {
      this.updateGraderoster(this.section.graderoster_url,
                             this.gradeStore.grades)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.reviewing = true;
          this.graderoster = data.graderoster;
        })
        .catch((error) => {
          console.log(error.message);
          this.gradeError = error.message;
        });
    },
    submitGrades: function () {
      if (this.reviewing) {
        this.submitGraderoster(this.section.graderoster_url, {})
          .then((response) => {
            return response.data;
          })
          .then((data) => {
            this.reviewing = true;
            this.graderoster = data.graderoster;
          })
          .catch((error) => {
            console.log(error.message);
            this.gradeError = error.message;
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
          this.loadGraderoster();
        })
        .catch((error) => {
          console.log(error.message);
          this.isLoading = false;
        })
        .finally(() => {
          this.pageTitle = this.section.section_name;
          document.title = this.pageTitle + " - GradePage";
        });
    },
  },
  created() {
    this.loadSection();
  },
};
</script>
