<template>
  <div :aria-labelledby="sectionNameId">
    <template v-if="section.section_url">
      <RouterLink :to="{ path: section.section_url }" :title="routerLinkTitle">
        <div class="fs-4":id="sectionNameId">{{ section.display_name }}</div>
      </RouterLink>
    </template>
    <template v-else>
      <div class="fs-4" :id="sectionNameId">{{ section.display_name }}</div>
    </template>
    <div>
      <BPlaceholder
        v-if="isLoading"
        class="bg-light-gray"
        style="max-width: 9rem"
        animation="glow"
      /><template v-else>{{ gradingStatusText }}</template>
    </div>
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
      default: {},
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
      } else if (this.section.status_url) {
        return this.formatGradingStatus(this.secondaryStatus);
      } else {
        return this.formatGradingStatus(this.gradingStatus);
      }
    },
    routerLinkTitle() {
      if (this.section.status_url) {
        return this.formatLinkTitle(this.secondaryStatus);
      } else {
        return this.formatLinkTitle(this.gradingStatus);
      }
    },
  },
  data() {
    return {
      isLoading: true,
      secondaryStatus: {},
      errorStatus: "",
      sectionNameId: "section-name-" + this.section.section_id,
    };
  },
  methods: {
    loadSectionStatus: function () {
      if (this.section.status_url) {
        this.getSectionStatus(this.section.status_url).then(response => {
          return response.data;
        }).then(data => {
          this.isLoading = false;
          this.secondaryStatus = data.grading_status;
        }).catch(error => {
          this.isLoading = false;
          this.errorStatus = error.message;
        });
      } else {
          return this.gradingStatus;
      }
    },
  },
  created() {
    setTimeout(() => {
      this.loadSectionStatus();
    }, 1000);
  },
};
</script>
