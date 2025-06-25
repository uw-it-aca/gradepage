<template>
  <div class="" :aria-labelledby="sectionNameId">
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

    <div v-if="isLoading">Loading primary grading status text...</div>
    <template v-else>
      <div
        class="d-flex"
        :class="!gradesAccepted ? 'text-body' : 'text-secondary'"
        v-html="gradingStatusText"
      ></div>

      <div v-if="savedGradeWarning" class="mt-2 border border-warning">
        <div class="fw-bold">
          <i class="bi bi-exclamation-triangle-fill text-warning me-2"></i
          >Resubmit to make any changes official.
        </div>
        <div class="text-secondary small">
          Otherwise, the most recent grade submission on
          {{ formatLongDateTime(gradingStatus.submitted_date) }} will stand.
        </div>
      </div>
    </template>
  </div>

  <ul
    v-if="section.secondary_sections && section.secondary_sections.length"
    class="list-unstyled ms-5"
  >
    <li
      v-for="(secondary, index) in section.secondary_sections"
      :key="secondary.section_id"
      class="py-4"
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
import { formatLongDateTime } from "@/utils/dates";
import {
  formatGradingStatus,
  formatErrorStatus,
  formatLinkTitle,
} from "@/utils/section";
import { BPlaceholder, BLink, BBadge } from "bootstrap-vue-next";
import { useWorkflowStateStore } from "@/stores/state";
import { useGradeStore } from "@/stores/grade";

export default {
  name: "SectionPrimary",
  components: {
    SecondarySection,
    BPlaceholder,
    BLink,
    BBadge,
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
  },
  setup() {
    const appState = useWorkflowStateStore();
    const gradeStore = useGradeStore();

    return {
      getSectionStatus,
      formatGradingStatus,
      formatErrorStatus,
      formatLinkTitle,
      formatLongDateTime,
      appState,
      gradeStore,
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
        console.log(
          "primary.vue, section.grading_status: " + this.section.grading_status
        );
        return this.section.grading_status;
      } else if (this.errorStatus) {
        console.log(
          "primary.vue, errorStatus: " + JSON.stringify(this.errorStatus)
        );
        return this.formatErrorStatus(this.errorStatus);
      } else if (this.gradingStatus) {
        console.log(
          "primary.vue, gradingStatus: " + JSON.stringify(this.gradingStatus)
        );
        return this.formatGradingStatus(this.gradingStatus);
      }
      return "";
    },
    routerLinkTitle() {
      return this.gradingStatus ? this.formatLinkTitle(this.gradingStatus) : "";
    },
    gradesAccepted() {
      return this.gradingStatus
        ? this.gradingStatus.accepted_date !== null
        : false;
    },
    savedGradeWarning() {
      if (this.gradingStatus) {
        return (
          this.gradingStatus.grading_period_open &&
          this.gradingStatus.accepted_date !== null &&
          this.gradingStatus.saved_count > 0
        )
      }
      return false;
    },
  },
  created() {
    this.loadGradingStatus();
  },
  methods: {
    loadGradingStatus: function () {
      if (this.section.status_url) {
        this.isLoading = true;

        setTimeout(() => {
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
        }, 2000);
      }
    },
  },
};
</script>
