import { describe, it, expect, beforeAll } from "vitest";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

import { formatLongDateTime, formatShortDate } from "@/utils/dates";
// Adjust path as needed

dayjs.extend(utc);
dayjs.extend(timezone);

const LOCAL_TIMEZONE = "America/Los_Angeles";

describe("date formatting utilities", () => {
  beforeAll(() => {
    // Ensure consistent timezone for tests
    dayjs.tz.setDefault(LOCAL_TIMEZONE);
  });

  describe("formatLongDateTime", () => {
    it("formats a full datetime correctly", () => {
      const date = "2023-05-15T07:30:00Z"; // UTC
      const result = formatLongDateTime(date);
      expect(result).toBe("May 15, 2023 at 7:30 AM");
    });

    it("returns null when no date is provided", () => {
      expect(formatLongDateTime(null)).toBeNull();
    });
  });

  describe("formatShortDate", () => {
    it("formats a short date correctly", () => {
      const date = "2023-05-15T14:30:00Z";
      const result = formatShortDate(date);
      expect(result).toBe("05/15/23");
    });

    it("returns null when no date is provided", () => {
      expect(formatShortDate(null)).toBeNull();
    });
  });
});
