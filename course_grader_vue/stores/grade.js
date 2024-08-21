import { defineStore } from "pinia";
import { validateGrade } from "@/utils/grade";

export const useGradeStatusStore = defineStore({
  id: "grade-status",
  state: () => {
    return {
      name: "GradeStatus",
      gradeStatus: {
        "missing": new Set(),
        "invalid": new Set(),
      },
    };
  },
  getters: {
    missing (state) {
      return this.gradeStatus.missing.size;
    },
    invalid (state) {
      return  this.gradeStatus.invalid.size;
    },
  },
  actions: {
    validate (id, grade, incomplete, choices) {
      let error = validateGrade(grade, incomplete, choices);

      this.gradeStatus.missing.delete(id);
      this.gradeStatus.invalid.delete(id);

      if (grade === "") {
        this.gradeStatus.missing.add(id);
      } else if (error !== "") {
        this.gradeStatus.invalid.add(id);
      }
      return error;
    },
  },
});
