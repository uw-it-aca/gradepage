<template>
  <div class="fs-5 text-muted fw-light">
    <span>{{ title }}</span>
  </div>
  <div v-if="section.section_name">
    <span class="fs-2 m-0 me-3">
      <BPlaceholder
        v-if="!section.section_name"
        class="bg-body-secondary"
        width="15"
        animation="glow"
      />{{ section.section_name }}
    </span>
    <span class="small">
      {{ gettext("sln") }}
      <BPlaceholder
        v-if="!section.section_sln"
        class="bg-body-secondary"
        width="5"
        animation="glow"
      />{{ section.section_sln }}</span
    >
  </div>
</template>

<script>
import { BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    BPlaceholder,
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
    title: {
     type: String,
     required: true,
    },
  },
};
</script>
