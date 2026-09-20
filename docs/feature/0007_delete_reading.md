# Feature 0007 — Delete Reading

## Status

Ready

## Summary

A user can permanently delete an existing kWh reading from the detail view. Tapping the Delete action button on the detail page opens a simple confirmation modal. The user must explicitly confirm before the record is deleted.

## Trigger

- The Delete button (trash icon) on the detail page top bar opens the confirmation modal.

## Confirmation Modal

A minimal modal asking a plain yes/no question:

- Question: **"Wirklich löschen?"**
- No record details, no irreversibility explanation — kept deliberately simple.
- Two answer buttons:
  - **Ja** (confirm) — styled as a destructive/danger action
  - **Nein** (cancel)

## Behavior

- On **Ja**:
  - Sends `DELETE /api/readings/:id`.
  - On success: navigates back to the main screen.
  - On failure (404 or server error): closes the modal and shows the error message at the top of the detail page.
- On **Nein**:
  - Closes the modal; stays on the detail page with no changes.

## Backend

- `DELETE /api/readings/{id}` endpoint:
  - 404 if the record does not exist or belongs to a different meter.
  - 204 No Content on success.

## Notes

- The destructive nature of this operation (no trash/undo) justifies the mandatory confirmation step.
- The confirmation is intentionally minimal — a bare "Are you sure?" with Ja/Nein answers and no extra context.