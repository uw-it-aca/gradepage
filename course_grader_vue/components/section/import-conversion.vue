<template>
  <template v-if="submissionsWithImportConversions.length">
    <div v-if="submissionsWithImportConversions.length > 1">
      Grades calculated using grade conversion scales.
      <label class="visually-hidden">
        Select a grade conversion scale to view:
      </label>
      <BDropdown
        v-model="selectedImportConversion"
        size="sm"
        variant="outline-secondary"
        no-caret
        class="float-end d-inline-block"
        toggle-class="rounded-2"
      >
        <template #button-content> View Scale </template>
        <template>
          <BDropdownItem
            v-for="(submission, index) in submissionsWithImportConversions"
            :key="index"
            :value="submission.grade_import.import_conversion"
          >
            <i class="me-2 text-body-tertiary"></i>
            Section {{ submission.section_id }}
          </BDropdownItem>
        </template>
      </BDropdown>
    </div>
    <div v-else>
      Grades calculated using a grade conversion scale.
      <BLink
        title="Show the grade conversion scale that was used"
        @click.prevent="showImportConversion()"
        >View scale
      </BLink>
    </div>
    <div v-if="selectedImportConversion">
      <h2 class="visually-hidden">Grade Conversion Scale</h2>
      <ol>
        <li v-for="(row, index) in importConversionRows" :key="index">
          <span
            >&ge; <span>{{ row.min_percentage }}&percnt;</span> &equals;
          </span>
          <span>{{ row.grade }}</span>
        </li>
        <li>
          <span>&lt; <span>{{
              importConversionRows[importConversionRows.length - 1].min_percentage
            }}&percnt;</span> &equals;
          </span>
          <span>{{ selectedImportConversion.lowest_valid_grade }}</span>
        </li>
      </ol>
      <BLink
        title="Hide grade conversion scale"
        @click.prevent="hideImportConversion()"
        >Hide scale
      </BLink>
    </div>
  </template>
</template>

<script>
import {
  BLink,
  BDropdown,
  BDropdownItem,
} from "bootstrap-vue-next";

export default {
  name: "ImportConversions",
  components: {
    BLink,
    BDropdown,
    BDropdownItem,
  },
  props: {
    submissions: {
      type: Array,
      required: true,
    },
  },
  setup() {
    return {};
  },
  data() {
    return {
      selectedImportConversion: null,
    };
  },
  computed: {
    submissionsWithImportConversions() {
      return this.submissions.filter(
        submission => (
          submission.grade_import !== null &&
          submission.grade_import.import_conversion !== null
        )
      );
    },
    importConversionRows() {
      if (this.selectedImportConversion !== null) {
        return this.selectedImportConversion.grade_scale.filter(
           row => row.min_percentage !== null);
      }
    },
  },
  methods: {
    showImportConversion: function () {
      this.selectedImportConversion = this.submissionsWithImportConversions[
        0].grade_import.import_conversion;
    },
    hideImportConversion: function () {
      this.selectedImportConversion = null;
    },
  },
};
</script>
