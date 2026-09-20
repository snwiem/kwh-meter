# Feature 0005 — Record Detail View

## Status

Ready — replacing the previously defined modal overlay approach.

## Summary

When a user taps or clicks on a reading entry in the main screen list, the app navigates to a dedicated detail page (not a modal overlay) showing the full details of that record in read-only mode.

## Trigger

- Tapping or clicking anywhere on a row in the readings list navigates to the detail page.

## Detail Page Content

The page displays all fields of the selected reading:

| Field     | Description                                    |
|-----------|------------------------------------------------|
| Date/Time | Timestamp in German format `DD.MM.YYYY HH:MM`  |
| Value     | The kWh value with unit (kWh)                  |
| Comment   | The full comment text (if present)             |

## Top Bar Actions

The detail page top bar includes two action buttons:

| Action | Icon       | Behavior                                     |
|--------|------------|----------------------------------------------|
| Edit   | Pencil/Edit | Navigate to the edit view for this record    |
| Delete | Trash/Delete | Open delete confirmation modal               |

## Behavior

- The page is **read-only** — no inline editing.
- A back button in the top bar (or browser back gesture) returns to the main screen.
- The URL route contains the record ID, e.g. `/readings/:id`.

## Navigation Flow

```
Main Screen → (tap row) → Detail Page → (tap Edit) → Edit View
                                      → (tap Delete) → Confirmation Modal → (confirm) → Main Screen
                                                                           → (cancel) → back to Detail Page
```

## Notes

- This replaces the previously defined modal overlay approach (see ADR if recorded).
- The edit and delete features are defined separately in feature docs 0006 and 0007.
