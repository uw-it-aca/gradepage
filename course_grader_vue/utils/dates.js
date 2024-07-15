import dayjs from "dayjs";
import localizedFormat from "dayjs/plugin/localizedFormat";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(localizedFormat);
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(relativeTime);

const LOCAL_TIMEZONE = "America/Los_Angeles";

function formatDate(date, format) {
  return date ? dayjs(date).format(format) : null;
}

function formatLongDateTime(date) {
  return formatDate(date, "MMMM D[,] YYYY [at] h:mm A");
}

function formatShortDate(date) {
  return formatDate(date, "MM/DD/YY");
}

export {
  formatLongDateTime,
  formatShortDate,
};
