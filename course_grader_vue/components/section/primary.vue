<template>
  <div class="mb-3" :aria-labelledby="sectionNameId">
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
      style="max-width: 200px"
      animation="glow"
    />
  </div>

  <ul
    v-if="section.secondary_sections && section.secondary_sections.length"
    class="list-unstyled ms-4"
  >
    <li
      class="mb-3"
      v-for="(secondary, index) in section.secondary_sections"
      :key="secondary.section_id"
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
  formatLinkTitle
} from "@/utils/section";
import { BPlaceholder } from "bootstrap-vue-next";

export default {
  components: {
    SecondarySection,
    BPlaceholder
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
  computed: {
    gradingStatusText() {
      if (this.section.grading_status) {
        return this.section.grading_status;
      } else if (this.errorStatus) {
        return this.formatErrorStatus(this.errorStatus);
      } else if (this.gradingStatus) {
        return this.formatGradingStatus(this.gradingStatus);
      }
    },
    routerLinkTitle() {
      if (this.gradingStatus) {
        return this.formatLinkTitle(this.gradingStatus);
      }
    },
  },
  data() {
    return {
      gradingStatus: null,
      secondaryStatus: [],
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
            this.gradingStatus = data.grading_status;
            if (data.grading_status.hasOwnProperty("secondary_sections")) {
              this.secondaryStatus = data.grading_status.secondary_sections;
            }
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
