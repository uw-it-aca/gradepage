<template>
  <div v-if="errorResponse">
    TODO: {{ errorResponse }}
  </div>
  <div v-else-if="gradeImport.has_valid_percentages" class="d-grid gap-2">
    <p>{{ gettext("import_conversion_required") }}</p>
    <p>{{ gettext("import_conversion_required_select") }}</p>
    <BButton
      variant="outline-secondary"
      @click="">
      {{ gettext("conversion_scale_ug") }}</BButton>
    <BButton
      variant="outline-secondary"
      @click="">
      {{ gettext("conversion_scale_gr") }}</BButton>
    <BButton
      variant="outline-secondary"
      @click="">
      {{ gettext("conversion_scale_cnc") }}</BButton>
    <BButton
      variant="outline-secondary"
      @click="">
      {{ gettext("conversion_scale_pf") }}</BButton>
    <BButton
      variant="outline-secondary"
      @click="">
      {{ gettext("conversion_scale_hpf") }}</BButton>
  </div>
  <div v-else>
    <p>
      To continue, click <strong>{{ gettext("import_save_grades") }}</strong>.
      <br /><small><em>You will have a chance to enter, adjust, and review grades on the next screen.</em></small>
    </p>
    <p>To select a different file, click <strong>Cancel</strong>.</p>
    <div>
      <BButton variant="primary" @click="saveGrades">
        {{ gettext("import_save_grades") }}
      </BButton>
    </div>
  </div>
</template>

<script>
import { saveImportedGrades } from "@/utils/data";
import { BButton } from "bootstrap-vue-next";

export default {
  components: {
    BButton,
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
    gradeImport: {
      type: Object,
      required: true,
    },
  },
  setup() {
    return {
      saveImportedGrades,
    };
  },
  data() {
    return {
      errorResponse: null,
    };
  },
  methods: {
    saveGrades() {
      let url = this.section.import_url + "/" + this.gradeImport.id;
      this.saveImportedGrades(url, {})
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.errorResponse = null;
        })
        .catch((error) => {
          this.errorResponse = error.response;
        });
    },
  },
};
</script>
