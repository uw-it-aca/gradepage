<template>
  <BCard class="shadow-sm rounded-3" header-class="p-3" header="Default">
    <template #header>
      <SectionHeader :section="section" title="Convert grades for" />
    </template>

    <h3>Convert Final Score to Grade Points</h3>
    <p>
      To use the conversion calculator, enter minimum percentages and equivalent class grades in two or more rows in the calculator, and click <strong>Apply</strong>. The calculator fills in the rest of the grade point scale.
    </p>

    <div v-if="courseGradingSchemes.length">
      <label for="course-scale-select" class="visually-hidden">
        Convert grades using a Canvas grading scheme:
      </label>
      <BDropdown
        id="course-scale-select"
        size="sm"
        variant="outline-secondary"
        class="d-inline-block"
      >
        <template #button-content>
          Use the Canvas grading scheme from your course
        </template>
        <BDropdownItem
          v-for="scheme in courseGradingSchemes"
          :value="scheme"
          @click.prevent="courseGradingSchemeSelected(scheme)"
        >{{ scheme.course_name }}&nbsp;({{ scheme.grading_scheme_name }})
        </BDropdownItem>
      </BDropdown>
    </div>

    <div v-if="previousScales && previousScales.terms.length">
      <label for="previous-scale-select" class="visually-hidden">
        Convert grades using a scale that you have used before:
      </label>
      <BDropdown
        id="previous-scale-select"
        size="sm"
        variant="outline-secondary"
        class="d-inline-block"
      >
        <template #button-content>
          Use one of your previous conversion scales
        </template>
        <BDropdownGroup
          v-for="term in previousScales.terms"
          :header="term.quarter + ' ' + term.year"
        >
          <BDropdownItem
            v-for="scale in term.conversion_scales"
            :value="scale"
            @click.prevent="previousScaleSelected(scale)"
          >{{ scale.section }}</BDropdownItem>
        </BDropdownGroup>
      </BDropdown>
    </div>

    <GradeConversionCalculator />

    <template #footer>
      <BLink
        title="Cancel"
        @click="cancelConversion"
      >Cancel
      </BLink>
      <BButton
        variant="primary"
        title="Review converted grades"
        @click="reviewConversion"
      >Review converted grades &gt;&gt;
      </BButton>
      <span
        v-if="scaleErrorCount"
        role="alert"
        class="text-danger invalid-grade small"
      >
        <strong>{{ scaleErrorText }}</strong> (see above)
      </span>
    </template>
  </BCard>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import GradeConversionCalculator from "@/components/convert/calculator.vue";
import Student from "@/components/student.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { useCalculatorStore } from "@/stores/calculator";
import {
  BCard,
  BButton,
  BLink,
  BDropdown,
  BDropdownItem,
  BDropdownGroup,
} from "bootstrap-vue-next";

export default {
  props: {
    section: {
      type: Object,
      required: true,
    },
  },
  components: {
    SectionHeader,
    GradeConversionCalculator,
    Student,
    BCard,
    BButton,
    BLink,
    BDropdown,
    BDropdownItem,
    BDropdownGroup,
  },
  setup() {
    const appState = useWorkflowStateStore();
    const calculatorStore = useCalculatorStore();
    return {
      appState,
      calculatorStore,
    };
  },
  data() {
    return {
      scaleErrorCount: 0,
    };
  },
  computed: {
    previousScales() {
      return this.calculatorStore.previousScales;
    },
    courseGradingSchemes() {
      return this.appState.gradeImport.course_grading_schemes;
    },
    scaleErrorText() {
      return interpolate(ngettext(
        "One invalid grade", "%(count)s invalid grades", this.scaleErrorCount),
          {count: this.scaleErrorCount}, true);
    },
  },
  methods: {
    courseGradingSchemeSelected: function (scheme) {
      this.calculatorStore.initializeCalculator(scheme);
    },
    previousScaleSelected: function (scale) {
      this.calculatorStore.initializeCalculator(scale);
    },
    cancelConversion: function () {
      this.appState.$reset();
    },
    reviewConversion: function() {
      this.scaleErrorCount = this.calculatorStore.validateScaleValues();
      if (this.scaleErrorCount === 0) {
        this.appState.convertImportedGrades(
          this.calculatorStore.scaleValues,
          this.calculatorStore.lowestValidGrade
        );
        this.appState.reviewConversion();
      }
    },
  },
};
</script>
