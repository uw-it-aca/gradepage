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
      workflowState: null,
      graderoster: null,
      unsubmitted: 0,
      defaultScale: null,
    };
  },
  getters: {
    editingGrades (state) {
      return this.workflowState === EDIT_GRADES;
    },
    reviewingGrades (state) {
      return this.workflowState === REVIEW_GRADES;
    },
    confirmingGrades (state) {
      return this.workflowState === CONFIRM_GRADES;
    },
    convertingImport (state) {
      return this.workflowState === CONVERT_IMPORT;
    },
    reviewingConversion (state) {
      return this.workflowState === REVIEW_CONVERSION;
    },
  },
  actions: {
    editGrades () {
      this.workflowState = EDIT_GRADES;
    },
    reviewGrades () {
      this.workflowState = REVIEW_GRADES;
    },
    confirmGrades () {
      this.workflowState = CONFIRM_GRADES;
    },
    convertImport (scale) {
      this.defaultScale = scale;
      this.workflowState = CONVERT_IMPORT;
    },
    reviewConversion () {
      this.workflowState = REVIEW_CONVERSION;
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
