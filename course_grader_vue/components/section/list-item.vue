<template>
  <div aria-labelledby="section-name-{{ section.section_id }}">
    <template v-if="section.section_url">
      <router-link :to="{ path: section.section_url }" :title="linkTitle">
        <h3 id="section-name-{{ section.section_id }}">{{ section.display_name }}</h3>
      </router-link>
    </template>
    <template v-else>
      <h3 id="section-name-{{ section.section_id }}">{{ section.display_name }}</h3>
    </template>
    <div id="section-status-{{ section.section_id }}">{{ gradingStatus }}</div>
  </div>
</template>

<script>
import { getSectionStatus } from "@/utils/data";

export default {
  props: {
    section: {
      type: Object,
      required: true,
    },
  },
  setup() {
    return {
      getSectionStatus,
    };
  },
  data() {
    return {
      gradingStatus: {},
      linkTitle: "Default title",
    };
  },
  methods: {
    createGradngStatus: function(data) {
      let gs = data.grading_status,
          section_name = gs.display_name,
          text = "";

      if (gs.unsubmitted_count && gs.grading_period_open) {
        this.linkTitle = "Submit grades for " + section_name;
        this.gradingStatus = (gs.unsubmitted_count > 1)
          ? gs.unsubmitted_count + " grades to submit"
          : "One grade to submit";
      } else {
        this.gradingStatus = text;
      }
    },
    loadSectionStatus: function () {
      if (this.section.status_url) {
        this.getSectionStatus(this.section.status_url).then(response => {
          return response.data;
        }).then(data => {
          this.createGradngStatus(data);
        }).catch(error => {
          this.gradingStatus = error.message; // TODO: create error msg
        });
      }
    },
  },
  created() {
    this.loadSectionStatus();
  },
};
</script>
