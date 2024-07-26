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
      section_id: this.section.section_id,
    };
  },
  methods: {
    loadSectionStatus: function () {
      if (this.section.status_url) {
        this.getSectionStatus(this.section.status_url).then(response => {
          return response.data;
        }).then(data => {
          this.gradingStatusText = this.formatGradingStatus(data.grading_status);
          this.routerLinkTitle = this.formatLinkTitle(data.grading_status);
        }).catch(error => {
          console.log(error.message);
        });
      } else {
        if (this.gradingStatus.hasOwnProperty(this.section_id)) {
          this.updateGradingStatusUI(this.gradingStatus[this.section_id]);
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
