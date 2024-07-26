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
</template>

<script>
import { getSectionStatus } from "@/utils/data";
import { formatGradingStatus, formatLinkTitle } from "@/utils/grading-status";

export default {
  props: {
    section: {
      type: Object,
      required: true,
    },
    gradingStatus: {
      type: Object,
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
      sectionNameId: "section-name-" + this.section.section_id,
      gradingStatusText: "",
      routerLinkTitle: "",
    };
  },
  methods: {
    applyGradingStatus: function (grading_status) {
      this.gradingStatusText = this.formatGradingStatus(grading_status);
      this.routerLinkTitle = this.formatLinkTitle(grading_status);
    },
    loadSectionStatus: function () {
      if (this.section.status_url) {
        this.getSectionStatus(this.section.status_url).then(response => {
          return response.data;
        }).then(data => {
          this.applyGradingStatus(data.grading_status);
        }).catch(error => {
          console.log(error.message);
        });
      } else {
        // Check for a grading status in the prop
        let grading_status = this.gradingStatus.find((gs) =>
          gs.section_id === this.section.section_id
        );
        if (grading_status) {
          this.applyGradingStatus(grading_status);
        }
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
