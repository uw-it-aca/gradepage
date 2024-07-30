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
  if (data.grading_status) {
    return data.grading_status;
  } else if (data.unsubmitted_count && data.grading_period_open) {
    return (data.unsubmitted_count > 1)
      ? data.unsubmitted_count + " grades to submit"
      : "1 grade to submit";
  } else {
    if (data.submitted_count) {
      if (data.submitted_date) {
        if (data.accepted_date) {
          let submitted_date_str = formatLongDateTime(data.submitted_date);
          return (data.submitted_count > 1)
            ? data.submitted_count + " grades submitted on " + submitted_date_str
            : "1 grade submitted on " + submitted_date_str;
        } else {
          return (data.submitted_count > 1)
            ? data.submitted_count + " grade submissions in progress"
            : "1 grade submission in progress";
        }
      } else {
        return (data.submitted_count > 1)
          ? data.submitted_count + " grades submitted"
          : "1 grade submitted";
      }
    } else {
      if (!data.grading_period_open) {
        return "No submission information";
      }
    }
  }
}

export {
  formatLinkTitle,
  formatGradingStatus,
};
