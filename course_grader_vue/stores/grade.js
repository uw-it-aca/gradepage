import { defineStore } from "pinia";
import { validateGrade } from "@/utils/grade";

export const useGradeStore = defineStore("grade", {
  state: () => {
    return {
      name: "Grade",
      gradeStatus: {
        missing: new Set(),
        invalid: new Set(),
        saved: new Set()
      },
      gradeData: {},
      gradeChoices: {},
    };
  },
  getters: {
    missing(state) {
      return this.gradeStatus.missing.size;
    },
    invalid(state) {
      return this.gradeStatus.invalid.size;
    },
    saved(state) {
      return this.gradeStatus.saved.size;
    },
    grades(state) {
      var key,
        arr = [];
      for (key in this.gradeData) {
        if (this.gradeData.hasOwnProperty(key)) {
          arr.push(this.gradeData[key]);
        }
      }
      return arr;
    },
  },
  actions: {
    addSaved(studentId) {
      this.gradeStatus.saved.add(studentId);
    },
    validate(studentId, grade, incomplete, writing, choices) {
      let error = validateGrade(grade, incomplete, choices);

      this.gradeStatus.missing.delete(studentId);
      this.gradeStatus.invalid.delete(studentId);

      if (grade === "") {
        this.gradeStatus.missing.add(studentId);
      } else if (error !== "") {
        this.gradeStatus.invalid.add(studentId);
      }

      this.gradeData[studentId] = {
        student_id: studentId,
        grade: grade,
        is_incomplete: incomplete,
        is_writing: writing,
        no_grade_now: grade === gettext("x_no_grade_now"),
      };
      this.gradeChoices[studentId] = choices;

      return error;
    },
    processImport(data) {
      var grade_count = 0,
        valid_grade_count = 0,
        valid_percentage_count = 0,
        override_grade_count = 0,
        unposted_grade_count = 0,
        unposted_with_override_grade_count = 0,
        min_valid = 0.5,
        error;

      for (const student of data.students) {
        if (
          !student.is_auditor &&
          student.date_withdrawn === null &&
          student.imported_grade !== null &&
          student.imported_grade !== ""
        ) {
          grade_count += 1;

          error = validateGrade(
            student.imported_grade,
            student.is_incomplete,
            this.gradeChoices[student.student_id]
          );

          if (error === "") {
            valid_grade_count += 1;
          } else if (!isNaN(student.imported_grade)) {
            valid_percentage_count += 1;
          }

          if (student.is_override_grade) {
            override_grade_count += 1;
          }

          if (student.has_unposted_grade) {
            unposted_grade_count += 1;
            if (student.is_override_grade) {
              unposted_with_override_grade_count += 1;
            }
          }
        }
      }

      data.grade_count = grade_count;
      data.has_valid_grades = false;
      data.has_valid_percentages = false;
      data.override_grade_count = override_grade_count;
      data.unposted_grade_count = unposted_grade_count;
      data.unposted_with_override_grade_count =
        unposted_with_override_grade_count;

      if (grade_count > 0) {
        if (valid_grade_count / grade_count >= min_valid) {
          data.has_valid_grades = true;
        } else if (valid_percentage_count / grade_count >= min_valid) {
          data.has_valid_percentages = true;
        }
      }
      return data;
    },
  },
});
