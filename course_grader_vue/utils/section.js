import { formatLongDateTime } from "@/utils/dates";

function formatLinkTitle(data) {
  if (data.unsubmitted_count && data.grading_period_open) {
    return interpolate("Submit grades for %(display_name)s", data, true);
  } else {
    if (data.submitted_count && data.submitted_date) {
      return interpolate(
        "View submitted grades for %(display_name)s",
        data,
        true
      );
    }
  }
}

function formatGradingStatus(data) {
  var base;
  if (data.grading_status) {
    return data.grading_status;
  } else if (data.unsubmitted_count && data.grading_period_open) {
    base = ngettext(
      "%(unsubmitted_count)s grade to submit",
      "%(unsubmitted_count)s grades to submit",
      data.unsubmitted_count
    );
  } else {
    if (data.submitted_count) {
      if (data.submitted_date) {
        if (data.accepted_date) {
          let submitted_date_str = formatLongDateTime(data.submitted_date);
          base =
            ngettext(
              "%(submitted_count)s grade submitted on ",
              "%(submitted_count)s grades submitted on ",
              data.submitted_count
            ) + submitted_date_str;
        } else if (data.status_code !== "200") {
          return gettext("There was an error submitting grades");
        } else {
          base = ngettext(
            "%(submitted_count)s grade submission in progress",
            "%(submitted_count)s grade submissions in progress",
            data.submitted_count
          );
        }
      } else {
        base = ngettext(
          "%(submitted_count)s grade submitted",
          "%(submitted_count)s grades submitted",
          data.submitted_count
        );
      }
    } else {
      if (!data.grading_period_open) {
        return gettext("No submission information");
      }
    }
  }

  if (base !== undefined) {
    return interpolate(base, data, true);
  }
  return "";
}

function formatErrorStatus(error) {
  return error.error ? error.error : gettext("Error retrieving grading status");
}

function alignTop() {
  console.log("alignTop called...");

  const reference = document.getElementById("referenceDiv");
  const target = document.getElementById("targetDiv");

  if (!reference) {
    console.warn("Reference div not found");
    return;
  } else if (!target) {
    console.warn("Target div not found");
    return;
  }

  //const referenceTop = reference.getBoundingClientRect().top + window.scrollY;
  //target.style.position = "absolute"; // or 'relative' depending on layout
  //target.style.top = `${referenceTop}px`;

  const referenceTop = reference.getBoundingClientRect().top + window.scrollY;
  const targetTop = target.getBoundingClientRect().top + window.scrollY;
  const offset = referenceTop - targetTop; // Apply margin offset to align target with reference

  //console.log("targetTop.." + targetTop);
  //console.log("referenceTop.." + referenceTop);
  //console.log("offset.." + offset);
  target.style.marginTop = `${offset}px`;
}

export { formatLinkTitle, formatGradingStatus, formatErrorStatus, alignTop };
