<template>
  <BDropdown
    v-model="showImportOptions"
    size="sm"
    variant="subdued-primary"
    no-caret
    class="float-end d-inline-block"
    toggle-class="rounded-2"
  >
    <template #button-content>
      <i class="bi bi-arrow-return-right me-2"></i>
      Import from...
    </template>
    <BDropdownItemButton v-b-modal.modalImportCanvasGrades
      ><i class="bi bi-journal-check me-2"></i>
      Canvas Gradebook
    </BDropdownItemButton>
    <BDropdownItemButton v-b-modal.modalImportCsvGrades
      ><i class="bi bi-filetype-csv me-2"></i>
      CSV File
    </BDropdownItemButton>
    <BDropdownDivider />
    <BDropdownItem
      href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
      target="_blank"
      title="Information on assigning and submitting grades"
    >
      <i class="bi bi-question-circle me-2 text-body-tertiary"></i>
      GradePage Help
    </BDropdownItem>
  </BDropdown>

  <BModal
    id="modalImportCanvasGrades"
    title="Import Canvas Gradebook"
    ok-only
    ok-variant="secondary"
    ok-title="Cancel"
    no-close-on-backdrop
    @show="showCanvasModal"
    @hidden="hideCanvasModal"
  >
    <CanvasGrades
      :section="section"
      :expected-grade-count="expectedGradeCount"
      :modal-open="modalOpen"
    />
  </BModal>

  <BModal
    id="modalImportCsvGrades"
    title="Import CSV File"
    ok-only
    ok-variant="secondary"
    ok-title="Cancel"
    no-close-on-backdrop
    @show="showUploadModal"
  >
    <UploadGrades
      :section="section"
      :expected-grade-count="expectedGradeCount"
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
import { useWorkflowStateStore } from "@/stores/state";
import { ref } from "vue";

export default {
  components: {
    CanvasGrades,
    UploadGrades,
    BDropdown,
    BDropdownDivider,
    BDropdownItem,
    BDropdownItemButton,
    BModal,
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
    const showImportOptions = ref(false);
    const appState = useWorkflowStateStore();
    return {
      showImportOptions,
      appState,
    };
  },
  data() {
    return {
      modalOpen: false,
    };
  },
  methods: {
    showCanvasModal() {
      this.appState.resetGradeImport();
      this.modalOpen = true;
    },
    hideCanvasModal() {
      this.modalOpen = false;
    },
    showUploadModal() {
      this.appState.resetGradeImport();
    },
  },
};
</script>
