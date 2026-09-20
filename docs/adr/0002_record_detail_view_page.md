# ADR 0002 — Record Detail View as a Dedicated Page

## Status

Accepted

## Date

2026-09-20

## Context

The original feature specification for the record detail view (issue #6, `docs/feature/0005_record_detail_view.md`) described a modal overlay opened on top of the main screen. After the MVP, this approach was revisited during refinement.

## Decision

Use a dedicated route/page (`/readings/:id`) for the read-only record detail view instead of a modal overlay.

## Consequences

- The detail view is a separate page, consistent with the Add and Edit views, which is more ergonomic on mobile (its own top bar, room for actions, and a natural back-navigation stack).
- The detail page top bar carries the Edit and Delete actions plus a back button.
- The navigation flow becomes: list → detail page → edit page, with the back button returning through the hierarchy.
- No modal visibility/state management is required for the detail view itself (a modal remains only for the delete confirmation, see `docs/feature/0007_delete_reading.md`).

## Supersedes

- The modal-overlay design originally described in `docs/feature/0005_record_detail_view.md` (superseded and rewritten).