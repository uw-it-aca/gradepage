<template>
  <BDropdown
    v-model="showImportOptions"
    size="sm"
    variant="outline-primary"
    no-caret
  >
    <template #button-content>
      <i class="bi bi-arrow-return-right me-1"></i>Import from...</template
    >
    <BDropdownItemButton v-b-modal.modalImportCanvasGrades
      >Canvas Gradebook</BDropdownItemButton
    >
    <BDropdownItemButton v-b-modal.modalImportCsvGrades
      >CSV File</BDropdownItemButton
    >
  </BDropdown>

  <BModal
    id="modalImportCanvasGrades"
    title="Import Canvas Gradebook"
    no-close-on-backdrop
  >
    <p>8 total grades found in ESS 101 AA in Canvas Gradebook</p>
    <p>
      The Office of the Registrar requires submitted grades to follow official
      formatting.
    </p>
    <p>Please select a format to use:</p>

    <div class="d-grid gap-2">
      <BButton variant="outline-secondary"
        >Undergraduate Scale (4.0-0.7)</BButton
      >
      <BButton variant="outline-secondary">Graduate Scale (4.0-1.7)</BButton>
      <BButton variant="outline-secondary">Credit/No Credit Scale</BButton>
      <BButton variant="outline-secondary"
        >School of Medicine Pass/No Pass</BButton
      >
      <BButton variant="outline-secondary"
        >Honors/High Pass/Pass/Fail Scale</BButton
      >
    </div>
    <template #footer>CANCEL</template>
  </BModal>

  <BModal
    id="modalImportCsvGrades"
    title="Import CSV File"
    no-close-on-backdrop
  >
    <p>
      You are importing final grades for section
      <strong>{{ section.section_name }}</strong>
    </p>
    <p>
      {{ ngettext("One grade expected", "%(expectedGradeCount)s grades expected",
                  expectedGradeCount) }}
    </p>
    <p>The CSV is required to contain at least two columns:</p>
    <ul>
      <li>a column for student identifier (<strong>SIS User ID</strong> or <strong>StudentNo)</strong> AND</li>
      <li>a column for grades to be submitted (<strong>ImportGrade</strong>)</li>
    </ul>

    <p>
      An imported CSV file can contain letter grades, grade codes, or
      percentages. You will be prompted to
      <a
        href="https://itconnect.uw.edu/learn/tools/gradepage/import-convert-csv/#convert"
        title="Learn about converting percentages on IT Connect"
        target="_blank">
        convert percentages
      </a>
      during the import process.
    </p>

    <p>
      <a
        href="https://itconnect.uw.edu/learn/tools/gradepage/import-convert-csv/"
        title="Learn about importing a CSV on IT Connect"
        target="_blank">
        Learn more about formatting and importing a CSV file.
      </a>
    </p>
    <p>To begin import, choose the CSV file, and then click
       <strong>Verify CSV</strong>.
    </p>

    <div class="mb-3">
      <label for="formFile" class="visually-hidden">
        Select a CSV file to Import
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

    </div>

    <template #footer>
      <BButton
        :disabled="uploadDisabled"
        variant="primary"
        @click="processFileUpload"
      >
        Verify CSV
      </BButton>
    </template>
  </BModal>
</template>

<script>
import { ref } from "vue";
import { uploadGrades } from "@/utils/data";
import {
  BButton,
  BDropdown,
  BDropdownItemButton,
  BModal,
} from "bootstrap-vue-next";

export default {
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
  components: {
    BButton,
    BDropdown,
    BDropdownItemButton,
    BModal,
  },
  setup() {
    const showImportOptions = ref(false);
    return {
      showImportOptions,
      uploadGrades,
    };
  },
  data() {
    return {
      file: null,
      errorResponse: null,
      gradeImport: null,
    };
  },
  computed: {
    uploadDisabled() {
      return this.file === null;
    },
  },
  methods: {
    fileSelected(files) {
      this.file = files[0];
    },
    processFileUpload() {
      this.uploadGrades(this.section.upload_url, this.file)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.gradeImport = data.grade_import;
        })
        .catch((error) => {
          this.errorResponse = error.response;
        });
    },
    processCanvasImport() {
      this.createImport(this.section.import_url, {"source": "canvas"})
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.gradeImport = data.grade_import;
        })
        .catch((error) => {
          this.errorResponse = error.response;
        });
    },
  },
};
</script>
