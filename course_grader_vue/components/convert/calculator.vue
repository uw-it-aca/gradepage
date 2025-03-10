<template>
  <div>
    <label for="import-scale-selector" class="visually-hidden">
      Choose your grade scale:
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
        v-for="(scale, index) in calculatorStore.availableScales"
        :key="index"
        :value="scale"
        @click.prevent="calculatorStore.setScale(scale)"
        >{{ gettext("conversion_scale_" + scale) }}
      </BDropdownItem>
    </BDropdown>
  </div>

  <div class="col-7 bg-body-tertiary p-3">
    <div v-if="!calculatorStore.isFixedScale">
      <h4 id="grade_conversion_header">Grade conversion calculator</h4>
      <p>
        Set at least two Percentage to Grade Point conversion points and click
        <strong>Apply</strong> to create the full Grade Scale below.
      </p>

      <div class="d-flex justify-content-between">
        <div class="fw-bold">Final Score</div>
        <div class="fw-bold">Grade Point</div>
      </div>

      <ol class="list-unstyled">
        <li v-for="(data, index) in calculatorValues" :key="index">
          <template v-if="0 < index && index < calculatorValues.length">
            <div class="d-flex my-3">
              <div class="w-50 text-center">
                <BLink
                  title="Add a row to the conversion table. Leave unused rows blank."
                  tabindex="0"
                  @click.prevent="calculatorStore.addCalculatorRow(index)"
                  >+ Add a row</BLink
                >
              </div>
              <div class="w-50 text-center">
                <i class="bi bi-three-dots-vertical"></i>
              </div>
            </div>
          </template>

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
            title="Reset the grade conversion calculator"
            @click.prevent="calculatorStore.resetCalculatorValues()"
            >Reset</BLink
          >
        </span>
        <span>
          <BButton
            title="Create grade scale"
            @click="calculatorStore.calculateScale()"
          >
            <i class="fa fa-angle-double-down fa-lg"></i> Apply
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
      <h4 id="grade_scale_header" class="visually-hidden">Grade Scale:</h4>

      <div class="d-flex justify-content-between">
        <div class="fw-bold">Minimum score for class grade</div>
        <div class="fw-bold">Grade Point</div>
      </div>

      <ol aria-label="Review and adjust Grade Scale:" class="list-unstyled">
        <li v-for="(data, index) in scaleValues" :key="index">
          <GradeScaleRow
            :row-data="data"
            :last="index === scaleValues.length - 1"
            :index="index"
          />
        </li>
      </ol>
      <span>
        <BButton @click.prevent="calculatorStore.resetScaleValues()"
          >Clear scale</BButton
        >
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
  name: "CalculatorComp",
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
