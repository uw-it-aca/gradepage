import { formatLongDateTime } from "@/utils/dates";

function formatLinkTitle(data) {
  if (data.unsubmitted_count && data.grading_period_open) {
    return "Submit grades for " + data.display_name;
  } else {
    if (data.submitted_count && data.submitted_date) {
      return "View grade receipt for " + data.display_name;
    }
  }
}

function formatGradingStatus(data) {
  var base;
  if (data.grading_status) {
    return data.grading_status;
  } else if (data.unsubmitted_count && data.grading_period_open) {
      base = ngettext("%(unsubmitted_count)s grade to submit",
                      "%(unsubmitted_count)s grades to submit",
                      data.unsubmitted_count);
  } else {
    if (data.submitted_count) {
      if (data.submitted_date) {
        if (data.accepted_date) {
          let submitted_date_str = formatLongDateTime(data.submitted_date);
          base = ngettext("%(submitted_count)s grade submitted on ",
                          "%(submitted_count)s grades submitted on ",
                          data.submitted_count) + submitted_date_str;
        } else {
          base = ngettext("%(submitted_count)s grade submission in progress",
                          "%(submitted_count)s grade submissions in progress",
                          data.submitted_count);
        }
      } else {
        base = ngettext("%(submitted_count)s grade submitted",
                        "%(submitted_count)s grades submitted",
                        data.submitted_count);
      }
    } else {
      if (!data.grading_period_open) {
        return gettext("no_submission_information");
      }
    }
  }

  if (base !== undefined) {
    return interpolate(base, data, true);
  }
}

function formatErrorStatus(response) {
  return response.data ? response.data.error : "Error retrieving grading status";
}

export {
  formatLinkTitle,
  formatGradingStatus,
  formatErrorStatus,
};
