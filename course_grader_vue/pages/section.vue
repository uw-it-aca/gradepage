<template>
  <Layout :page-title="pageTitle">
    <template #content>
      <div v-if="errorResponse">
        <Errors :error-response="errorResponse" />
      </div>
      <template v-if="isLoading">
        <div role="status">
          <span class="visually-hidden">Loading grade roster...</span>
        </div>
        <div aria-hidden="true">
          <h1 class="fs-1 fw-bold">
            <BPlaceholder
              animation="glow"
              cols="2"
              variant="secondary-subtle"
            />
          </h1>
          <h2 class="fs-2 m-0 me-3 mb-5">
            <BPlaceholder
              animation="glow"
              cols="3"
              variant="secondary-subtle"
            />
          </h2>
          <table class="table table-striped">
            <thead class="table-body-secondary">
              <tr>
                <th scope="col" style="width: 35%">Student</th>
                <th scope="col">Section</th>
                <th scope="col">Credits</th>
                <th scope="col" style="width: 45%">Grade</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="index in 5" :key="index">
                <td>
                  <div class="fs-4">
                    <BPlaceholder
                      animation="glow"
                      cols="9"
                      variant="secondary-subtle"
                    />
                  </div>
                  <div>
                    <BPlaceholder
                      animation="glow"
                      cols="5"
                      variant="secondary-subtle"
                    />
                  </div>
                </td>
                <td valign="middle">
                  <BPlaceholder
                    animation="glow"
                    cols="2"
                    variant="secondary-subtle"
                  />
                </td>
                <td valign="middle">
                  <BPlaceholder
                    animation="glow"
                    cols="4"
                    variant="secondary-subtle"
                  />
                </td>
                <td>&nbsp;</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
      <div v-else>
        <template v-if="appState.editingGrades">
          <EditGrades :section="section" />
        </template>
        <template v-else-if="appState.confirmingGrades">
          <ConfirmGrades :section="section" />
        </template>
        <template v-else-if="appState.reviewingGrades">
          <ReviewGrades :section="section" />
        </template>
        <template v-else-if="appState.convertingImport">
          <ConvertImport :section="section" />
        </template>
        <template v-else-if="appState.reviewingConversion">
          <ReviewConversion :section="section" />
        </template>
        <template v-else>
          {{ loadGraderoster() }}
        </template>
      </div>
    </template>
  </Layout>
</template>

<script>
import Layout from "@/layouts/default.vue";
import Errors from "@/components/errors.vue";
import EditGrades from "@/components/workflow/edit-grades.vue";
import ReviewGrades from "@/components/workflow/review-grades.vue";
import ConfirmGrades from "@/components/workflow/confirm-grades.vue";
import ConvertImport from "@/components/workflow/convert-import.vue";
import ReviewConversion from "@/components/workflow/review-conversion.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { useGradeStore } from "@/stores/grade";
import { getSection, getGraderoster } from "@/utils/data";
import { BPlaceholder } from "bootstrap-vue-next";

export default {
  name: "SectionPage",
  components: {
    Layout,
    EditGrades,
    ReviewGrades,
    ConfirmGrades,
    ConvertImport,
    ReviewConversion,
    Errors,
    BPlaceholder,
  },
  setup() {
    const appState = useWorkflowStateStore();
    const gradeStore = useGradeStore();
    return {
      appState,
      gradeStore,
      getSection,
      getGraderoster,
    };
  },
  data() {
    return {
      isLoading: true,
      section: null,
      pageTitle: "Course Section",
      errorResponse: null,
    };
  },
  created() {
    this.loadSection();
  },
  methods: {
    loadGraderoster: function () {
      if (this.section.graderoster_url && !this.errorResponse) {
        this.isLoading = true;

        this.gradeStore.$reset();
        this.appState.$reset();

        setTimeout(() => {
          this.getGraderoster(this.section.graderoster_url)
            .then((data) => {
              this.appState.setGraderoster(data.graderoster);
              this.errorResponse = null;
            })
            .catch((error) => {
              this.errorResponse = error.data;
            })
            .finally(() => {
              this.isLoading = false;
              console.log("done loading grade roster...");
            });
        }, 500);
      } else {
        this.isLoading = false;
      }
    },
    loadSection: function () {
      let section_id = this.$route.params.id;
      this.getSection("/api/v1/section/" + section_id)
        .then((data) => {
          this.section = data.section;
          document.title = this.section.section_name + " - GradePage";
          this.pageTitle = this.section.section_name;
          this.loadGraderoster();
        })
        .catch((error) => {
          this.errorResponse = error.data;
          this.isLoading = false;
        });
    },
  },
};
</script>
