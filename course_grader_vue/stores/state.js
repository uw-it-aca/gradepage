import { defineStore } from "pinia";

// Workflow states
const EDIT_GRADES = 1;
const REVIEW_GRADES = 2;
const CONFIRM_GRADES = 3;
const CONVERT_IMPORT = 4;
const REVIEW_CONVERSION = 5;

export const useWorkflowStateStore = defineStore({
  id: "workflow-state",
  state: () => {
    return {
      name: "workflowState",
      _workflowState: null,
      graderoster: null,
      unsubmitted: 0,
    };
  },
  getters: {
    editingGrades (state) {
      return this._workflowState === EDIT_GRADES;
    },
    reviewingGrades (state) {
      return this._workflowState === REVIEW_GRADES;
    },
    confirmingGrades (state) {
      return this._workflowState === CONFIRM_GRADES;
    },
    convertingImport (state) {
      return this._workflowState === CONVERT_IMPORT;
    },
    reviewingConversion (state) {
      return this._workflowState === REVIEW_CONVERSION;
    },
  },
  actions: {
    editGrades () {
      this._workflowState = EDIT_GRADES;
    },
    reviewGrades () {
      this._workflowState = REVIEW_GRADES;
    },
    confirmGrades () {
      this._workflowState = CONFIRM_GRADES;
    },
    convertImport () {
      this._workflowState = CONVERT_IMPORT;
    },
    reviewConversion () {
      this._workflowState = REVIEW_CONVERSION;
    },
    setGraderoster (graderoster) {
      this.graderoster = graderoster;
      this.unsubmitted = graderoster.students.filter(
          (s) => s.grade_url !== null).length

      // Initialize workflow state
      if (this.unsubmitted > 0) {
        this.editGrades();
      } else {
        this.confirmGrades();
      }
    },
  },
});
