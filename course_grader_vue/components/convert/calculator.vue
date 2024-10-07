<template>

  <div>
    <label for="import_scale_selector" class="visually-hidden">
      {{ gettext("conversion_scale_chooser_label") }}
    </label>
    <select v-model="selectedScale" id="import_scale_selector">
      <option v-for="scale in availableScales" :value="scale">
        {{ gettext("conversion_scale_" + scale) }}
      </option>
    </select>
  </div>

  <div v-if="!fixedScale">
    <div class="clearfix">
       <h4 class="visually-hidden" id="grade_conversion_header">{{ gettext("calculator_header") }}</h4>
       <span class="visually-hidden">{{ gettext("calculator_instructions") }}</span>
       <strong class="pull-left" aria-hidden="true">{{ gettext("calculator_perc_label_vis") }}</strong>
       <strong class="pull-right" aria-hidden="true">{{ gettext("calculator_grade_label") }}</strong>
    </div>
    <ol>
      <li v-for="(grade, index) in calculatorValues">
        <div v-if="index === calculatorValues.length - 1">
          <BLink
            @click.prevent="addCalculatorRow"
            :title="gettext('calculator_addrow_title')"
            tabindex="0"
          >
            {{ gettext("calculator_addrow") }}
          </BLink>
          <span class="pull-right" style="margin-right:3em;">
            <i class="fa fa-ellipsis-v fa-lg"></i>
          </span>
        </div>
        <CalculatorRow
          percentage=""
          :grade="grade"
          :first="index === 0"
          :last="index === calculatorValues.length - 1"
          :index="index"
        />
      </li>
    </ol>
    <div class="clearfix">
      <span>
        <BButton
          :title="gettext('calculator_reset_title')"
          @click="resetCalculator"
        >{{ gettext("reset") }}</BButton>
      </span>
      <span>
        <BButton
          :title="gettext('calculator_apply_title')"
          @click="applyConversion()"
        >
          <i class="fa fa-angle-double-down fa-lg"></i> {{ gettext("apply") }}
        </BButton>
      </span>
    </div>
  </div>

  <div v-if="fixedScale">
    <span>{{ gettext("calculator_min_" + selectedScale) }}</span>
  </div>
  <div id="conversion_grade_scale_container" aria-labelledby="grade_scale_header">
    <h4 class="visually-hidden" id="grade_scale_header">{{ gettext("grade_scale_header") }}</h4>
    <div class="clearfix">
      <strong class="pull-left" aria-hidden="true">{{ gettext("grade_scale_grade_label_vis") }}</strong>
      <strong class="pull-right" aria-hidden="true">{{ gettext("calculator_grade_label") }}</strong>
    </div>
    <ol :aria-label="gettext('grade_scale_list_label_sr')">
      <li v-for="(grade, index) in scales[selectedScale]">
        <GradeScaleRow
          min-percentage=""
          :grade="grade"
          :last="index === scales[selectedScale].length - 1"
          :index="index"
        />
      </li>
    </ol>
    <span>
      <BButton
        @click="resetGradeScale"
      >{{ gettext("grade_scale_clear") }}</BButton>
    </span>
  </div>
</template>

<script>
import CalculatorRow from "@/components/convert/calculator-row.vue";
import GradeScaleRow from "@/components/convert/grade-scale-row.vue";
import { BButton } from "bootstrap-vue-next";

export default {
  components: {
    CalculatorRow,
    GradeScaleRow,
    BButton,
  },
  props: {
    defaultScale: {
      type: String,
      required: true,
    },
    defaultScaleValues: {
      type: Array,
      default: [],
    },
    defaultCalculatorValues: {
      type: Array,
      default: [],
    },
  },
  data() {
    return {
      availableScales: ["ug", "gr", "cnc", "pf", "hpf"],
      scales: {
        "ug": [],
        "gr": [],
        "cnc": ["CR", "NC"],
        "pf": ["P", "F"],
        "hpf": ["H", "HP", "P", "F"],
      },
      defaultScales: {
        "ug": ["4.0", "0.7"],
        "gr": ["4.0", "1.7"],
      },
      selectedScale: this.defaultScale,
      calculatorValues: [],
      scaleValues: [],
    };
  },
  computed: {
    fixedScale() {
      return (this.selectedScale === "cnc" ||
              this.selectedScale === "hpf" ||
              this.selectedScale === "pf") ? true : false;
    },
  },
  methods: {
    changeGradingScale: function () {
      this.scaleValues = this.scales[this.selectedScale];
    },
    addCalculatorRow: function () {
      this.calculatorValues.splice(-1, 0, "");
    },
    resetCalculator: function () {
    },
    resetGradeScale: function () {
    },
    applyConversion: function () {
    },
    initScales: function () {
      var i, value;

      this.scales.ug = [];
      this.scales.gr = [];

      for (i = 40; i >= 7; i--) {
        value = i / 10;
        if (value === parseInt(value, 10)) {
          value = value + ".0";
        }
        this.scales.ug.push(value.toString());
        if (value >= 1.7) {
          this.scales.gr.push(value.toString());
        }
      }
      this.scales.ug.push("0.0");
      this.scales.gr.push("0.0");
    },
    initCalculator: function () {
      this.initScales();
      this.scaleValues = this.defaultScaleValues || this.scales[this.selectedScale];
      if (!this.fixedScale) {
        this.calculatorValues = this.defaultCalculatorValues.length
          ? this.defaultCalculatorValues
          : this.defaultScales[this.selectedScale];
      }
    },
  },
  created() {
    this.initCalculator();
  },
};
</script>

