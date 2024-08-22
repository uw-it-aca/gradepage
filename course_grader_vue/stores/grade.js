import { defineStore } from "pinia";
import { validateGrade } from "@/utils/grade";

export const useGradeStore = defineStore({
  id: "grade",
  state: () => {
    return {
      name: "Grade",
      gradeStatus: { "missing": new Set(), "invalid": new Set() },
      gradeData: {},
    };
  },
  getters: {
    missing (state) {
      return this.gradeStatus.missing.size;
    },
    invalid (state) {
      return  this.gradeStatus.invalid.size;
    },
    grades (state) {
      var key, arr = [];
      for (key in this.gradeData) {
        if (this.gradeData.hasOwnProperty(key)) {
          arr.push(this.gradeData[key]);
        }
      }
      return arr;
    },
  },
  actions: {
    validate (studentId, grade, incomplete, writing, choices) {
      let error = validateGrade(grade, incomplete, choices);

      this.gradeStatus.missing.delete(studentId);
      this.gradeStatus.invalid.delete(studentId);

      if (grade === "") {
        this.gradeStatus.missing.add(studentId);
      } else if (error !== "") {
        this.gradeStatus.invalid.add(studentId);
      }

      this.gradeData[studentId] = {
        "student_id": studentId,
        "grade": grade,
        "is_incomplete": incomplete,
        "is_writing": writing,
        "no_grade_now": grade === gettext("x_no_grade_now"),
      };

      return error;
    },
  },
});
