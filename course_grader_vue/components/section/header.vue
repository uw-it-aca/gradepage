<template>
  <div class="">
    <h1 class="fs-1 fw-bold">{{ title }}</h1>
    <div class="d-flex align-items-end">
      <h2 v-if="section.section_name" class="fs-2 m-0 me-3">
        <BPlaceholder
          v-if="!section.section_name"
          class="bg-body-secondary"
          width="15"
          animation="glow"
        />{{ section.section_name }}
      </h2>
      <span class="fs-5 text-secondary"
        >SLN
        <BPlaceholder
          v-if="!section.section_sln"
          width="5"
          animation="glow"
        />{{ section.section_sln }}</span
      >
    </div>
  </div>
</template>

<script>
import { BPlaceholder } from "bootstrap-vue-next";

export default {
  name: "SectionHeader",
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
