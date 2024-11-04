<template>
  <p v-html="importingGradesText"></p>

  <div v-if="appState.gradeImport">
    <div v-if="appState.gradeImport.grade_count">
      <p>
        <i class="fa fa-check-circle text-success" aria-hidden="true"></i>
        <span v-html="gradesFoundText"></span>
      </p>

      <ImportConvertSave :section="section" />

    </div>
    <div v-else>
      <span v-html="noGradesFoundText"></span>
      {{ gettext("select_alternate_import") }}
    </div>
  </div>
  <div v-else>
    <p>{{ expectedGradeCountText }}</p>
    <p>{{ gettext("csv_required_cols") }}</p>
    <ul>
      <li v-html="gettext('required_col_student')"></li>
      <li v-html="gettext('required_col_grade')"></li>
    </ul>

    <p>
      {{ gettext("csv_grade_types") }}
      <BLink
        href="https://itconnect.uw.edu/learn/tools/gradepage/import-convert-csv/#convert"
        :title="gettext('convert_percentages_help_title')"
        v-text="gettext('learn_more')"
        target="_blank">
      </BLink>
    </p>

    <p>
      <BLink
        href="https://itconnect.uw.edu/learn/tools/gradepage/import-convert-csv/"
        :title="gettext('format_csv_help_title')"
        v-text="gettext('format_csv_help')"
        target="_blank">
      </BLink>
    </p>
    <p v-html="gettext('begin_csv_import')"></p>

    <div class="mb-3">
      <label for="formFile" class="visually-hidden">
        {{ gettext("select_csv_file") }}
      </label>
      <input
        class="form-control"
        type="file"
        id="formFile"
        accept=".csv"
        @change="fileSelected($event.target.files)"
      />
    </div>

    <div v-if="errorResponse" class="alert alert-danger" role="alert">
      <div v-if="fileLimitExceeded">
        <i class="fas fa-exclamation-circle"></i>
        <strong>{{ gettext("file_size_exceeded") }}</strong><br/>
        <small>{{ gettext("file_name") }}: <em>{{ file.name }}</em></small>
        <ul>
          <li v-html="gettext('select_different_file')"</li>
        </ul>
      </div>
      <div v-else-if="missingHeaderGrade">
        <i class="fas fa-exclamation-circle"></i>
        <strong v-html="gettext('missing_header_grade')"></strong><br/>
        <small>{{ gettext("file_name") }}: <em>{{ file.name }}</em></small>
        <ul>
          <li v-html="gettext('missing_header_grade_help')"></li>
          <li v-html="gettext('select_different_file')"</li>
          <li>
            <BLink
              href="https://itconnect.uw.edu/learn/tools/gradepage/import-convert-csv/#format"
              :title="gettext('format_csv_help')"
              target="_blank"
            >{{ gettext("format_csv_help") }}</BLink>
          </li>
        </ul>
      </div>
      <div v-else-if="missingHeaderStudent">
        <i class="fas fa-exclamation-circle"></i>
        <strong v-html="gettext('missing_header_student')"></strong><br/>
        <small>{{ gettext("file_name") }}: <em>{{ file.name }}</em></small>
        <ul>
          <li v-html="gettext('missing_header_student_help')"></li>
          <li v-html="gettext('select_different_file')"</li>
        </ul>
      </div>
      <div v-else>
        <i class="fas fa-exclamation-circle"></i>
        <strong>{{ errorResponse.data.error }}</strong><br>
        <small>{{ gettext("file_name") }}: <em>{{ file.name }}</em></small>
        <ul>
          <li v-html="gettext('select_different_file')"</li>
        </ul>
      </div>
      <p>
        <BLink
          href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
          :title="gettext('import_other_options_title')"
          v-text="gettext('import_other_options')"
          target="_blank"
        ></BLink>
      </p>
    </div>
    <div v-else-if="appState.gradeImport && !appState.gradeImport.grade_count">
      <div class="alert alert-danger gp-upload-error" role="alert">
        <i class="fas fa-exclamation-circle"></i>
        <span v-html="import_no_grades_found"></span><br/>
        <small>{{ gettext("file_name") }}: <em>{{ file.name }}</em></small>
        <ul>
          <li v-text="gettext('confirm_grade_column')"></li>
          <li v-text="gettext('confirm_student_column')"></li>
          <li v-text="gettext('confirm_roster_students')"></li>
          <li v-html="gettext('select_different_file')"</li>
        </ul>
        <p>
          <BLink
            href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
            :title="gettext('import_other_options_title')"
            v-text="gettext('import_other_options')"
            target="_blank"
          ></BLink>
        </p>
      </div>
    </div>

    <div>
      <BButton
        :disabled="uploadDisabled"
        variant="primary"
        @click="uploadFile"
        v-text="gettext('verify_file_btn')"
      >
      </BButton>
    </div>
  </div>
</template>

<script>
import { useGradeStore } from "@/stores/grade";
import { uploadGrades } from "@/utils/data";
import ImportConvertSave from "@/components/import/convert-options.vue";
import { BButton, BLink } from "bootstrap-vue-next";
import { useWorkflowStateStore } from "@/stores/state";

export default {
  components: {
    ImportConvertSave,
    BButton,
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
  },
  setup() {
    const appState = useWorkflowStateStore();
    const gradeStore = useGradeStore();
    return {
      appState,
      gradeStore,
      uploadGrades,
    };
  },
  data() {
    return {
      file: null,
      errorResponse: null,
    };
  },
  computed: {
    uploadDisabled() {
      return this.file === null;
    },
    missingHeaderGrade() {
      return (
        this.errorResponse &&
        typeof(this.errorResponse.data) === "object" &&
        this.errorResponse.data.error === "Missing header: grade");
    },
    missingHeaderStudent() {
      return (
        this.errorResponse &&
        typeof(this.errorResponse.data) === "object" &&
        this.errorResponse.data.error === "Missing header: student");
    },
    fileLimitExceeded() {
      return (
        this.errorResponse &&
        typeof(this.errorResponse.data) === "string"  &&
        this.errorResponse.data.indexOf("Request Entity Too Large") !== -1);
    },
    expectedGradeCountText() {
      return interpolate(ngettext(
        "One grade expected",
        "%(count)s grades expected",
        this.expectedGradeCount), {"count": this.expectedGradeCount}, true);
    },
    importingGradesText() {
      return interpolate(gettext("importing_grades_for_section"),
        {section_name: this.section.section_name}, true);
    },
    gradesFoundText() {
      return interpolate(ngettext(
        "<strong>%(grade_count)s</strong> of <strong>%(expected_count)s</strong> grade found in the file <strong>%(file_name)s</strong>",
        "<strong>%(grade_count)s</strong> of <strong>%(expected_count)s</strong> grades found in the file <strong>%(file_name)s</strong>",
        this.appState.gradeImport.grade_count), {
          grade_count: this.appState.gradeImport.grade_count,
          expected_count: this.expectedGradeCount,
          file_name: this.file.name,
        }, true
      );
    },
    noGradesFoundText() {
      return interpolate(gettext("no_grades_found_csv"),
        {section_name: this.section.section_name}, true);
    },
  },
  methods: {
    fileSelected(files) {
      this.errorResponse = null;
      this.file = files[0];
    },
    uploadFile() {
      this.uploadGrades(this.section.upload_url, this.file)
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
        });
    },
  },
};
</script>
