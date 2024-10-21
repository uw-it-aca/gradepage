import { defineStore } from "pinia";
import { getConversionScales } from "@/utils/data";
import { toRaw } from "vue";

const UG_GRADE_SCALE = [
  "4.0", "3.9", "3.8", "3.7", "3.6", "3.5", "3.4", "3.3", "3.2", "3.1",
  "3.0", "2.9", "2.8", "2.7", "2.6", "2.5", "2.4", "2.3", "2.2", "2.1",
  "2.0", "1.9", "1.8", "1.7", "1.6", "1.5", "1.4", "1.3", "1.2", "1.1",
  "1.0", "0.9", "0.8", "0.7", "0.0"]
const GR_GRADE_SCALE = [
  "4.0", "3.9", "3.8", "3.7", "3.6", "3.5", "3.4", "3.3", "3.2", "3.1",
  "3.0", "2.9", "2.8", "2.7", "2.6", "2.5", "2.4", "2.3", "2.2", "2.1",
  "2.0", "1.9", "1.8", "1.7", "0.0"]
const CNC_GRADE_SCALE = ["CR", "NC"]
const PF_GRADE_SCALE = ["P", "F"]
const HPF_GRADE_SCALE = ["H", "HP", "P", "F"]
const VALID_SCALES = ["ug", "gr", "cnc", "pf", "hpf"];
const FIXED_SCALES = ["cnc", "pf", "hpf"]

export const useCalculatorStore = defineStore({
  id: "calculator",
  state: () => {
    return {
      name: "Calculator",
      gradeScales: {
        "ug": UG_GRADE_SCALE,
        "gr": GR_GRADE_SCALE,
        "cnc": CNC_GRADE_SCALE,
        "pf": PF_GRADE_SCALE,
        "hpf": HPF_GRADE_SCALE,
      },
      defaultCalculatorValues: {"ug": ["4.0", "0.7"], "gr": ["4.0", "1.7"]},
      _previousScales: {ug: {}, gr: {}, cnc: {}, pf: {}, hpf: {}},
      selectedScale: "ug",
      calculatorValues: [],
      scaleValues: [],
      gradeImport: null,
    };
  },
  getters: {
    availableScales(state) {
      return VALID_SCALES;
    },
    isFixedScale(state) {
      return FIXED_SCALES.includes(this.selectedScale);
    },
    previousScales(state) {
      let scale = this.selectedScale,
          url = "/api/v1/conversion_scales/" + scale;
      if (!Object.prototype.hasOwnProperty.call(this._previousScales[scale], 'data')) {
        getConversionScales(url)
          .then((response) => {
            return response.data;
          })
          .then((data) => {
            this._previousScales[scale].data = data;
          });
      }
      return this._previousScales[scale].data;
    },
  },
  actions: {
    validScale(scale) {
      return VALID_SCALES.includes(scale) ? true : false;
    },
    setScale(scale) {
      if (this.validScale(scale)) {
        this.selectedScale = scale;
        this.resetCalculatorValues();
        this.resetScaleValues();
      }
    },
    setGradeImport(gradeImport) {
      this.gradeImport = gradeImport;
    },

    // Calculator actions
    addCalculatorRow() {
      this.calculatorValues.splice(-1, 0, {
        grade: "", percentage: "", gradeError: "", percentageError: ""});
    },
    updateCalculatorPercentage(index, value) {
      this.calculatorValues[index].percentage = value;
    },
    updateCalculatorGrade(index, value) {
      this.calculatorValues[index].grade = value;
    },
    resetCalculatorValues() {
      let scale = this.selectedScale;
      if (Object.prototype.hasOwnProperty.call(this.defaultCalculatorValues, scale)) {
        this.calculatorValues = this.defaultCalculatorValues[scale].map(
          g => ({grade: g, percentage: "", gradeError: "", percentageError: ""}));
      }
    },
    validateCalculatorValues() {
      var valid = true,
          currScale = this.gradeScales[this.selectedScale],
          highestValidGrade = parseFloat(currScale[0]),
          lowestValidGrade = parseFloat(currScale[currScale.length - 2]),
          lastSeenPercentage,
          lastSeenGrade,
          emptyRows = [];

      this.calculatorValues.forEach((cv, idx) => {
        cv.grade = cv.grade.trim();
        cv.percentage = cv.percentage.trim();

        if (cv.percentage === "" && cv.grade === "") {
          emptyRows.unshift(idx);
          return;
        }

        if (cv.percentage === "") {
          valid = false;
          cv.percentageError = gettext("calculator_min_missing");
        } else if (cv.percentage.match(/^[^-]+[-]/)) {
          valid = false;
          cv.percentageError = gettext("calculator_min_invalid");
        } else {
          var pct = Math.round(parseFloat(cv.percentage) * 10) / 10;
          if (isNaN(pct) || pct >= lastSeenPercentage) {
            valid = false;
            cv.percentageError = gettext("calculator_min_invalid");
          } else {
            lastSeenPercentage = pct;
            cv.percentageError = "";
          }
        }

        if (cv.grade === "") {
          valid = false;
          cv.gradeError = gettext("calculator_grade_missing");
        } else {
          var grd = Math.round(parseFloat(cv.grade) * 10) / 10;
          if (isNaN(grd) ||
              grd > highestValidGrade ||
              grd < lowestValidGrade ||
              grd >= lastSeenGrade) {
            valid = false;
            cv.gradeError = gettext("calculator_grade_invalid");
          } else {
            lastSeenGrade = grd;
            cv.gradeError = "";

            var strgrd = grd.toString();
            if (!strgrd.match(/\./)) {
              cv.grade = strgrd += ".0";
            }
            if (strgrd.match(/^\./)) {
              cv.grade = "0" + strgrd;
            }
          }
        }
      });

      emptyRows.forEach((i) => {
        this.calculatorValues.splice(i, 1);  // Silently remove empty rows
      });
      return valid;
    },

    // Grade scale actions
    updateScalePercentage(index, minPercentage) {
      this.scaleValues[index].minPercentage = minPercentage;
    },
    resetScaleValues() {
      let scale = this.selectedScale;
      this.scaleValues = this.gradeScales[scale].map(
        g => ({grade: g, minPercentage: "", minPercentageError: ""}));
    },
    calculateScale() {
      var currCalcGrade,
          currCalcPos = 0,
          matchedPos = null;

      if (!this.validateCalculatorValues()) {
        return;
      }

      //const reverseCalc = this.calculatorValues.slice().reverse();

      currCalcGrade = this.calculatorValues[currCalcPos].grade;
      this.scaleValues.forEach((sv, idx) => {
        var currPercentage,
            prevPercentage,
            stepValue,
            stepPercentage,
            i;

        if (sv.grade === currCalcGrade) {
          if (matchedPos !== null) {
            currPercentage = parseFloat(
              this.calculatorValues[currCalcPos].percentage, 10);
            prevPercentage = parseFloat(
              this.calculatorValues[currCalcPos - 1].percentage, 10);
            stepValue = (currPercentage - prevPercentage) / (idx - matchedPos);

            for (i = matchedPos; i <= idx; i++) {
              stepPercentage = prevPercentage + (stepValue * (i - matchedPos));
              stepPercentage = Math.round(stepPercentage * 10) / 10;
              this.scaleValues[i].minPercentage = stepPercentage.toString();
            }
          }
          matchedPos = idx;
          currCalcPos++;
          if (this.calculatorValues[currCalcPos]) {
            currCalcGrade = this.calculatorValues[currCalcPos].grade;
          }
        }
      });
    },
    validateScaleValues() {
      var errorCount = 0,
          seenMins = {};

      this.scaleValues.forEach((sv, idx, arr) => {
        if (idx === arr.length - 1) {
          return;
        }

        sv.minPercentage = sv.minPercentage.trim();
        if (sv.minPercentage === "") {
          errorCount++;
          sv.minPercentageError = gettext("calculator_min_missing");
        } else {
          var pct = Math.round(parseFloat(sv.minPercentage) * 10) / 10;
          if (isNaN(pct)) {
            errorCount++;
            sv.minPercentageError = gettext("calculator_min_invalid");
          } else {
            if (pct in seenMins) {
              let dupeError = gettext("min_percentage_duplicate");
              errorCount++;
              sv.minPercentage = pct.toString();
              sv.minPercentageError = dupeError;
              this.scaleValues[seenMins[pct]].minPercentageError = dupeError;
            } else {
              sv.minPercentageError = "";
            }
            seenMins[pct] = idx;
          }
        }
      });
      return errorCount;
    },
  },
});
