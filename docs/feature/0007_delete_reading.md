# Feature 0007 — Delete Reading

## Status

Ready

## Summary

A user can delete an existing kWh reading from the detail view. Tapping the Delete action button on the detail page opens a confirmation modal. The user must explicitly confirm before the record is permanently deleted.

## Trigger

- The Delete button (trash icon) on the detail page top bar opens the confirmation modal.

## Confirmation Modal

The modal displays:

- A warning message, e.g.:
  > **Eintrag löschen?**
  > Dieser Eintrag wird unwiderruflich gelöscht und kann nicht wiederhergestellt werden (außer über einen Export-Backup).
- Two buttons:
  - **Löschen** (confirm delete) — styled as a destructive/danger action
  - **Abbrechen** (cancel) — returns to the detail page without changes

## Behavior

- On confirm: sends `DELETE /api/readings/:id`, then navigates back to the main screen.
- On cancel: closes the modal, stays on the detail page.
- If the API call fails, an error message is shown inside the modal. The record is not removed.

## Notes

- The destructive nature of this operation (no trash/undo) justifies the mandatory confirmation step.
- The confirmation modal must clearly communicate that the action is irreversible.
