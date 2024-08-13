function normalizeGrade(grade) {
  grade = grade.trim();
  if (grade.match(/^(?:n|nc|p|h|hw|f|hp|i|cr)$/i)) {
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

function validateGrade(grade, incomplete, choices, incompleteBlocklist) {
  var is_hypenated,
      is_cnc,
      is_hhppf,
      is_undergrad_numeric,
      is_grad_numeric;

  if (grade === "" || choices.includes(grade)) {
    return "";
  }

  if (incomplete && incompleteBlocklist.includes(grade)) {
    return gettext("grade_invalid_incomplete");
  }

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
  }
}

export {
  normalizeGrade,
  validateGrade,
};
