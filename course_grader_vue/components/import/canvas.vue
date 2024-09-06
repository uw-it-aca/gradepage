<template>
  <p>
    8 total grades found in {{ section.section_name }} in Canvas Gradebook
  </p>
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
</template>

<script>
import { createImport } from "@/utils/data";
import { BButton } from "bootstrap-vue-next";

export default {
  components: {
    BButton
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
    return {
      createImport,
    };
  },
  data() {
    return {
      gradeImport: null,
      errorResponse: null,
    };
  },
  methods: {
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
