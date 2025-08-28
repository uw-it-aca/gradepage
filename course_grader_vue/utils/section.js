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
  }

  if (data.unsubmitted_count) {
    if (data.grading_period_open) {
      base = ngettext(
        "%(unsubmitted_count)s grade to submit",
        "%(unsubmitted_count)s grades to submit",
        data.unsubmitted_count
      );
    } else {
      base = ngettext(
        "%(unsubmitted_count)s grade not submitted",
        "%(unsubmitted_count)s grades not submitted",
        data.unsubmitted_count
      );
    }
  } else if (data.submitted_count) {
    if (data.submitted_date) {
      if (data.accepted_date) {
        base =
          ngettext(
            "%(submitted_count)s grade submitted on ",
            "%(submitted_count)s grades submitted on ",
            data.submitted_count
          ) + formatLongDateTime(data.submitted_date);
      } else {
        if (data.status_code !== "200") {
          return gettext("There was an error submitting grades on ") +
            formatLongDateTime(data.submitted_date);
        } else {
          base = ngettext(
            "%(submitted_count)s grade submission in progress",
            "%(submitted_count)s grade submissions in progress",
            data.submitted_count
          );
        }
      }
    } else {
      base = ngettext(
        "%(submitted_count)s grade submitted",
        "%(submitted_count)s grades submitted",
        data.submitted_count
      );
    }
  } else if (!data.grading_period_open) {
    return gettext("No submission information");
  }

  if (base !== undefined) {
    return interpolate(base, data, true);
  }
  return "";
}

function formatErrorStatus(error) {
  let str = error.error;
  return str
    ? str.charAt(0).toUpperCase() + str.slice(1)
    : gettext("Error retrieving grading status");
}

function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: "smooth", // smooth scrolling
  });
}

export {
  formatLinkTitle,
  formatGradingStatus,
  formatErrorStatus,
  scrollToTop,
};
