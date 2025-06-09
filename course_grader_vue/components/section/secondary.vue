<template>
  <div :aria-labelledby="sectionNameId">
    <div class="d-flex">
      <template v-if="section.section_url">
        <BLink :href="section.section_url" :title="routerLinkTitle">
          <div :id="sectionNameId" class="fs-4">{{ section.display_name }}</div>
        </BLink>
      </template>
      <template v-else>
        <div :id="sectionNameId" class="fs-4">{{ section.display_name }}</div>
      </template>
      <div class="ms-2">
        <BBadge
          v-if="gradesAccepted"
          pill
          bg-variant="success-subtle"
          text-variant="success-emphasis"
          class="fw-semibold me-1"
          >submitted</BBadge
        >
      </div>
    </div>

    <div v-if="gradingStatusText" class="d-flex">
      <div>{{ gradingStatusText }}</div>
      <div v-if="gradesAccepted" class="text-success fw-bold ms-3">
        <i class="bi bi-check-circle-fill"></i>
      </div>
    </div>
    <BPlaceholder
      v-else
      class="bg-body-secondary"
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
  formatLinkTitle,
} from "@/utils/section";
import { BPlaceholder, BBadge, BLink } from "bootstrap-vue-next";

export default {
  name: "SectionSecondary",
  components: {
    BPlaceholder,
    BLink,
    BBadge,
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
  data() {
    return {
      secondaryStatus: null,
      errorStatus: null,
      sectionNameId: "section-name-" + this.section.section_id,
      isLoading: false,
    };
  },
  computed: {
    gradingStatusText() {
      if (this.section.grading_status) {
        console.log(
          "secondary.vue, section.grading_status: " +
            this.section.grading_status
        );
        return this.section.grading_status;
      } else if (this.errorStatus) {
        console.log(
          "secondary.vue, errorStatus: " + JSON.stringify(this.errorStatus)
        );
        return this.formatErrorStatus(this.errorStatus);
      } else if (this.secondaryStatus) {
        console.log(
          "secondary.vue, secondaryStatus: " +
            JSON.stringify(this.secondaryStatus)
        );
        return this.formatGradingStatus(this.secondaryStatus);
      } else if (this.gradingStatus) {
        console.log(
          "secondary.vue, gradingStatus: " + JSON.stringify(this.gradingStatus)
        );
        return this.formatGradingStatus(this.gradingStatus);
      }
      return "";
    },
    routerLinkTitle() {
      if (this.secondaryStatus) {
        return this.formatLinkTitle(this.secondaryStatus);
      } else if (this.gradingStatus) {
        return this.formatLinkTitle(this.gradingStatus);
      }
      return "";
    },
    gradesAccepted() {
      if (this.secondaryStatus) {
        return this.secondaryStatus.accepted_date !== null;
      } else if (this.gradingStatus) {
        return this.gradingStatus.accepted_date !== null;
      }
      return false;
    },
  },
  created() {
    setTimeout(() => {
      this.loadGradingStatus();
    }, 1000);
  },
  methods: {
    loadGradingStatus: function () {
      if (this.section.status_url) {
        this.isLoading = true;
        this.getSectionStatus(this.section.status_url)
          .then((data) => {
            // Secondary status overrules the prop
            this.secondaryStatus = data.section.grading_status;
          })
          .catch((error) => {
            this.errorStatus = error.data;
          })
          .finally(() => {
            this.isLoading = false;
          });
      }
    },
  },
};
</script>
