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
    <p>You are importing final grades for section ESS 101 AB</p>

    <p>The CSV is required to contain at least two columns:</p>
    <ul>
      <li>a column for student identifier (SIS User ID or StudentNo) AND</li>
      <li>a column for grades to be submitted (ImportGrade)</li>
    </ul>

    <p>
      An imported CSV file can contain letter grades, grade codes, or
      percentages. You will be prompted to convert percentages during the import
      process.
    </p>
    <p>Learn more about formatting and importing a CSV file.</p>
    <p>To begin import, choose the CSV file, and then click Verify CSV.</p>

    <div class="mb-3">
      <input class="form-control" type="file" id="formFile" accept=".csv" />
    </div>

    <template #footer>
      <BButton variant="primary">Verify CSV</BButton>
    </template>
  </BModal>
</template>

<script>
import { ref } from "vue";
import {
  BButton,
  BDropdown,
  BDropdownItemButton,
  BModal,
} from "bootstrap-vue-next";

export default {
  props: {},
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
    };
  },
  data() {
    return {};
  },
};
</script>
