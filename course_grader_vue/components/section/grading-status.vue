<template>
  <template v-if="graderoster.has_successful_submissions">
    <BCard bg-variant="body-tertiary" class="border-0 mb-4">
      <div v-if="savedGrades" class="border-bottom mb-2 pb-2">
        <span class="fw-bold">
          <i class="bi bi-exclamation-triangle-fill text-warning me-2"></i>
          Resubmit to make any changes official.
        </span>
        Otherwise, the most recent grade submission will stand.
      </div>
      <div v-if="
        graderoster.is_primary_section &&
        graderoster.linked_section_count > 1"
      >
        <!-- primary section with more than one linked section -->
        <div class="d-flex justify-content-between">
          <div>
            <div class="fw-bold ms-4">
              Course sections submitted.
              {{ graderoster.submissions.length }} of
              {{ graderoster.linked_section_count }}
            </div>
            <div class="fst-italic small ms-4">
              Submitted grades may differ from official final grade.
              <BLink
                to="https://registrar.washington.edu/staff-faculty/grading-resources/"
                >Learn why</BLink
              >.
            </div>
          </div>
          <div>
            <BButton v-b-toggle.collapse-1 variant="quiet-primary" size="sm"
              >Show sections</BButton
            >
          </div>
        </div>
        <BCollapse id="collapse-1">
          <ul class="list-unstyled mt-2 ms-4">
            <li
              v-for="(submission, index) in graderoster.submissions"
              :key="index"
            >
              <i class="bi bi-check-circle-fill text-success me-2"></i>
              <span v-if="submission.section_id"
                >Section {{ submission.section_id }}:
              </span>
              <span v-html="gradesSubmittedText(submission)"></span>
            </li>
          </ul>
        </BCollapse>
      </div>
      <div v-else>
        <!-- primary section with zero or one linked section, or a linked section -->
        <ul class="list-unstyled m-0">
          <li>
            <i class="bi bi-check-circle-fill text-success me-2"></i>
            <span v-if="graderoster.submissions[0].section_id"
              >Section {{ graderoster.submissions[0].section_id }}:
            </span>
            <span
              v-html="gradesSubmittedText(graderoster.submissions[0])">
            </span>
          </li>
        </ul>
        <div class="fst-italic small ms-4">
          Submitted grades may differ from official final grade.
          <BLink
            to="https://registrar.washington.edu/staff-faculty/grading-resources/"
            >Learn why</BLink
          >.
        </div>
      </div>
    </BCard>
  </template>
  <!-- No submissions, grading period closed -->
  <template v-else-if=
    "!graderoster.submissions.length && !graderoster.gradable_student_count"
  >
    <BCard bg-variant="body-tertiary" class="border-0 mb-4">
      <div class="d-flex justify-content-between">
        <div>
          <div class="fw-bold ms-4">
            No grades were submitted for this section.
          </div>
        </div>
      </div>
    </BCard>
  </template>
</template>

<script>
import {
  BCard,
  BLink,
  BButton,
  BCollapse,
} from "bootstrap-vue-next";
import { gradesSubmittedText } from "@/utils/grade";

export default {
  name: "SectionGradingStatus",
  components: {
    BCard,
    BLink,
    BButton,
    BCollapse,
  },
  props: {
    graderoster: {
      type: Object,
      required: true,
    },
    savedGrades: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  setup() {
    return {
      gradesSubmittedText,
    };
  },
  data() {
    return {};
  },
};
</script>
