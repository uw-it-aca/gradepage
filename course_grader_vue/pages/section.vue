<template>
  <Layout :page-title="pageTitle">
    <template #content>
      <div v-if="errorResponse">
        <Errors :error-response="errorResponse" />
      </div>
      <div v-if="isLoading">Loading grade roster state...</div>
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
      if (this.section.graderoster_url) {
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
        }, 2000);
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
