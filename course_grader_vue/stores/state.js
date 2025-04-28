import { defineStore } from "pinia";

// Workflow states
const EDIT_GRADES = 1;
const REVIEW_GRADES = 2;
const CONFIRM_GRADES = 3;
const CONVERT_IMPORT = 4;
const REVIEW_CONVERSION = 5;

export const useWorkflowStateStore = defineStore("workflow-state", {
  state: () => {
    return {
      name: "workflowState",
      _workflowState: null,
      graderoster: null,
      gradeImport: null,
    };
  },
  getters: {
    editingGrades(state) {
      return this._workflowState === EDIT_GRADES;
    },
    reviewingGrades(state) {
      return this._workflowState === REVIEW_GRADES;
    },
    confirmingGrades(state) {
      return this._workflowState === CONFIRM_GRADES;
    },
    convertingImport(state) {
      return this._workflowState === CONVERT_IMPORT;
    },
    reviewingConversion(state) {
      return this._workflowState === REVIEW_CONVERSION;
    },
    convertedGradeData(state) {
      return Object.fromEntries(
        this.gradeImport.students.map((s) => [
          s.student_reg_id,
          s.converted_grade,
        ])
      );
    },
  },
  actions: {
    editGrades() {
      this._workflowState = EDIT_GRADES;
    },
    reviewGrades() {
      this._workflowState = REVIEW_GRADES;
    },
    confirmGrades() {
      this._workflowState = CONFIRM_GRADES;
    },
    convertImport() {
      this._workflowState = CONVERT_IMPORT;
    },
    reviewConversion() {
      this._workflowState = REVIEW_CONVERSION;
    },
    setGradeImport(gradeImport) {
      this.gradeImport = gradeImport;
    },
    resetGradeImport() {
      this.gradeImport = null;
    },
    setGraderoster(graderoster) {
      this.graderoster = graderoster;

      // Initialize workflow state
      if (this.graderoster.gradable_student_count > 0) {
        if (this.graderoster.has_successful_submissions) {
          if (this.graderoster.has_saved_grades) {
            this.editGrades();
          } else {
            this.confirmGrades();
          }
        } else {
          this.editGrades();
        }
      } else {
        this.confirmGrades();
      }
    },
    convertImportedGrades(scaleValues, lowestValidGrade) {
      this.gradeImport.students.forEach((student) => {
        let importedPct = parseFloat(student.imported_grade);
        let match = scaleValues.find((sv) => {
          return importedPct >= parseFloat(sv.minPercentage);
        });
        student.converted_grade = match ? match.grade : lowestValidGrade;
      });
    },
  },
});
