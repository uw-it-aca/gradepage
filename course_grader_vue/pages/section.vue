<template>
  <Layout :page-title="pageTitle">
    <template #content>

      <div v-if="errorResponse">
        <Errors :error-response="errorResponse" />
      </div>
      <div v-else-if="!isLoading">
        <template v-if="appState.editingGrades">
          <EditGrades :section="section" />
        </template>
        <template v-else-if="appState.confirmingGrades">
          <ConfirmGrades :section="section" :is-loading="isLoading" />
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
           TODO...
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
      section: {},
      pageTitle: "Course Section",
      errorResponse: null,
    };
  },
  methods: {
    loadGraderoster: function () {
      if (this.section.graderoster_url) {
        this.gradeStore.$reset();
        this.appState.$reset();
        this.getGraderoster(this.section.graderoster_url)
          .then((response) => {
            return response.data;
          })
          .then((data) => {
            this.appState.setGraderoster(data.graderoster);
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
    loadSection: function () {
      let section_id = this.$route.params.id;
      this.getSection("/api/v1/section/" + section_id)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.section = data.section;
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
