<template>
  <div :aria-labelledby="sectionNameId">
    <template v-if="section.section_url">
      <BLink :href="section.section_url" :title="routerLinkTitle">
        <div class="fs-4" :id="sectionNameId">{{ section.display_name }}</div>
      </BLink>
    </template>
    <template v-else>
      <div class="fs-4" :id="sectionNameId">{{ section.display_name }}</div>
    </template>

    <div v-if="gradingStatusText">{{ gradingStatusText }}</div>
    <BPlaceholder
      v-else
      class="bg-light-gray"
      style="max-width: 9rem"
      animation="glow"
    />
  </div>
</template>

<script>
import { getSectionStatus } from "@/utils/data";
import {
  formatGradingStatus,
  formatErrorStatus,
  formatLinkTitle
} from "@/utils/section";
import { BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    BPlaceholder
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
    gradingStatus: {
      type: Object,
      default: undefined,
    },
  },
  setup() {
    return {
      getSectionStatus,
      formatGradingStatus,
      formatErrorStatus,
      formatLinkTitle,
    };
  },
  computed: {
    gradingStatusText() {
      if (this.section.grading_status) {
        return this.section.grading_status;
      } else if (this.errorStatus) {
        return this.formatErrorStatus(this.errorStatus);
      } else if (this.secondaryStatus) {
        return this.formatGradingStatus(this.secondaryStatus);
      } else if (this.gradingStatus) {
        return this.formatGradingStatus(this.gradingStatus);
      }
    },
    routerLinkTitle() {
      if (this.secondaryStatus) {
        return this.formatLinkTitle(this.secondaryStatus);
      } else if (this.gradingStatus) {
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
        this.getSectionStatus(this.section.status_url)
          .then((response) => {
            return response.data;
          })
          .then((data) => {
            // Secondary status overrules the prop
            this.secondaryStatus = data.grading_status;
          })
          .catch((error) => {
            this.errorStatus = error.response;
          });
      }
    },
  },
  created() {
    setTimeout(() => {
      this.loadGradingStatus();
    }, 1000);
  },
};
</script>
