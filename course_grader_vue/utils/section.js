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

function formatGradingStatus(data, richtext=false) {
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
      data.long_submitted_date = formatLongDateTime(data.submitted_date);
      if (data.accepted_date) {
        if (richtext) {
          base = ngettext(
            "<strong>One grade submitted</strong> by <strong>%(submitted_by)s</strong> on %(long_submitted_date)s.",
            "<strong>%(submitted_count)s grades submitted</strong> by <strong>%(submitted_by)s</strong> on %(long_submitted_date)s.",
            data.submitted_count
          );
        } else {
          base = ngettext(
            "%(submitted_count)s grade submitted on %(long_submitted_date)s",
            "%(submitted_count)s grades submitted on %(long_submitted_date)s",
            data.submitted_count);
        }
      } else {
        if (data.status_code !== "200") {
          base = gettext(
            "There was an error submitting grades on %(long_submitted_date)s"
          );
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
    return gettext("No grades were submitted for this section");
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
