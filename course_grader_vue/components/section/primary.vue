<template>
  <div :aria-labelledby="sectionNameId">
    <template v-if="section.section_url">
      <router-link :to="{ path: section.section_url }" :title="routerLinkTitle">
        <h3 :id="sectionNameId">{{ section.display_name }}</h3>
      </router-link>
    </template>
    <template v-else>
      <h3 :id="sectionNameId">{{ section.display_name }}</h3>
    </template>
    <div v-if="section.grading_status">
      {{ section.grading_status }}
    </div>
    <div v-else>{{ gradingStatusText }}</div>
  </div>
  <div v-if="section.secondary_sections && section.secondary_sections.length">
    <ul>
      <li v-for="secondary in section.secondary_sections" :key="secondary.section_id">
        <secondary-section :section="secondary" :gradingStatus="gradingStatus"></secondary-section>
      </li>
    </ul>
  </div>
</template>

<script>
import SecondarySection from "@/components/section/secondary.vue";
import { getSectionStatus } from "@/utils/data";
import { formatGradingStatus, formatLinkTitle } from "@/utils/grading-status";

export default {
  components: {
    "secondary-section": SecondarySection,
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
  },
  setup() {
    return {
      getSectionStatus,
      formatGradingStatus,
      formatLinkTitle,
    };
  },
  data() {
    return {
      gradingStatus: {},
      sectionNameId: "section-name-" + this.section.section_id,
      gradingStatusText: "",
      routerLinkTitle: "",
    };
  },
  methods: {
    loadSecondarySectionStatus: function(gs) {
      var secondary, l, i;
      if (gs.hasOwnProperty("secondary_sections")) {
        for (i = 0, l = gs.secondary_sections.length; i < l; i++) {
          secondary = gs.secondary_sections[i];
          this.gradingStatus[secondary.section_id] = secondary.grading_status;
        }
      }
    },
    loadSectionStatus: function () {
      if (this.section.status_url) {
        this.getSectionStatus(this.section.status_url).then(response => {
          return response.data;
        }).then(data => {
          this.gradingStatusText = this.formatGradingStatus(data.grading_status);
          this.routerLinkTitle = this.formatLinkTitle(data.grading_status);
          this.loadSecondarySectionStatus(data.grading_status);
        }).catch(error => {
          console.log(error.message);
        });
      }
    },
  },
  created() {
    if (!this.section.grading_status) {
      this.loadSectionStatus();
    }
  },
};
</script>
