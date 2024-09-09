<template>
  <BDropdown
    v-model="showImportOptions"
    size="sm"
    variant="outline-primary"
    no-caret
    toggle-class="rounded-2"
  >
    <template #button-content>
      <i class="bi bi-arrow-return-right me-1"></i>Import from...</template
    >
    <BDropdownItemButton v-b-modal.modalImportCanvasGrades
      @click="showModal"
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
    hide-footer
  >
    <CanvasGrades
      :section="section"
      :expected-grade-count="expectedGradeCount"
      :modal-open="modalOpen"
      import-source="canvas"/>
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
      import-source="csv" />
  </BModal>
</template>

<script>
import CanvasGrades from "@/components/import/canvas.vue";
import UploadGrades from "@/components/import/upload.vue";
import { BDropdown, BDropdownItemButton, BModal } from "bootstrap-vue-next";
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
