<template>
    <ul class="list-unstyled">
      <li v-for="section in sections" :key="section.section_id" class="mb-3">
        <PrimarySection :section="section"></PrimarySection>
      </li>
    </ul>
</template>

<script>
import PrimarySection from "@/components/section/primary.vue";

export default {
  components: {
    PrimarySection,
  },
  props: {
    sections: {
      type: Object,
      required: true,
    },
  },
};
</script>
