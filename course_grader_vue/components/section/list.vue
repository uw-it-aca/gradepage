<template>
  <div>
    <ul>
      <li v-for="section in sections" :key="section.section_id" id="section-{{section.section_id}}">
        <section-list-item :section="section"></section-list-item>
        <div v-if="section.secondary_sections && section.secondary_sections.length">
          <ul>
            <li v-for="secondary in section.secondary_sections" :key="secondary.section_id" id="section-{{secondary.section_id}}">
              <section-list-item :section="secondary"></section-list-item>
            </li>
          </ul>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import SectionListItem from "@/components/section/list-item.vue";

export default {
  components: {
    "section-list-item": SectionListItem,
  },
  props: {
    sections: {
      type: Object,
      required: true,
    },
  },
};
</script>
