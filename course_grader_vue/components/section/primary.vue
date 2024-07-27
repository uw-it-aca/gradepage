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
  <div v-if="section.secondary_sections && section.secondary_sections.length">
    <ul>
      <li v-for="(secondary, index) in section.secondary_sections" :key="secondary.section_id">
        <secondary-section :section="secondary" :grading-status="secondaryStatus[index]"></secondary-section>
      </li>
    </ul>
  </div>
</template>

<script>
import SecondarySection from "@/components/section/secondary.vue";
import { getSectionStatus } from "@/utils/data";
import { formatGradingStatus, formatLinkTitle } from "@/utils/grading-status";

export default {
  components: {
    "secondary-section": SecondarySection,
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
      formatLinkTitle,
    };
  },
  computed: {
    gradingStatusText() {
      if (this.section.grading_status)  {
        return this.section.grading_status;
      } else if (this.errorStatus) {
        return this.errorStatus;
      } else {
        return this.formatGradingStatus(this.gradingStatus);
      }
    },
    routerLinkTitle() {
      return this.formatLinkTitle(this.gradingStatus);
    },
  },
  data() {
    return {
      gradingStatus: {},
      secondaryStatus: [],
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
          this.gradingStatus = data.grading_status;
          this.secondaryStatus = data.grading_status.secondary_sections;
        }).catch(error => {
          this.errorStatus = error.message;
        });
      }
    },
  },
  created() {
    this.loadSectionStatus();
  },
};
</script>
