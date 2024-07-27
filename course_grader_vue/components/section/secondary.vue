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
    <div>{{ gradingStatusText }}</div>
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
      default: null,
    },
  },
  setup() {
    return {
      getSectionStatus,
      formatGradingStatus,
      formatLinkTitle,
    };
  },
  computed: {
    gradingStatusText() {
      if (this.section.grading_status) {
        return this.section.grading_status;
      } else if (this.errorStatus) {
        return this.errorStatus;
      } else if (this.secondaryStatus) {
        return this.formatGradingStatus(this.secondaryStatus);
      } else {
        return this.formatGradingStatus(this.gradingStatus);
      }
    },
    routerLinkTitle() {
      if (this.secondaryStatus) {
        return this.formatLinkTitle(this.secondaryStatus);
      } else {
        return this.formatLinkTitle(this.gradingStatus);
      }
    },
  },
  data() {
    return {
      secondaryStatus: null,
      errorStatus: null,
      sectionNameId: "section-name-" + this.section.section_id,
    };
  },
  methods: {
    loadGradingStatus: function () {
      if (this.section.status_url) {
        this.getSectionStatus(this.section.status_url).then(response => {
          return response.data;
        }).then(data => {
          // Secondary status overrules the prop
          this.secondaryStatus = data.grading_status;
        }).catch(error => {
          this.errorStatus = error.message;
        });
      }
    },
  },
  created() {
    this.loadGradingStatus();
  },
};
</script>
