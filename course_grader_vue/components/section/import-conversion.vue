<template>
  <template v-if="submissionsWithImportConversions.length">
    <div v-if="submissionsWithImportConversions.length > 1">
      Grades calculated using grade conversion scales.
      <label class="visually-hidden">
        Select a grade conversion scale to view:
      </label>
      <BDropdown
        size="sm"
        text="Select a conversion scale to view"
        class="float-end d-inline-block"
        variant="outline-secondary"
        toggle-class="rounded-2"
      >
        <BDropdownItemButton
          v-for="(submission, index) in submissionsWithImportConversions"
          :key="index"
          :value="submission"
          @click.prevent="showImportConversion(submission)"
        >
          <i class="me-2 text-body-tertiary"></i>
          Section {{ submission.section_id }}
        </BDropdownItemButton>
      </BDropdown>
    </div>
    <div v-else>
      Grades calculated using a grade conversion scale.
      <BLink
        title="Show the grade conversion scale that was used"
        @click.prevent="showImportConversion(submissionsWithImportConversions[0])"
        >View scale
      </BLink>
    </div>
    <div v-if="selectedImportConversion">
      <h2 class="visually-hidden">Grade Conversion Scale</h2>
      <table class="table table-striped">
        <thead class="table-body-secondary">
          <tr>
            <th scope="col">Minimum Percentage</th>
            <th scope="col">Grade</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in importConversionRows" :key="index">
            <td>&ge; {{ row.min_percentage }}&percnt;</td>
            <td>{{ row.grade }}</td>
          </tr>
          <tr>
            <td>
              &lt;
              {{
                importConversionRows[importConversionRows.length - 1]
                  .min_percentage
              }}&percnt;
            </td>
            <td>{{ selectedImportConversion.lowest_valid_grade }}</td>
          </tr>
        </tbody>
      </table>
      <BLink
        title="Hide grade conversion scale"
        @click.prevent="hideImportConversion()"
        >Hide scale
      </BLink>
    </div>
  </template>
</template>

<script>
import { BLink, BDropdown, BDropdownItem, BDropdownItemButton } from "bootstrap-vue-next";

export default {
  name: "ImportConversions",
  components: {
    BLink,
    BDropdown,
    BDropdownItem,
    BDropdownItemButton,
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
        (submission) =>
          submission.grade_import !== null &&
          submission.grade_import.import_conversion !== null
      );
    },
    importConversionRows() {
      if (this.selectedImportConversion !== null) {
        return this.selectedImportConversion.grade_scale.filter(
          (row) => row.min_percentage !== null
        );
      }
      return [];
    },
  },
  methods: {
    showImportConversion: function (submission) {
      this.selectedImportConversion = submission.grade_import.import_conversion;
    },
    hideImportConversion: function () {
      this.selectedImportConversion = null;
    },
  },
};
</script>
