<template>
  <BDropdown
    v-model="showImportOptions"
    size="sm"
    variant="outline-secondary"
    no-caret
    class="float-end d-inline-block"
    toggle-class="rounded-2"
  >
    <template #button-content>
      <i class="bi bi-arrow-return-right me-2 text-body-tertiary"></i>Import from...</template
    >
    <BDropdownItemButton v-b-modal.modalImportCanvasGrades @click="showModal"
      ><i class="bi bi-journal-check me-2 text-body-tertiary"></i>Canvas
      Gradebook</BDropdownItemButton
    >
    <BDropdownItemButton v-b-modal.modalImportCsvGrades
      ><i class="bi bi-filetype-csv me-2 text-body-tertiary"></i>CSV File</BDropdownItemButton
    >
    <BDropdownDivider />
    <BDropdownItem
      href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
      target="_blank"
      title="Information on assigning and submitting grades"
      ><i class="bi bi-question-circle me-2 text-body-tertiary"></i>GradePage Help
    </BDropdownItem>
  </BDropdown>

  <BModal
    id="modalImportCanvasGrades"
    title="Import Canvas Gradebook"
    no-close-on-backdrop
    hide-footer
  >
    <CanvasGrades
      :section="section"
      :expected-grade-count="expectedGradeCount"
      :modal-open="modalOpen"
      import-source="canvas"
    />
  </BModal>

  <BModal
    id="modalImportCsvGrades"
    title="Import CSV File"
    no-close-on-backdrop
    hide-footer
  >
    <UploadGrades
      :section="section"
      :expected-grade-count="expectedGradeCount"
      import-source="csv"
    />
  </BModal>
</template>

<script>
import CanvasGrades from "@/components/import/canvas.vue";
import UploadGrades from "@/components/import/upload.vue";
import {
  BDropdown,
  BDropdownDivider,
  BDropdownItem,
  BDropdownItemButton,
  BModal,
} from "bootstrap-vue-next";
import { ref } from "vue";

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
    CanvasGrades,
    UploadGrades,
    BDropdown,
    BDropdownDivider,
    BDropdownItem,
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
    return {
      modalOpen: false,
    };
  },
  methods: {
    showModal() {
      this.modalOpen = true;
    },
  },
};
</script>
