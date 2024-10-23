<template>
  <!-- grade submission in progress -->
  <BAlert
    v-if="appState.graderoster.has_inprogress_submissions"
    variant="info"
    :model-value="true"
    class="small d-flex align-items-center"
  >
    <div class="flex-fill me-3">
      <i class="bi bi-exclamation-circle-fill me-1"></i>
      {{ gettext("grade_submission_inprogress") }}.
      {{ gettext("in_progress_submission_email") }}
    </div>
    <div>
      <BLink
        class="btn btn-info btn-sm rounded-3 text-nowrap"
        :href="section.term_url"
        >Return to class list</BLink
      >
    </div>
  </BAlert>

  <BCard class="shadow-sm rounded-3" header-class="p-3" header="Default">
    <template #header>
      <SectionHeader :section="section" :title="gettext('submitted_grades_for')" />

      <template>
        <BDropdown
          v-model="showSectionOptions"
          size="sm"
          variant="outline-secondary"
          no-caret
          class="float-end d-inline-block"
          toggle-class="rounded-2"
        >
          <template #button-content>
            <i class="bi bi-three-dots"></i
          ></template>
          <BDropdownItem :href="section.export_url">
            <i class="bi bi-download me-2 text-body-tertiary"></i>Download Change of Grade
          </BDropdownItem>
          <BDropdownItem href="javascript:window.print()">
            <i class="bi bi-printer me-2 text-body-tertiary"></i>Print this page
          </BDropdownItem>
          <BDropdownDivider />
          <BDropdownItem
            href="https://itconnect.uw.edu/learn/tools/gradepage/assign-submit-grades/"
            target="_blank"
            title="Information on assigning and submitting grades"
            ><i class="bi bi-question-circle me-2 text-body-tertiary"></i>GradePage Help
          </BDropdownItem>
        </BDropdown>
      </template>

      <div
        v-if="!appState.graderoster.is_submission_confirmation"
        class="small"
        role="status"
      >
        {{ gettext("confirmation_alert_warning") }}
        <BLink
          href="https://registrar.washington.edu/staffandfaculty/grading-resources/#faqs"
          target="_blank"
          class="d-print-none"
        >More info.
        </BLink>
      </div>

      <div v-if="appState.graderoster.is_writing_section"
        class="bg-body-secondary p-3 rounded-3"
      >
        <div class="small" role="status">
          {{ gettext("writing_course_note_receipt") }}
        </div>
      </div>
    </template>

    <template v-if="appState.graderoster.is_submission_confirmation">
      <template v-if="appState.graderoster.has_failed_submissions">
        <!-- warning -->
        <BAlert
          v-if="appState.graderoster.has_successful_submissions"
          variant="warning"
          :model-value="true"
          class="small"
        >
          <i class="bi bi-exclamation-triangle-fill me-1"></i>
          {{
            interpolate(
              ngettext(
                "Grades submitted, but one grade had an error.",
                "Grades submitted, but %(failed_submission_count)s grades had errors.",
                appState.graderoster.failed_submission_count
              ),
              appState.graderoster,
              true
            )
          }}
        </BAlert>

        <!-- danger -->
        <BAlert v-else variant="danger" :model-value="true" class="small">
          <i class="bi bi-exclamation-octagon-fill me-1"></i>
          {{
            interpolate(
              ngettext(
                "Grade submitted with error.",
                "Grades submitted with errors.",
                appState.graderoster.failed_submission_count
              ),
              appState.graderoster,
              true
            )
          }}
        </BAlert>
      </template>

      <!-- success -->
      <BAlert v-else variant="success" :model-value="true" class="small">
        <i class="bi bi-check-circle-fill me-1"></i>
        {{ gettext("grade_submission_successful") }}
      </BAlert>
    </template>

    <!-- success -->
    <BAlert
      v-for="submission in appState.graderoster.submissions"
      variant="success"
      :model-value="true"
      class="small"
    >
      <i class="bi bi-check-circle-fill me-1"></i>
      <span v-if="submission.section_id">
        {{ gettext("section") }} {{ submission.section_id }}:
      </span>
      <strong>{{ submission.submitted_count }}</strong>
      {{ gettext("grades_submitted_to_registrar_by") }}
      <strong>{{ submission.submitted_by }}</strong>
      on {{ formatLongDateTime(submission.submitted_date) }}.
      <BLink
        href="https://itconnect.uw.edu/learn/tools/gradepage/change-submitted-grades/"
        target="_blank"
        title="Change submitted grades"
        >Change submitted grades?
      </BLink>
    </BAlert>

    <template>
      <div v-if="appState.graderoster.has_duplicate_codes"
        class="mb-2 pb-2 small text-muted border-bottom"
      >
        {{ gettext("duplicate_code") }}
        <i class="bi bi-circle-fill text-secondary"></i>
      </div>
    </template>

    <ul v-if="appState.graderoster.students"
      class="list-unstyled m-0">
      <li
        v-for="(student, index) in appState.graderoster.students"
        :key="student.item_id"
        class="bpt-2 mt-2"
        :class="index != 0 ? 'border-top' : ''"
      >
        <Student :student="student" />
      </li>
    </ul>
    <ul v-else class="list-unstyled m-0">
      <li v-for="index in 8" class="border-top pt-2 mt-2" :key="index">
        <BPlaceholder
          class="d-block bg-body-secondary"
          style="height: 60px"
          animation="glow"
        />
      </li>
    </ul>

    <div v-if="appState.graderoster.has_grade_imports">
      <div v-if="appState.graderoster.grade_import_count > 1">
        {{ gettext("multi_conversion_scale_msg") }}
        <label class="visually-hidden">
          {{ gettext("multi_conversion_scale_view") }}
        </label>
        <select id="gp-select-scale" @change="showGradeScale($event)">
          <option selected disabled>
            {{ gettext("multi_conversion_scale_option_view") }}
          </option>
          <option
            v-for="(submission, index) in appState.graderoster.submissions"
            v-if="submission.grade_import"
            :value="index"
          >
            Section {{ submission.section_id }}
          </option>
        </select>
      </div>
      <div v-else-if="!selectedGradeScale">
        {{ gettext("conversion_scale_msg") }}
        <BLink
          :title="gettext('conversion_scale_view_title')"
          @click="showGradeScale($event)"
        >
          {{ gettext("conversion_scale_view") }}
        </BLink>
      </div>

      <div v-if="selectedGradeScale">
        <h2 class="visually-hidden">{{ gettext("conversion_scale_header") }}</h2>
        <ol>
          <li v-for="(item, index) in selectedGradeScale">
            <span v-if="index === selectedGradeScale.length - 1">
              <span>&lt; <span>{{ item.min_percentage }}&percnt;</span> &equals; </span>
              <span>{{ lowestValidGrade }}</span>
            </span>
            <span v-else>
              <span>&ge; <span>{{ item.min_percentage }}&percnt;</span> &equals; </span>
              <span>{{ item.grade }}</span>
            </span>
          </li>
        </ol>
        <BLink
          :title="gettext('conversion_scale_hide_title')"
          @click.prevent="hideGradeScale()"
        >
          {{ gettext("conversion_scale_hide") }}
        </BLink>
      </div>
    </div>
  </BCard>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import { useWorkflowStateStore } from "@/stores/state";
import {
  BCard,
  BAlert,
  BLink,
  BPlaceholder,
  BDropdown,
  BDropdownItem,
  BDropdownDivider,
} from "bootstrap-vue-next";
import { formatLongDateTime } from "@/utils/dates";
import { ref } from "vue";

export default {
  components: {
    SectionHeader,
    Student,
    BCard,
    BAlert,
    BLink,
    BPlaceholder,
    BDropdown,
    BDropdownItem,
    BDropdownDivider,
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      selectedGradeScale: null,
      lowestValidGrade: null,
    };
  },
  methods: {
    showGradeScale (ev) {
      var idx = (ev.target.value) ? ev.target.value : 0,
          conversion;

      if (appState.graderoster.submissions[idx]) {
        conversion = appState.graderoster.submissions[idx].import_conversion;
        this.selectedGradeScale = conversion.grade_scale;
        this.lowestValidGrade = conversion.lowest_valid_grade;
      }
    },
    hideGradeScale () {
      this.selectedGradeScale = null;
      this.lowestValidGrade = null;
    },
  },
  setup() {
    const showSectionOptions = ref(false);
    const appState = useWorkflowStateStore();
    return {
      appState,
      formatLongDateTime,
      showSectionOptions,
    };
  },
};
</script>
