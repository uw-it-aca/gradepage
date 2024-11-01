<template>
  <div v-if="isLoading">
    Loading...
  </div>
  <div v-else-if="errorResponse">
    <i class="fas fa-exclamation-circle"></i>
    <strong>{{ errorResponse.data.error }}</strong>
  </div>
  <div v-else-if="appState.gradeImport">
    <div v-if="appState.gradeImport.status_code != 200">
      {{ gettext("import_canvas_error") }}
      ({{ appState.gradeImport.status_code }}).
    </div>
    <div v-else-if="appState.gradeImport.grade_count">
      <p v-html="gradesFoundText"></p>

      <div v-if="appState.gradeImport.override_grade_count" role="alert" class="alert alert-warning">
        <span class="fa-stack">
          <i class="fas fa-circle fa-stack-2x" aria-hidden="true"></i>
          <i class="fas fa-marker fa-flip-horizontal fa-stack-1x fa-inverse" aria-hidden="true"></i>
        </span>

        <p>
          <span v-html="overrideGradesFoundText"></span>
          <BLink
            target="_blank"
            :title="gettext('import_override_grades_title')"
            v-text="gettext('learn_more')"
            href="https://itconnect.uw.edu/learn/tools/canvas/canvas-help-for-instructors/assignments-grading/new-gradebook/final-grade-override/">
          </BLink>.
        </p>
      </div>

      <div v-if="appState.gradeImport.unposted_grade_count" role="alert" class="alert alert-danger">
        <i class="fas fa-exclamation-circle fa-2x" aria-hidden="true"></i>
        <p v-html="unpostedGradesFoundText"></p>
        <span v-html="gettext('import_unposted_grade_warning')"></span>
        <BLink
          target="_blank"
          :title="gettext('import_unposted_grade_title')"
          v-text="gettext('learn_more')"
          href="https://itconnect.uw.edu/learn/tools/canvas/canvas-help-for-instructors/assignments-grading/correctly-import-grades/">
        </BLink>.
      </div>

      <ImportConvertSave :section="section" />

    </div>
    <div v-else>
      <span v-html="noGradesFoundText"></span>
      {{ gettext("select_alternate_import") }}
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
      return interpolate(ngettext(
        "import_grade_found",
        "import_grades_found",
        this.appState.gradeImport.grade_count), {
          section_name: this.section.section_name,
          source_name: this.appState.gradeImport.source_name,
          grade_count: this.appState.gradeImport.grade_count,
        }, true
      );
    },
    noGradesFoundText() {
      return interpolate(gettext("no_grades_found_canvas"),
        {section_name: this.section.section_name}, true);
    },
    overrideGradesFoundText() {
      return interpolate(ngettext(
        "import_override_grade_found",
        "import_override_grades_found",
        this.appState.gradeImport.override_grade_count), {
          override_grade_count: this.appState.gradeImport.override_grade_count
        }, true
      );
    },
    unpostedGradesFoundText() {
      return interpolate(ngettext(
        "import_unposted_grade_found",
        "import_unposted_grades_found",
        this.appState.gradeImport.unposted_grade_count), {
          unposted_grade_count: this.appState.gradeImport.unposted_grade_count
        }, true
      );
    },
  },
  methods: {
    loadImportedGrades() {
      this.createImport(this.section.import_url, {"source": this.importSource})
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
  mounted() {
    watch(() => this.modalOpen, (newValue, oldValue) => {
      this.errorResponse = null;
      if (this.modalOpen) {
        this.loadImportedGrades();
      }
    });
  },
};
</script>
