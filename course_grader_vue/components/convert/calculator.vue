<template>
  <!--<div class="mb-3">
    <label for="import-scale-selector" class="me-2"
      >Choose your grade scale:</label
    >
    <BDropdown
      id="import-scale-selector"
      size="sm"
      no-caret
      variant="outline-primary rounded-2"
      class="d-inline-block"
      toggle-class="rounded-2"
    >
      <template #button-content>
        {{ gettext("conversion_scale_" + calculatorStore.selectedScale)
        }}<i class="bi bi-chevron-down ms-1"></i>
      </template>
      <BDropdownItem
        v-for="(scale, index) in calculatorStore.availableScales"
        :key="index"
        :value="scale"
        @click.prevent="calculatorStore.setScale(scale)"
        >{{ gettext("conversion_scale_" + scale) }}
      </BDropdownItem>
    </BDropdown>
  </div>-->

  <div class="row">
    <div class="col-9">
      <div v-if="!calculatorStore.isFixedScale">
        <p>
          To use the conversion calculator, enter minimum percentages and
          equivalent class grades in two or more rows in the calculator, and
          click
          <strong>Apply to Grade Scale</strong>. The calculator fills in the
          rest of the grade scale.
        </p>
        <div class="d-flex justify-content-between">
          <h4>Conversion calculator</h4>
          <div class="text-end">
            <BButton
              title="Reset the grade conversion calculator"
              size="sm"
              variant="outline-primary rounded-2"
              @click.prevent="calculatorStore.resetCalculatorValues()"
              >Reset</BButton
            >

            <BButton
              title="Create grade scale"
              size="sm"
              variant="outline-primary rounded-2 ms-2"
              @click="calculatorStore.calculateScale()"
            >
              Apply to Grade Scale
            </BButton>
          </div>
        </div>
        <table class="table">
          <thead class="table-body-secondary">
            <tr>
              <th scope="col" class="w-50">Final Score (percentage)</th>
              <th scope="col"></th>
              <th scope="col" class="w-50">Grade Point</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(data, index) in calculatorValues" :key="index">
              <template v-if="0 < index && index < calculatorValues.length">
                <tr>
                  <td class="text-center small">
                    <BLink
                      title="Add a row to the conversion table. Leave unused rows blank."
                      tabindex="0"
                      class="link-quiet-primary"
                      @click.prevent="calculatorStore.addCalculatorRow(index)"
                      >+ Add a row</BLink
                    >
                  </td>
                  <td>&nbsp;</td>
                  <td class="text-center">
                    <i class="bi bi-three-dots-vertical"></i>
                  </td>
                </tr>
              </template>

              <CalculatorRow
                :row-data="data"
                :first="index === 0"
                :last="index === calculatorValues.length - 1"
                :index="index"
              />
            </template>
          </tbody>
        </table>
      </div>
      <div v-else>
        <p>
          {{ gettext("calculator_min_" + calculatorStore.selectedScale) }}
        </p>
      </div>

      <div
        id="conversion_grade_scale_container"
        class="mb-5"
        aria-labelledby="grade_scale_header"
      >
        <div class="d-flex justify-content-between">
          <h4>
            {{ gettext("conversion_scale_" + calculatorStore.selectedScale) }}
          </h4>
          <div class="text-end">
            <BDropdown
              size="sm"
              text="Choose Grade Scale"
              class="d-inline-block"
              variant="outline-primary"
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

            <BButton
              variant="outline-primary rounded-2 ms-2"
              size="sm"
              @click.prevent="calculatorStore.resetScaleValues()"
              >Clear scale</BButton
            >
          </div>
        </div>

        <table class="table">
          <thead class="table-body-secondary">
            <tr>
              <th scope="col" class="w-50">Minimum score</th>
              <th scope="col"></th>
              <th scope="col" class="w-50">Grade</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(data, index) in scaleValues" :key="index">
              <GradeScaleRow
                :row-data="data"
                :last="index === scaleValues.length - 1"
                :index="index"
              />
            </template>
          </tbody>
        </table>
      </div>
      <!-- END: calculator layout -->
    </div>
  </div>
</template>

<script>
import { useCalculatorStore } from "@/stores/calculator";
import CalculatorRow from "@/components/convert/calculator-row.vue";
import GradeScaleRow from "@/components/convert/grade-scale-row.vue";
import { BLink, BButton } from "bootstrap-vue-next";

export default {
  name: "CalculatorComp",
  components: {
    CalculatorRow,
    GradeScaleRow,
    BButton,
    BLink,
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
