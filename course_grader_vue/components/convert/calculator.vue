<template>

  <div>
    <label for="import_scale_selector" class="visually-hidden">
      {{ gettext("conversion_scale_chooser_label") }}
    </label>
    <select id="import_scale_selector" @change="changeGradingScale()">
      <option value="ug">{{ gettext("conversion_scale_ug") }}</option>
      <option value="gr">{{ gettext("conversion_scale_gr") }}</option>
      <option value="cnc">{{ gettext("conversion_scale_cnc") }}</option>
      <option value="pf">{{ gettext("conversion_scale_pf") }}</option>
      <option value="hpf">{{ gettext("conversion_scale_hpf") }}</option>
    </select>
  </div>

  <div>
    <div class="clearfix">
       <h4 class="sr-only" id="grade_conversion_header">{{ gettext("calculator_header") }}</h4>
       <span class="sr-only">{{ gettext("calculator_instructions") }}</span>
       <div class="pull-left" aria-hidden="true">{{ gettext("calculator_perc_label_vis") }}</div>
        <div class="pull-right" aria-hidden="true">{{ gettext("calculator_grade_label") }}</div>
    </div>
    <div v-if="isFixedScale">
      {{ gettext("calculator_min_" + scale) }}
    </div>
    <ol>
      <li v-for="(grade, index) in calculatorValues">
        <div v-if="!isFixedScale && index === calculatorValues.length - 1">
          <BLink
            @click="addCalculatorRow()"
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
          @click="clearCalculator"
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

  <div id="conversion_grade_scale_container" aria-labelledby="grade_scale_header">
    <h4 class="sr-only" id="grade_scale_header">{{ gettext("grade_scale_header") }}</h4>
    <div class="clearfix">
      <div class="pull-left" aria-hidden="true">{{ gettext("grade_scale_grade_label_vis") }}</div>
      <div class="pull-right" aria-hidden="true">{{ gettext("calculator_grade_label") }}</div>
    </div>
    <ol :aria-label="gettext('grade_scale_list_label_sr')">
      <li v-for="(data, index) in scaleValues">
        <GradeScaleRow
          min-percentage=""
          grade=""
          :last="index === scaleValues.length - 1"
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

  <div class="clearfix" style="max-width:480px;margin:10px 0;">
    <div class="clearfix">
      <BButton
        class="pull-left btn btn-link"
        :title="gettext('cancel_title')"
        @click="cancelConversion"
      >{{ gettext("cancel") }}
      </BButton>
      <BButton
        class="pull-right btn gp-btn"
        :title="gettext('conversion_submit_title')"
        @click="reviewConversion"
      >
        {{ gettext("conversion_submit") }} <i class="fa fa-angle-double-right fa-lg"></i>
      </BButton>
    </div>
    <div id="grade_conversion_invalid_err" role="alert">
        <span class="pull-right gp-conversion-err"></span>
    </div>
  </div>

</template>

<script>
import CalculatorRow from "@/components/convert/calculator-row.vue";
import GradeScaleRow from "@/components/convert/grade-scale-row.vue";
import { BButton } from "bootstrap-vue-next";

export default {
  components: {
    CalculatorRow,
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
      scale: this.defaultScale,
      scaleValues: this.defaultScaleValues,
      calculatorValues: this.defaultCalculatorValues,
      scales: {
        "cnc": ["CR", "NC"],
        "hpf": ["H", "HP", "P", "F"],
        "pf": ["P", "F"],
        "ug": [],
        "gr": [],
      },
      defaultScales: {
        "ug": ["4.0", "0.7"],
        "gr": ["4.0", "1.7"],
      },
    };
  },
  computed: {
    isFixedScale() {
      return (this.scale === "cnc" || this.scale === "hpf" || this.scale === "pf");
    },
  },
  methods: {
    changeGradingScale: function () {
    },
    addCalculatorRow: function () {
    },
    resetCalculator: function () {
    },
    resetGradeScale: function () {
    },
    applyConversion: function () {
    },
    reviewConversion: function () {
    },
    cancelConversion: function () {
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
  },
  created() {
    this.initScales();
  },
};
</script>

