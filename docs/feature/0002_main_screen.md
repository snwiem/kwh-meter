# Feature 0002 — Main Screen

## Summary

The main screen is the entry point of the application. It shows the currently configured energy meter identity, a pageable list of the latest readings, and a prominent button to add a new reading.

## Layout

### Header row
- Displays the **Zählernummer** of the currently active energy meter, left-aligned.
- A prominent **"+" button** is placed right-aligned in the same row, providing quick access to add a new reading.

### Readings list
- Displays readings belonging to the currently configured `zaehler_nr` only.
- Sorted by timestamp, most recent first.
- **Pageable**: each page shows a maximum of **10 entries**.
- The list must be **scrollable**.

### List entry columns
| Column    | Description                                              |
|-----------|----------------------------------------------------------|
| Date/Time | Timestamp in German format: `DD.MM.YYYY HH:MM`           |
| Value     | The kWh value of the reading                             |
| Comment   | An icon indicator shown only if a comment exists; clicking it (or anywhere on the row) opens the record detail overlay |

## Record detail overlay (read-only)

- Clicking anywhere on a list entry opens a **modal overlay**.
- The overlay displays all fields of the record: date/time, value, and comment.
- The overlay is **read-only** — no editing is possible from here.

## Navigation

- The "+" button navigates to a **separate page** for adding a new reading (see Feature 0003).
- No other navigation is required on the main screen for MVP.
