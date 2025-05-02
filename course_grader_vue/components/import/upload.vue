<!-- eslint-disable vue/no-v-html -->
<template>
  <p>
    You are importing final grades for section
    <strong>{{ section.section_name }}</strong>
  </p>

  <div v-if="appState.gradeImport">
    <div v-if="appState.gradeImport.grade_count">
      <p>
        <i class="fa fa-check-circle text-success" aria-hidden="true"></i>
        <span v-html="uploadGradesFoundText"></span>
      </p>

      <ImportConvertSave :section="section" />
    </div>
    <div v-else>
      <span>
        No grades found for <strong>{{ section.section_name }}</strong> in this
        CSV file.
      </span>
      Select a different file for import or enter grades manually.
    </div>
  </div>
  <div v-else>
    <p>
      {{
        interpolate(
          ngettext(
            "One grade expected",
            "%(count)s grades expected",
            expectedGradeCount
          ),
          { count: expectedGradeCount },
          true
        )
      }}
    </p>
    <p>The CSV is required to contain at least two columns:</p>
    <ul>
      <li>
        a column for student identifier (<strong>SIS User ID</strong> or
        <strong>StudentNo)</strong> AND
      </li>
      <li>a column for grades to be submitted (<strong>ImportGrade</strong></li>
    </ul>

    <p>
      An imported CSV file can contain final grades or percentages. You will be
      prompted to convert percentages during the import process.
      <BLink
        href="https://itconnect.uw.edu/learn/tools/gradepage/import-convert-csv/#convert"
        title="Learn about converting percentages on IT Connect"
        target="_blank"
        >Learn more
      </BLink>
    </p>

    <p>
      <BLink
        href="https://itconnect.uw.edu/learn/tools/gradepage/import-convert-csv/"
        title="Learn about importing a CSV file on IT Connect"
        target="_blank"
      >
        Learn more about formatting and importing a CSV file for GradePage.
      </BLink>
    </p>
    <p>
      To begin import, choose the CSV file, and then click
      <strong>Verify CSV</strong>.
    </p>

    <div class="mb-3">
      <label for="formFile" class="visually-hidden">
        Select a CSV file to import.
      </label>
      <input
        id="formFile"
        class="form-control"
        type="file"
        accept=".csv"
        @change="fileSelected($event.target.files)"
      />
    </div>

    <div v-if="errorResponse" class="alert alert-danger" role="alert">
      <div v-if="fileLimitExceeded">
        <i class="fas fa-exclamation-circle"></i>
        <strong>Allowable file size exceeded (2 Mb).</strong><br />
        <small
          >File: <em>{{ file.name }}</em></small
        >
        <ul>
          <li>Select a different file for import.</li>
        </ul>
      </div>
      <div v-else-if="missingHeaderGrade">
        <i class="fas fa-exclamation-circle"></i>
        <strong>Missing column heading: &quot;ImportGrade&quot;</strong>
        <br />
        <small
          >File: <em>{{ file.name }}</em></small
        >
        <ul>
          <li>
            Confirm that the .csv file contains a column with the heading
            &quot;ImportGrade&quot; and that the column contains the grades you
            want to submit.
          </li>
          <li>Select a different file for import.</li>
          <li>
            <BLink
              href="https://itconnect.uw.edu/learn/tools/gradepage/import-convert-csv/#format"
              title="Learn about importing a CSV file on IT Connect"
              target="_blank"
              >Learn more about formatting and importing a CSV file for
              GradePage.</BLink
            >
          </li>
        </ul>
      </div>
      <div v-else-if="missingHeaderStudent">
        <i class="fas fa-exclamation-circle"></i>
        <strong
          >Missing column heading: &quot;SIS User ID&quot; OR
          &quot;StudentNo&quot;</strong
        >
        <br />
        <small
          >File: <em>{{ file.name }}</em></small
        >
        <ul>
          <li>
            Confirm that the .csv file contains a column with the heading
            &quot;SIS User ID&quot; or &quot;StudentNo&quot;.
          </li>
          <li>Select a different file for import.</li>
        </ul>
      </div>
      <div v-else>
        <i class="fas fa-exclamation-circle"></i>
        <strong>{{ errorResponse.error }}</strong
        ><br />
        <small
          >File: <em>{{ file.name }}</em></small
        >
        <ul>
          <li>Select a different file for import.</li>
        </ul>
      </div>
      <p>
        <BLink
          href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
          title="Learn about other options to submit grades on IT Connect"
          target="_blank"
          >See other options for submitting grades.</BLink
        >
      </p>
    </div>
    <div v-else-if="appState.gradeImport && !appState.gradeImport.grade_count">
      <div class="alert alert-danger gp-upload-error" role="alert">
        <i class="fas fa-exclamation-circle"></i>
        <span>
          No grades found for <strong>{{ section.section_name }}</strong> in
          this CSV file. </span
        ><br />
        <small
          >File: <em>{{ file.name }}</em></small
        >
        <ul>
          <li>Confirm that the ImportGrade column contains grade values.</li>
          <li>
            Confirm that the SIS User ID or StudentNo column contains student
            identifiers.
          </li>
          <li>
            Confirm that the .csv file contains students from this section.
          </li>
          <li>Select a different file for import.</li>
        </ul>
        <p>
          <BLink
            href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
            title="Learn about other options to submit grades on IT Connect"
            target="_blank"
          ></BLink
          >See other options for submitting grades.
        </p>
      </div>
    </div>

    <div>
      <BButton :disabled="uploadDisabled" variant="primary" @click="uploadFile"
        >Verify CSV
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
  name: "ImportUpload",
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
        typeof this.errorResponse === "object" &&
        this.errorResponse.error === "Missing header: grade"
      );
    },
    missingHeaderStudent() {
      return (
        this.errorResponse &&
        typeof this.errorResponse === "object" &&
        this.errorResponse.error === "Missing header: student"
      );
    },
    fileLimitExceeded() {
      return (
        this.errorResponse &&
        typeof this.errorResponse.data === "string" &&
        this.errorResponse.data.indexOf("Request Entity Too Large") !== -1
      );
    },
    uploadGradesFoundText() {
      return interpolate(
        ngettext(
          "<strong>%(grade_count)s</strong> of <strong>%(expected_count)s</strong> grade found in the file <strong>%(file_name)s</strong>",
          "<strong>%(grade_count)s</strong> of <strong>%(expected_count)s</strong> grades found in the file <strong>%(file_name)s</strong>",
          this.appState.gradeImport.grade_count
        ),
        {
          grade_count: this.appState.gradeImport.grade_count,
          expected_count: this.expectedGradeCount,
          file_name: this.file.name,
        },
        true
      );
    },
  },
  methods: {
    fileSelected(files) {
      this.errorResponse = null;
      this.file = files[0];
    },
    uploadFile() {
      this.uploadGrades(this.section.upload_url, this.file)
        .then((data) => {
          this.errorResponse = null;
          let gradeImport = this.gradeStore.processImport(data.grade_import);
          this.appState.setGradeImport(gradeImport);
        })
        .catch((error) => {
          this.appState.resetGradeImport();
          this.errorResponse = error;
        });
    },
  },
};
</script>
