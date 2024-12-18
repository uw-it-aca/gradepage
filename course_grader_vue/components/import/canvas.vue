<!-- eslint-disable vue/no-v-html -->
<template>
  <div v-if="isLoading">Loading...</div>
  <div v-else-if="errorResponse">
    <i class="fas fa-exclamation-circle"></i>
    <strong>{{ errorResponse.data.error }}</strong>
  </div>
  <div v-else-if="appState.gradeImport">
    <div v-if="appState.gradeImport.status_code != 200">
      There was an error importing grades from Canvas ({{
        appState.gradeImport.status_code
      }}).
    </div>
    <div v-else-if="appState.gradeImport.grade_count">
      <p v-html="gradesFoundText"></p>

      <div
        v-if="appState.gradeImport.override_grade_count"
        role="alert"
        class="alert alert-warning"
      >
        <span class="fa-stack">
          <i class="fas fa-circle fa-stack-2x" aria-hidden="true"></i>
          <i
            class="fas fa-marker fa-flip-horizontal fa-stack-1x fa-inverse"
            aria-hidden="true"
          ></i>
        </span>

        <p>
          <span v-html="overrideGradesFoundText"></span>
          <BLink
            target="_blank"
            title="Learn more about importing grade overrides on IT Connect"
            href="https://itconnect.uw.edu/learn/tools/canvas/canvas-help-for-instructors/assignments-grading/new-gradebook/final-grade-override/"
            >Learn more </BLink
          >.
        </p>
      </div>

      <div
        v-if="appState.gradeImport.unposted_grade_count"
        role="alert"
        class="alert alert-danger"
      >
        <i class="fas fa-exclamation-circle fa-2x" aria-hidden="true"></i>
        <p v-html="unpostedGradesFoundText"></p>
        <span>
          Unposted grades <strong>ARE NOT</strong> represented in the imported
          final grade.
        </span>
        <BLink
          target="_blank"
          title="Learn more about Canvas grade posting on IT Connect"
          href="https://itconnect.uw.edu/learn/tools/canvas/canvas-help-for-instructors/assignments-grading/new-gradebook/posting-policy/"
          >Learn more </BLink
        >.
      </div>

      <ImportConvertSave :section="section" />
    </div>
    <div v-else>
      <span>
        No grades found for <strong>{{ section.section_name }}</strong> in
        Canvas.
      </span>
      Select a different option for import or enter grades manually.
    </div>
  </div>
</template>

<script>
import ImportConvertSave from "@/components/import/convert-options.vue";
import { BLink } from "bootstrap-vue-next";
import { useWorkflowStateStore } from "@/stores/state";
import { useGradeStore } from "@/stores/grade";
import { createImport } from "@/utils/data";
import { watch } from "vue";

export default {
  name: "ImportCanvas",
  components: {
    ImportConvertSave,
    BLink,
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
    expectedGradeCount: {
      type: Number,
      required: true,
    },
    modalOpen: {
      type: Boolean,
      required: true,
      default: false,
    },
  },
  setup() {
    const appState = useWorkflowStateStore();
    const gradeStore = useGradeStore();
    return {
      appState,
      gradeStore,
      createImport,
    };
  },
  data() {
    return {
      importSource: "canvas",
      errorResponse: null,
      isLoading: true,
    };
  },
  computed: {
    gradesFoundText() {
      return interpolate(
        ngettext(
          "One grade found for <strong>%(section_name)s</strong> in <strong>%(source_name)s</strong>.",
          "%(grade_count)s total grades found for <strong>%(section_name)s</strong> in <strong>%(source_name)s</strong>.",
          this.appState.gradeImport.grade_count
        ),
        {
          section_name: this.section.section_name,
          source_name: this.appState.gradeImport.source_name,
          grade_count: this.appState.gradeImport.grade_count,
        },
        true
      );
    },
    overrideGradesFoundText() {
      return interpolate(
        ngettext(
          "You have one final grade override in this Canvas Grade Import. This grade WILL BE included in the imported grades.",
          "You have <strong>%(override_grade_count)s final grade overrides</strong> in this Canvas Grade Import. These grades WILL BE included in the imported grades.",
          this.appState.gradeImport.override_grade_count
        ),
        {
          override_grade_count: this.appState.gradeImport.override_grade_count,
        },
        true
      );
    },
    unpostedGradesFoundText() {
      return interpolate(
        ngettext(
          "You have <strong>one student with unposted grades</strong> in this Canvas Grade Import.",
          "You have <strong>%(unposted_grade_count)s students with unposted grades</strong> in this Canvas Grade Import.",
          this.appState.gradeImport.unposted_grade_count
        ),
        {
          unposted_grade_count: this.appState.gradeImport.unposted_grade_count,
        },
        true
      );
    },
  },
  mounted() {
    watch(
      () => this.modalOpen,
      (newValue, oldValue) => {
        this.errorResponse = null;
        if (this.modalOpen) {
          this.loadImportedGrades();
        }
      }
    );
  },
  methods: {
    loadImportedGrades() {
      this.createImport(this.section.import_url, { source: this.importSource })
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.errorResponse = null;
          let gradeImport = this.gradeStore.processImport(data.grade_import);
          this.appState.setGradeImport(gradeImport);
        })
        .catch((error) => {
          this.appState.resetGradeImport();
          this.errorResponse = error.response;
        })
        .finally(() => {
          this.isLoading = false;
        });
    },
  },
};
</script>
