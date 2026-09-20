# Feature 0004 — Export Readings

## Summary

The user can export all readings for the currently configured energy meter as a file download. The export is accessible via a dedicated export page, reachable through a global burger menu.

## Navigation

- A **burger menu** is available globally in the app (e.g. top corner of every screen).
- The menu contains an **"Export"** item that navigates to the export page.
- The export page is separate from the main screen, keeping the UI clean and leaving room for future export options.

## Export Page

- The page contains exactly **two download buttons**:
  - **"Export as TSV"**
  - **"Export as JSON"**
- No filtering by time range or field selection — the export always includes **all records** for the currently configured `zaehler_nr`.
- Clicking a button triggers an immediate **file download** in the browser.

## Export Formats

### TSV (Tab-Separated Values)
- Field separator: **tab character (`\t`)**
- First row is a **header row** with column names.
- Columns: `zaehler_nr`, `timestamp`, `value_kwh`, `comment`
- Timestamp format: `DD.MM.YYYY HH:MM` (German style, consistent with the UI)
- TSV is preferred over CSV to avoid conflicts with the German decimal comma in the value field and to eliminate the need for field quoting logic.

### JSON
- A JSON array of objects, one object per reading.
- Fields per object: `zaehler_nr`, `timestamp`, `value_kwh`, `comment`
- Timestamp format: ISO 8601 (`YYYY-MM-DDTHH:MM:SS`)
- The `comment` field is `null` if no comment was entered.

## Data Integrity — Tab Sanitisation

- When a reading is **saved**, any tab characters in the comment field must be sanitised before persisting:
  - One or more consecutive tab characters (`\t+`) are **silently replaced with a single space**.
  - No warning or notification is shown to the user.
- This ensures TSV export integrity regardless of how the comment was entered.
