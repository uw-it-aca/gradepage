import { defineStore } from "pinia";
import { getConversionScales } from "@/utils/data";

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
          curr_scale = this.gradeScales[this.selectedScale],
          highest_valid_grade = parseFloat(curr_scale[0]),
          lowest_valid_grade = parseFloat(curr_scale[curr_scale.length - 2]),
          last_seen_percentage,
          last_seen_grade;

      // Remove empty rows
      this.calculatorValues = this.calculatorValues.filter(
        cv => cv.grade != "" && cv.percentage != "")

      this.calculatorValues.forEach((cv, idx) => {
        cv.percentage = cv.percentage.trim();
        if (cv.percentage === "") {
          valid = false;
          cv.percentageError = gettext("calculator_min_missing");
        } else if (cv.percentage.match(/^[^-]+[-]/)) {
          valid = false;
          cv.percentageError = gettext("calculator_min_invalid");
        } else {
          var pct = Math.round(parseFloat(cv.percentage) * 10) / 10;
          if (isNaN(pct) || pct >= last_seen_percentage) {
            valid = false;
            cv.percentageError = gettext("calculator_min_invalid");
          } else {
            last_seen_percentage = pct;
            cv.percentageError = "";
          }
        }

        cv.grade = cv.grade.trim();
        if (cv.grade === "") {
          valid = false;
          cv.gradeError = gettext("calculator_grade_missing");
        } else {
          var grd = Math.round(parseFloat(cv.grade) * 10) / 10;
          if (isNaN(grd) || grd > highest_valid_grade ||
              grd < lowest_valid_grade ||
              grd >= last_seen_grade) {
            valid = false;
            cv.gradeError = gettext("calculator_grade_invalid");
          } else {
            last_seen_grade = grd;
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
      return valid;
    },
    updateScalePercentage(index, minPercentage) {
      this.scaleValues[index].minPercentage = minPercentage;
    },
    resetScaleValues() {
      let scale = this.selectedScale;
      this.scaleValues = this.gradeScales[scale].map(
        g => ({grade: g, minPercentage: "", minPercentageError: ""}));
    },
    calculateScale() {
      if (!this.validateCalculatorValues()) {
        return;
      }

      const sortedGrades = this.calculatorValues.toSorted(function (a, b) {
        return b.percentage - a.percentage;
      });

      this.scaleValues.forEach((sv, idx) => {

      });
    },
  },
});
