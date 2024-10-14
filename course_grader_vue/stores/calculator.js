import { defineStore } from "pinia";
import { getConversionScales } from "@/utils/data";

const UG_GRADE_SCALE = [
  "4.0", "3.9", "3.8", "3.7", "3.6", "3.5", "3.4", "3.3", "3.2", "3.1",
  "3.0", "2.9", "2.8", "2.7", "2.6", "2.5", "2.4", "2.3", "2.2", "2.1",
  "2.0", "1.9", "1.8", "1.7", "1.6", "1.5", "1.4", "1.3", "1.2", "1.1",
  "1.0", "0.9", "0.8", "0.7"]
const GR_GRADE_SCALE = [
  "4.0", "3.9", "3.8", "3.7", "3.6", "3.5", "3.4", "3.3", "3.2", "3.1",
  "3.0", "2.9", "2.8", "2.7", "2.6", "2.5", "2.4", "2.3", "2.2", "2.1",
  "2.0", "1.9", "1.8", "1.7"]
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
      _gradeScales: {
        "ug": UG_GRADE_SCALE,
        "gr": GR_GRADE_SCALE,
        "cnc": CNC_GRADE_SCALE,
        "pf": PF_GRADE_SCALE,
        "hpf": HPF_GRADE_SCALE,
      },
      _defaultCalculatorValues: {"ug": ["4.0", "0.7"], "gr": ["4.0", "1.7"]},
      _previousScales: {ug: {}, gr: {}, cnc: {}, pf: {}, hpf: {}},
      _selectedScale: "ug",
      _activeCalculatorValues: [],
      _activeScaleValues: [],
      _gradeImport: null,
    };
  },
  getters: {
    selectedScale(state) {
      return this._selectedScale;
    },
    availableScales(state) {
      return VALID_SCALES;
    },
    isFixedScale(state) {
      return FIXED_SCALES.includes(this._selectedScale);
    },
    previousScales(state) {
      let scale = this._selectedScale,
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
    calculatorValues(state) {
      if (!this._activeCalculatorValues.length) {
        this.resetCalculatorValues();
      }
      return this._activeCalculatorValues;
    },
    scaleValues(state) {
      if (!this._activeScaleValues.length) {
        this.resetScaleValues();
      }
      return this._activeScaleValues;
    },
    gradeImport(state) {
      return this._gradeImport;
    }
  },
  actions: {
    validScale(scale) {
      return VALID_SCALES.includes(scale) ? true : false;
    },
    setScale(scale) {
      if (this.validScale(scale) && scale !== this._selectedScale) {
        this._selectedScale = scale;
        this.resetCalculatorValues();
        this.resetScaleValues();
      }
    },
    setGradeImport(gradeImport) {
      this._gradeImport = gradeImport;
    },
    addCalculatorRow() {
      this._activeCalculatorValues.splice(-1, 0, "");
    },
    resetCalculatorValues() {
      let scale = this._selectedScale;
      if (Object.prototype.hasOwnProperty.call(this._defaultCalculatorValues, scale)) {
        this._activeCalculatorValues = this._defaultCalculatorValues[scale].map(
          g => ({grade: g, percentage: ""}));
      }
    },
    updateScaleValue(grade, minPercentage) {
      let idx = this._activeScaleValues.findIndex(obj => obj.grade === grade);
      this._activeScaleValues[idx].minPercentage = minPercentage;
    },
    resetScaleValues() {
      let scale = this._selectedScale;
      this._activeScaleValues = this._gradeScales[scale].map(
        g => ({grade: g, minPercentage: ""}));
    },
  },
});
