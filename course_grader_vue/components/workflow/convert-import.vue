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
        @change="useCourseGaradingScheme($event.target.value)"
      >
        <option role="presentation" value="0" selected disabled>
          {{ gettext("course_scale_label") }} &gt;
        </option>
        <option v-for="scheme in courseGradingSchemes"
          :value="scheme.grading_scheme_id">
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
        @change="usePreviousScale($event.target.value)"
      >
        <option role="presentation" value="0" selected disabled>
          {{ gettext("previous_scale_label") }} &gt;
        </option>
        <optgroup
          v-for="term in previousScales.terms"
          :label="term.quarter + ' ' + term.year">
          <option v-for="scale in term.conversion_scales" :value="scale.id">
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
      >{{ gettext("conversion_submit") }}
      </BButton>
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
  computed: {
    previousScales() {
      return this.calculatorStore.previousScales;
    },
    courseGradingSchemes() {
      return this.calculatorStore.gradeImport.course_grading_schemes;
    },
  },
  methods: {
    useCourseGradingScheme: function () {
    },
    usePreviousScale: function () {
    },
    cancelConversion: function () {
      this.appState.editGrades();
    },
    reviewConversion: function() {
    },
  },
};
</script>
