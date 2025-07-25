<template>
  <h1 class="fs-1 fw-bold">Import Grades</h1>
  <div class="d-flex justify-content-between align-items-end mb-5">
    <SectionHeader :section="section" title="Convert Grades" />
    <div>
      <BDropdown
        id="import-scale-selector"
        size="sm"
        text="Choose Grade Scale"
        variant="outline-primary"
        class=""
        toggle-class="rounded-2"
      >
        <BDropdownItemButton
          v-for="(scale, index) in calculatorStore.availableScales"
          :key="index"
          :value="scale"
          @click.prevent="calculatorStore.setScale(scale)"
          >{{ gettext("conversion_scale_" + scale) }}
        </BDropdownItemButton>
      </BDropdown>
    </div>
  </div>

  <h3>
    Grade Scale:
    {{ gettext("conversion_scale_" + calculatorStore.selectedScale) }}
  </h3>
  <p>Convert Final Score to Grade Points</p>

  <div v-if="courseGradingSchemes.length" class="mb-4">
    <label for="course-scale-select" class="d-block">
      Convert grades using a Canvas grading scheme:
    </label>
    <BDropdown
      id="course-scale-select"
      size="sm"
      variant="outline-primary rounded-2"
      class="d-inline-block"
      text=" Use the Canvas grading scheme from your course"
    >
      <BDropdownItemButton
        v-for="(scheme, index) in courseGradingSchemes"
        :key="index"
        :value="scheme"
        @click.prevent="courseGradingSchemeSelected(scheme)"
        >{{ scheme.course_name }}&nbsp;({{ scheme.grading_scheme_name }})
      </BDropdownItemButton>
    </BDropdown>
  </div>

  <div v-if="previousScales && previousScales.terms.length" class="mb-4">
    <label for="previous-scale-select" class="d-block">
      Convert grades using a scale that you have used before:
    </label>
    <BDropdown
      id="previous-scale-select"
      size="sm"
      variant="outline-primary rounded-2"
      class="d-inline-block"
      text="Use one of your previous conversion scales"
    >
      <BDropdownGroup
        v-for="(term, index1) in previousScales.terms"
        :key="index1"
        :header="term.quarter + ' ' + term.year"
      >
        <BDropdownItemButton
          v-for="(scale, index2) in term.conversion_scales"
          :key="index2"
          :value="scale"
          @click.prevent="previousScaleSelected(scale)"
          >{{ scale.section }}</BDropdownItemButton
        >
      </BDropdownGroup>
    </BDropdown>
  </div>

  <GradeConversionCalculator />

  <div class="row justify-content-end">
    <div class="col-6">
      <BAlert
        v-if="scaleErrorCount"
        :model-value="true"
        variant="danger"
        class="small"
        ><i class="bi-exclamation-octagon-fill me-1"></i>Unable to submit
        because there are {{ scaleErrorText }}</BAlert
      >

      <div class="text-end">
        <BButton
          variant="outline-primary me-2"
          title="Cancel"
          @click="cancelConversion"
          >Cancel
        </BButton>
        <BButton
          variant="primary"
          title="Review converted grades"
          @click="reviewConversion"
          >Review converted grades
        </BButton>
      </div>
    </div>
  </div>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import GradeConversionCalculator from "@/components/convert/calculator.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { useCalculatorStore } from "@/stores/calculator";
import {
  BAlert,
  BCard,
  BButton,
  BLink,
  BDropdown,
  BDropdownGroup,
  BDropdownItemButton,
} from "bootstrap-vue-next";

export default {
  components: {
    SectionHeader,
    GradeConversionCalculator,
    BAlert,
    BButton,
    BDropdown,
    BDropdownItemButton,
    BDropdownGroup,
  },
  props: {
    section: {
      type: Object,
      required: true,
    },
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
      return interpolate(
        ngettext(
          "One invalid grade",
          "%(count)s invalid grades",
          this.scaleErrorCount
        ),
        { count: this.scaleErrorCount },
        true
      );
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
    reviewConversion: function () {
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
