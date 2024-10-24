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
      <select
        id="course-scale-select"
        v-model="courseGradingScheme"
        @change="courseGradingSchemeSelected()"
      >
        <option role="presentation" value="" selected disabled>
          {{ gettext("course_scale_label") }} &gt;
        </option>
        <option v-for="scheme in courseGradingSchemes" :value="scheme">
          {{ scheme.course_name }}&nbsp;({{ scheme.grading_scheme_name }})
        </option>
      </select>
    </div>

    <div v-if="previousScales && previousScales.terms.length">
      <label for="previous-scale-select" class="visually-hidden">
        {{ gettext("previous_scale_label_sr") }}
      </label>
      <select
        id="previous-scale-select"
        v-model="previousScale"
        @change="previousScaleSelected()"
      >
        <option role="presentation" value="" selected disabled>
          {{ gettext("previous_scale_label") }} &gt;
        </option>
        <optgroup
          v-for="term in previousScales.terms"
          :label="term.quarter + ' ' + term.year">
          <option v-for="scale in term.conversion_scales" :value="scale">
            {{ scale.section }}
          </option>
        </optgroup>
      </select>
    </div>

    <GradeConversionCalculator />

    <template #footer>
      <BLink
        :title="gettext('cancel_title')"
        @click="cancelConversion"
      >{{ gettext("cancel") }}
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
import { BButton, BCard, BLink } from "bootstrap-vue-next";

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
    BButton,
    BCard,
    BLink,
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
      courseGradingScheme: null,
      previousScale: null,
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
    courseGradingSchemeSelected: function () {
      if (this.courseGradingScheme) {
        this.calculatorStore.initializeCalculator(this.courseGradingScheme);
      }
      this.courseGradingScheme = null;
    },
    previousScaleSelected: function () {
      if (this.previousScale) {
        this.calculatorStore.initializeCalculator(this.previousScale);
      }
      this.previousScale = null;
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
