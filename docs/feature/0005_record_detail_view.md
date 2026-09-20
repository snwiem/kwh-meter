# Feature 0005 — Record Detail View

## Status

Deferred — out of scope for MVP.

## Summary

When a user clicks on a reading entry in the main screen list, a modal overlay opens showing the full details of that record in read-only mode.

## Trigger

- Clicking anywhere on a row in the readings list on the main screen opens the overlay.
- The comment icon (visible when a comment exists) is also clickable and opens the same overlay.

## Overlay content

The overlay displays all fields of the selected reading:

| Field     | Description                              |
|-----------|------------------------------------------|
| Date/Time | Timestamp in German format `DD.MM.YYYY HH:MM` |
| Value     | The kWh value with unit (kWh)            |
| Comment   | The full comment text (if present)       |

## Behavior

- The overlay is **read-only** — no editing is possible from here.
- The overlay can be dismissed by clicking outside it or a close button.
- No navigation away from the main screen occurs.
