import { formatLongDateTime } from "@/utils/dates";

const incompleteBlocklist = [gettext("x_no_grade_now"), "N", "CR"];

function normalizeGrade(grade) {
  try {
    grade = grade.toString().trim();
  } catch (error) {
    grade = "";
  }
  if (grade === "") {
    // pass
  } else if (grade.match(/^(?:n|nc|p|h|hw|f|hp|i|cr)$/i)) {
    grade = grade.toUpperCase();
  } else if (grade.match(/^x/i)) {
    grade = gettext("x_no_grade_now");
  } else {
    grade = grade.replace(/^([0-4])?\.([0-9])0+$/, "$1.$2");
    grade = grade.replace(/^\.([0-9])$/, "0.$1");
    grade = grade.replace(/^([0-4])\.?$/, "$1.0");
  }
  return grade;
}

function normalizeDefaultGrade(grade, choices) {
  if (grade === "" || incompleteBlocklist.includes(grade)) {
    return choices.includes("0.0") ? "0.0" : choices.includes("NC") ? "NC" : "";
  }
  return grade;
}

function validateGrade(grade, incomplete, choices) {
  var is_hypenated, is_cnc, is_hhppf, is_undergrad_numeric, is_grad_numeric;

  if (choices.includes(grade)) {
    return "";
  } else if (grade === "") {
    return "Grade is required.";
  } else if (incomplete && incompleteBlocklist.includes(grade)) {
    return gettext("grade_invalid_incomplete");
  } else {
    is_hypenated = choices.includes("N");
    is_cnc = choices.includes("NC");
    is_hhppf = choices.includes("HP");
    is_undergrad_numeric = choices.includes("0.9");
    is_grad_numeric = choices.includes("1.9") && !is_undergrad_numeric;

    if (is_hypenated && is_cnc && is_undergrad_numeric) {
      // Hyphenated, C/NC, Undergrad 4.0 scale
      if (grade === parseFloat(grade).toString() && grade < 0.7) {
        return gettext("grade_invalid_undergrad_lowest_passing");
      } else {
        return gettext("grade_invalid_hyphenated_CR_NC_undergrad");
      }
    } else if (is_hypenated && is_cnc && is_grad_numeric) {
      // Hyphenated, C/NC, Graduate 4.0 scale
      if (grade === parseFloat(grade).toString() && grade < 1.7) {
        return gettext("grade_invalid_grad_lowest_passing");
      } else {
        return gettext("grade_invalid_hyphenated_CR_NC_grad");
      }
    } else if (is_hypenated && is_undergrad_numeric) {
      // Hyphenated, Undergrad 4.0 scale
      if (grade === parseFloat(grade).toString() && grade < 0.7) {
        return gettext("grade_invalid_undergrad_lowest_passing");
      } else {
        return gettext("grade_invalid_hyphenated_undergrad");
      }
    } else if (is_hypenated && is_grad_numeric) {
      // Hyphenated, Graduate 4.0 scale
      if (grade === parseFloat(grade).toString() && grade < 1.7) {
        return gettext("grade_invalid_grad_lowest_passing");
      } else {
        return gettext("grade_invalid_hyphenated_grad");
      }
    } else if (is_hhppf && is_grad_numeric) {
      // H/HP/P/F, Graduate 4.0 scale
      if (grade === parseFloat(grade).toString() && grade < 1.7) {
        return gettext("grade_invalid_grad_lowest_passing");
      } else {
        return gettext("grade_invalid_H_HP_P_F_grad");
      }
    } else if (is_undergrad_numeric) {
      // Undergrad 4.0 scale
      return gettext("grade_invalid_undergrad_lowest_passing");
    } else if (is_grad_numeric) {
      // Graduate 4.0 scale
      return gettext("grade_invalid_grad_lowest_passing");
    } else if (is_hypenated && is_cnc) {
      // Hyphenated, C/NC
      return gettext("grade_invalid_hyphenated_CR_NC");
    } else if (is_cnc) {
      // C/NC
      return gettext("grade_invalid_CR_NC");
    } else if (is_hypenated && is_hhppf) {
      // Hyphenated, H/HP/P/F
      return gettext("grade_invalid_hyphenated_H_HP_P_F");
    } else if (is_hhppf) {
      // H/HP/P/F
      return gettext("grade_invalid_H_HP_P_F");
    } else {
      return "Enter a valid grade";
    }
  }
}

function priorGradeText(student) {
  var priorGrade;
  if (student.no_grade_now) {
    priorGrade = "X (No grade now)";
  } else if (student.has_incomplete) {
    priorGrade = "Incomplete (Default " + student.grade + ")";
  } else {
    priorGrade = student.grade;
    if (student.has_writing_credit) {
      priorGrade += " (W)";
    }
  }
  return "Submitted " + priorGrade + " on " + student.date_graded;
}

function duplicateCodeText() {
  return gettext("Student dropped this section, and re-added.");
}

function writingSectionText() {
  return gettext("Writing credit automatically given to all students with a passing grade in this course.");
}

export {
  incompleteBlocklist,
  normalizeGrade,
  normalizeDefaultGrade,
  validateGrade,
  priorGradeText,
  duplicateCodeText,
  writingSectionText,
};
