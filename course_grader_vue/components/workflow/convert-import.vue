<template>
  <BCard class="shadow-sm rounded-3" header-class="p-3" header="Default">
    <template #header>

      <SectionHeader :section="section" :title="gettext('convert_grades')" />

    </template>

    <h3>{{ gettext("conversion_header") }}</h3>
    <p>{{ gettext("conversion_instructions") }}</p>

    <label for="course-scale-select" class="visually-hidden">
      {{ gettext("course_scale_label_sr") }}
    </label>
    <select id="course-scale-select">
      <option role="presentation" value="0" selected disabled>
        {{ gettext("course_scale_label") }} &gt;
      </option>
      <option v-for="scheme in courseGradingSchemes"
        :value="scheme.grading_scheme_id">
        {{ course_name }}&nbsp;({{ scheme.grading_scheme_name }})
      </option>
    </select>

    <label for="previous-scale-select" class="visually-hidden">
      {{ gettext("previous_scale_label_sr") }}
    </label>
    <select id="previous-scale-select">
      <option role="presentation" value="0" selected disabled>
        {{ gettext("previous_scale_label") }} &gt;
      </option>
      <!-- <option v-for=""></option> -->
    </select>

    Using scale {{ appState.defaultScale }}

    <GradeConversionCalculator
      :scale="appState.defaultScale"
      :scale-values="scaleValues"
      :calculator-values="calculatorValues"
    />

    <template #footer>
      <BLink :title="gettext('cancel')" @click="editGrades">
        {{ gettext("cancel") }}
      </BLink>
      <BButton variant="primary" @click="reviewConversion">
        {{ gettext("conversion_submit") }}
      </BButton>
    </template>
  </BCard>
</template>

<script>
import { getConversionScales } from "@/utils/data";
import SectionHeader from "@/components/section/header.vue";
import GradeConversionCalculator from "@/components/convert/calculator.vue";
import Student from "@/components/student.vue";
import { useWorkflowStateStore } from "@/stores/state";
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
    return {
      appState,
      getConversionScales,
    };
  },
  data() {
    return {
      conversionScales: {},
      courseGradingSchemes: [],
      scaleValues: [],
      calculatorValues: [],
      errorResponse: null,
    };
  },
  methods: {
    editGrades: function () {
      this.appState.editGrades();
    },
    reviewConversion: function() {
    },
    loadPriorScales: function() {
      this.getConversionScales("/api/v1/conversion_scales/" + this.scale)
        .then((response) => {
          return response.data;
        })
        .then((data) => {
          this.conversionScales = data;
        })
        .catch((error) => {
          this.errorResponse = error.response;
        });
    },
  },
};
</script>
