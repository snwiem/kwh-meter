# Feature 0006 — Edit Reading

## Summary

A user can edit an existing kWh reading from the detail view. Tapping the Edit action button on the detail page navigates to a dedicated edit view that is pre-filled with the current values of the selected record.

## Trigger

- The Edit button (pencil icon) on the detail page top bar navigates to the edit view.

## Route

`/readings/:id/edit`

## Implementation Approach

- A **separate** `EditReadingView` component is used (the form markup is duplicated from `AddReadingView`, not shared).
- Rationale: keeps the edit form independently evolvable if edit-specific attributes are added later.

## View Layout

- **Header**: page header title **"Ablesung bearbeiten"** only (no "← Zurück" link in the header).
- **Top bar** (global): back button returns to the **detail page** (`/readings/:id`), discarding unsaved changes.
- **Form**: duplicates the Add form — timestamp, value, and comment fields, pre-filled.

| Field     | Pre-filled with                    |
|-----------|------------------------------------|
| Date/Time | Existing timestamp (local format)  |
| Value     | Existing kWh value                 |
| Comment   | Existing comment (empty if none)   |

- **Buttons** at the bottom, mirroring the Add form:
  - **Abbrechen** — discards changes, navigates back to the detail page.
  - **Speichern** — submits changes.

## Behavior

- All fields are editable.
- **Save** submits via `PUT /api/readings/:id`.
- After a successful save, navigate back to the detail page, which reflects the updated values.
- **Cancel** (top-bar back button or "Abbrechen") discards changes and returns to the detail page.
- Validation is identical to the Add view, including the in-app live range hints:

| Hint | Meaning                                    |
|------|--------------------------------------------|
| ≥ previous | value must be at least the previous reading |
| ≤ next     | value must be at most the next reading      |

- The live range hints must **exclude the record being edited** from its own neighbour calculation.

## Backend

- `PUT /api/readings/{id}` endpoint:
  - 404 if the record does not exist or belongs to a different meter.
  - Validates the new value against the readings immediately before/after, **excluding the record itself**.
  - Returns 422 with a German message when the value violates the ordering.
- `GET /api/readings/neighbours` must support excluding a specific record (e.g. an optional `exclude_id` query parameter) so the edit view can show correct live hints when the timestamp changes.

## Notes

- The page title "Ablesung bearbeiten" distinguishes the edit flow from the add flow ("Neue Ablesung").
- Removing the "← Zurück" link from the Add form header is tracked separately (see issue for tech debt).