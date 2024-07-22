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
    <div v-if="section.grading_status"  id="section-status-{{ section.section_id }}">
      {{ section.grading_status }}
    </div>
    <div v-else>{{ gradingStatus }}</div>
  </div>
</template>

<script>
import { getSectionStatus } from "@/utils/data";
import { formatLongDateTime } from "@/utils/dates";

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
      formatLongDateTime,
    };
  },
  data() {
    return {
      gradingStatus: "",
      linkTitle: "",
    };
  },
  methods: {
    formatGradngStatus: function(data) {
      let gs = data.grading_status;

      if (gs.unsubmitted_count && gs.grading_period_open) {
        this.linkTitle = "Submit grades for " + gs.display_name;
        this.gradingStatus = (gs.unsubmitted_count > 1)
          ? gs.unsubmitted_count + " grades to submit"
          : "One grade to submit";
      } else {
        if (gs.submitted_count) {
          if (gs.submitted_date) {
            this.linkTitle = "View grade receipt for " + gs.display_name;
            if (gs.accepted_date) {
              submitted_date = this.formatLongDateTime(gs.submitted_date);
              this.gradingStatus = (gs.submitted_count > 1)
                ? gs.submitted_count + " grades submitted on " + submitted_date
                : "One grade submitted on " + submitted_date;
            } else {
              this.gradingStatus = (gs.submitted_count > 1)
                ? gs.submitted_count + " grade submissions in progress"
                : "One grade submission in progress";
            }
          } else {
            this.gradingStatus = (gs.submitted_count > 1)
              ? gs.submitted_count + " grades submitted"
              : "One grade submitted";
          }
        } else {
          if (!gs.grading_period_open) {
            this.gradingStatus = "No submission information";
          }
        }
      }
    },
    formatErrorStatus: function (error) {
      this.gradingStatus = error.message; // TODO: actually format
    },
    loadSectionStatus: function () {
      if (this.section.status_url) {
        this.getSectionStatus(this.section.status_url).then(response => {
          return response.data;
        }).then(data => {
          this.formatGradngStatus(data);
        }).catch(error => {
          this.formatErrorStatus(error);
        });
      }
    },
  },
  created() {
    this.loadSectionStatus();
  },
};
</script>
