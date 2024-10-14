<template>
  <div v-if="gradeImport">
    <div v-if="gradeImport.grade_count">
      <p v-if="gradeImport.grade_count === 1">
        One grade found for <strong>{{ section.section_name }}</strong> in
        <strong>{{ gradeImport.source_name }}</strong>.
      </p>
      <p v-else>
        {{ gradeImport.grade_count }} total grades found for
        <strong>{{ section.section_name }}</strong> in
        <strong>{{ gradeImport.source_name }}</strong>.
      </p>

      <div v-if="gradeImport.override_grade_count" role="alert" class="alert alert-warning">
        <span class="fa-stack">
          <i class="fas fa-circle fa-stack-2x" aria-hidden="true"></i>
          <i class="fas fa-marker fa-flip-horizontal fa-stack-1x fa-inverse" aria-hidden="true"></i>
        </span>
        <p v-if="gradeImport.override_grade_count === 1">
          You have one final grade override in this Canvas Grade Import.
          This grade WILL BE included in the imported grades.
        </p>
        <p v-else>
          You have <strong>{{ gradeImport.override_grade_count }} final grade overrides</strong>
          in this Canvas Grade Import.
          These grades WILL BE included in the imported grades.
          <BLink
            target="_blank"
            href="https://itconnect.uw.edu/learn/tools/canvas/canvas-help-for-instructors/assignments-grading/new-gradebook/final-grade-override/">
            {{ gettext("learn_more") }}
          </BLink>.
        </p>
      </div>

      <div v-if="gradeImport.unposted_grade_count" role="alert" class="alert alert-danger">
        <span class="gp-unposted-grade-icon">
          <i class="fas fa-exclamation-circle fa-2x" aria-hidden="true"></i>
        </span>
        <p v-if="gradeImport.unposted_grade_count === 1">
          You have <strong>one student with unposted grades</strong>
          in this Canvas Grade Import.
        </p>
        <p v-else>
          You have <strong>{{ gradeImport.unposted_grade_count }} students
          with unposted grades</strong> in this Canvas Grade Import.
        </p>
        Unposted grades <strong>ARE NOT</strong> represented in the imported final grade.
        <BLink
          target="_blank"
          href="https://itconnect.uw.edu/learn/tools/canvas/canvas-help-for-instructors/assignments-grading/correctly-import-grades/">
          {{ gettext("learn_more") }}
        </BLink>.
      </div>

      <ImportConvertSave :section="section" :grade-import="gradeImport" />

    </div>
    <div v-else-if="gradeImport.status_code != 200">
      There was an error importing grades from Canvas ({{ gradeImport.status_code }}).
    </div>
  </div>
  <div v-else-if="errorResponse">
    <i class="fas fa-exclamation-circle"></i>
    <strong>{{ errorResponse.data.error }}</strong>
  </div>
</template>

<script>
import { useGradeStore } from "@/stores/grade";
import { createImport } from "@/utils/data";
import ImportConvertSave from "@/components/import/convert-options.vue";
import { BLink } from "bootstrap-vue-next";
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
    const gradeStore = useGradeStore();
    return {
      gradeStore,
      createImport,
    };
  },
  data() {
    return {
      importSource: "canvas",
      gradeImport: null,
      errorResponse: null,
    };
  },
  methods: {
    loadImportedGrades() {
      this.createImport(this.section.import_url, {"source": this.importSource})
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.errorResponse = null;
          this.gradeImport = this.gradeStore.processImport(data.grade_import);
        })
        .catch((error) => {
          this.errorResponse = error.response;
          this.gradeImport = null;
        });
    },
  },
  mounted() {
    watch(() => this.modalOpen, (newValue, oldValue) => {
      if (this.modalOpen) {
        this.loadImportedGrades();
      }
    });
  },
};
</script>
