<template>
  <BCard class="shadow-sm rounded-3" header-class="p-3" header="Default">
    <template #header>
      <SectionHeader :section="section" :title="gettext('convert_grades')" />
    </template>

    <h3>{{ gettext("conversion_header") }}</h3>
    <p>{{ gettext("conversion_instructions") }}</p>

    <div v-if="courseGradingSchemes.length">
      <label for="course-scale-select" class="visually-hidden">
        {{ gettext("course_scale_label_sr") }}
      </label>
      <BDropdown
        id="course-scale-select"
        size="sm"
        variant="outline-secondary"
        class="d-inline-block"
      >
        <template #button-content>
          {{ gettext("course_scale_label") }}
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
        {{ gettext("previous_scale_label_sr") }}
      </label>
      <BDropdown
        id="previous-scale-select"
        size="sm"
        variant="outline-secondary"
        class="d-inline-block"
      >
        <template #button-content>
          {{ gettext("previous_scale_label") }}
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
        :title="gettext('cancel_title')"
        v-text="gettext('cancel')"
        @click="cancelConversion"
      >
      </BLink>
      <BButton
        variant="primary"
        :title="gettext('conversion_submit_title')"
        @click="reviewConversion"
      >{{ gettext("conversion_submit") }} &gt;&gt;
      </BButton>
      <span
        v-if="scaleErrorCount"
        v-html="scaleErrorText"
        role="alert"
        class="text-danger invalid-grade small"
      ></span>
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
        "<strong>One invalid grade</strong> (see above)",
        "<strong>%(count)s invalid grades</strong> (see above)",
        this.scaleErrorCount
      ), {count: this.scaleErrorCount}, true);
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
