# Feature 0006 — Edit Reading

## Status

Ready

## Summary

A user can edit an existing kWh reading from the detail view. Tapping the Edit action button on the detail page navigates to an edit view that is pre-filled with the current values of the selected record.

## Trigger

- The Edit button (pencil icon) on the detail page top bar navigates to the edit view.

## Edit View Content

The edit view reuses the same form layout as the "Add Reading" view (`AddReadingView`), but is pre-filled with the existing record data:

| Field     | Pre-filled with             |
|-----------|-----------------------------|
| Date/Time | Existing timestamp          |
| Value     | Existing kWh value          |
| Comment   | Existing comment (or empty) |

## Behavior

- All fields are editable.
- A **Save** button submits the changes via `PUT /api/readings/:id`.
- A **Cancel** button discards changes and navigates back to the detail page.
- After a successful save, the user is navigated back to the detail page, which reflects the updated values.
- Validation rules are identical to the Add Reading view.

## Route

`/readings/:id/edit`

## Notes

- Reusing the form component from Add Reading is preferred over building a separate component.
- The page title / top bar should indicate "Eintrag bearbeiten" (Edit Entry) to distinguish from the add flow.
