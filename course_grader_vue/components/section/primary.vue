<template>
  <div class="mb-3" :aria-labelledby="sectionNameId">
    <template v-if="section.section_url">
      <BLink :href="section.section_url" :title="routerLinkTitle">
        <div :id="sectionNameId" class="fs-4">{{ section.display_name }}</div>
      </BLink>
    </template>
    <template v-else>
      <div :id="sectionNameId" class="fs-4">{{ section.display_name }}</div>
    </template>

    <div v-if="gradingStatusText">{{ gradingStatusText }}</div>
    <BPlaceholder
      v-else
      class="bg-body-secondary"
      style="max-width: 200px"
      animation="glow"
    />
  </div>

  <ul
    v-if="section.secondary_sections && section.secondary_sections.length"
    class="list-unstyled ms-4"
  >
    <li
      v-for="(secondary, index) in section.secondary_sections"
      :key="secondary.section_id"
      class="mb-3"
    >
      <SecondarySection
        :section="secondary"
        :grading-status="secondaryStatus[index]"
      ></SecondarySection>
    </li>
  </ul>
</template>

<script>
import SecondarySection from "@/components/section/secondary.vue";
import { getSectionStatus } from "@/utils/data";
import {
  formatGradingStatus,
  formatErrorStatus,
  formatLinkTitle,
} from "@/utils/section";
import { BPlaceholder, BLink } from "bootstrap-vue-next";

export default {
  name: "SectionPrimary",
  components: {
    SecondarySection,
    BPlaceholder,
    BLink,
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
      formatErrorStatus,
      formatLinkTitle,
    };
  },
  data() {
    return {
      gradingStatus: null,
      secondaryStatus: [],
      errorStatus: null,
      sectionNameId: "section-name-" + this.section.section_id,
      isLoading: false,
    };
  },
  computed: {
    gradingStatusText() {
      if (this.section.grading_status) {
        return this.section.grading_status;
      } else if (this.errorStatus) {
        return this.formatErrorStatus(this.errorStatus);
      } else if (this.gradingStatus) {
        return this.formatGradingStatus(this.gradingStatus);
      } else {
        return "";
      }
    },
    routerLinkTitle() {
      if (this.gradingStatus) {
        return this.formatLinkTitle(this.gradingStatus);
      } else {
        return "";
      }
    },
  },
  created() {
    this.loadGradingStatus();
  },
  methods: {
    loadGradingStatus: function () {
      if (this.section.status_url) {
        this.isLoading = true;
        this.getSectionStatus(this.section.status_url)
          .then((data) => {
            this.gradingStatus = data.grading_status;
            if (data.grading_status.hasOwnProperty("secondary_sections")) {
              this.secondaryStatus = data.grading_status.secondary_sections;
            }
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
