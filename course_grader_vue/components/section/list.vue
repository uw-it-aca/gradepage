<template>
  <div>
    <ul>
      <li v-for="section in sections" :key="section.section_id">
        <primary-section :section="section"></primary-section>
      </li>
    </ul>
  </div>
</template>

<script>
import PrimarySection from "@/components/section/primary.vue";

export default {
  components: {
    "primary-section": PrimarySection,
  },
  props: {
    sections: {
      type: Object,
      required: true,
    },
  },
};
</script>
