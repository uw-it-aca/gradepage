<template>
  <div>
    <label for="import-scale-selector" class="visually-hidden">
      {{ gettext("conversion_scale_chooser_label") }}
    </label>
    <BDropdown
      id="import-scale-selector"
      size="sm"
      variant="outline-secondary"
      class="d-inline-block"
    >
      <template #button-content>
        {{ gettext("conversion_scale_" + calculatorStore.selectedScale) }}
      </template>
      <BDropdownItem
        v-for="scale in calculatorStore.availableScales"
        :value="scale"
        @click.prevent="calculatorStore.setScale(scale)"
      >{{ gettext("conversion_scale_" + scale) }}
      </BDropdownItem>
    </BDropdown>
  </div>

  <div class="col-7 bg-body-tertiary p-3">
    <div v-if="!calculatorStore.isFixedScale">
      <h4 class="" id="grade_conversion_header">
        {{ gettext("calculator_header") }}
      </h4>
      <p class="">{{ gettext("calculator_instructions") }}</p>

      <div class="d-flex justify-content-between">
        <div class="fw-bold">{{ gettext("calculator_perc_label_vis") }}</div>
        <div class="fw-bold">{{ gettext("calculator_grade_label") }}</div>
      </div>

      <ol class="list-unstyled">
        <li v-for="(data, index) in calculatorValues" :key="index">
          <div v-if="index === calculatorValues.length - 1">
            <BLink
              @click.prevent="calculatorStore.addCalculatorRow()"
              :title="gettext('calculator_addrow_title')"
              tabindex="0"
            >
              {{ gettext("calculator_addrow") }}
            </BLink>
            <span class="pull-right" style="margin-right: 3em">
              <i class="fa fa-ellipsis-v fa-lg"></i>
            </span>
          </div>
          <CalculatorRow
            :row-data="data"
            :first="index === 0"
            :last="index === calculatorValues.length - 1"
            :index="index"
          />
        </li>
      </ol>

      <div class="my-5">
        <span>
          <BLink
            :title="gettext('calculator_reset_title')"
            @click.prevent="calculatorStore.resetCalculatorValues()"
            >{{ gettext("reset") }}
          </BLink>
        </span>
        <span>
          <BButton
            :title="gettext('calculator_apply_title')"
            @click="calculatorStore.calculateScale()"
          >
            <i class="fa fa-angle-double-down fa-lg"></i> {{ gettext("apply") }}
          </BButton>
        </span>
      </div>
    </div>

    <div v-if="calculatorStore.isFixedScale">
      <span>
        {{ gettext("calculator_min_" + calculatorStore.selectedScale) }}
      </span>
    </div>

    <div
      id="conversion_grade_scale_container"
      aria-labelledby="grade_scale_header"
    >
      <h4 class="visually-hidden" id="grade_scale_header">
        {{ gettext("grade_scale_header") }}
      </h4>

      <div class="d-flex justify-content-between">
        <div class="fw-bold">{{ gettext("grade_scale_grade_label_vis") }}</div>
        <div class="fw-bold">{{ gettext("calculator_grade_label") }}</div>
      </div>

      <ol
        :aria-label="gettext('grade_scale_list_label_sr')"
        class="list-unstyled"
      >
        <li v-for="(data, index) in scaleValues" :key="index">
          <GradeScaleRow
            :row-data="data"
            :last="index === scaleValues.length - 1"
            :index="index"
          />
        </li>
      </ol>
      <span>
        <BButton @click.prevent="calculatorStore.resetScaleValues()">{{
          gettext("grade_scale_clear")
        }}</BButton>
      </span>
    </div>
  </div>
</template>

<script>
import { useCalculatorStore } from "@/stores/calculator";
import CalculatorRow from "@/components/convert/calculator-row.vue";
import GradeScaleRow from "@/components/convert/grade-scale-row.vue";
import { BLink, BButton, BDropdown, BDropdownItem } from "bootstrap-vue-next";

export default {
  components: {
    CalculatorRow,
    GradeScaleRow,
    BButton,
    BLink,
    BDropdown,
    BDropdownItem,
  },
  setup() {
    const calculatorStore = useCalculatorStore();
    return {
      calculatorStore,
    };
  },
  data() {
    return {
      calculatorValues: [],
      scaleValues: [],
    };
  },
  created() {
    this.calculatorValues = this.calculatorStore.calculatorValues;
    this.scaleValues = this.calculatorStore.scaleValues;

    this.calculatorStore.$subscribe((mutation, state) => {
      this.calculatorValues = state.calculatorValues;
      this.scaleValues = state.scaleValues;
    });
  },
};
</script>
