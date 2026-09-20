# Feature 0008 — Infinite Scroll on Main Screen

## Summary

Replace the current page-based pagination on the main screen with an infinite scroll list. Records are loaded in batches as the user scrolls down, providing a seamless mobile-first experience.

## Motivation

The current pagination (previous/next buttons and page numbers) is not well-suited to mobile devices. An infinite scroll list feels natural on touch screens and avoids the need to tap pagination controls.

## Behavior

- On initial load, the first batch of records is fetched (e.g. 20 records).
- As the user scrolls toward the bottom of the list, the next batch is automatically fetched and appended.
- A loading indicator is shown at the bottom while a fetch is in progress.
- When all records have been loaded, no further fetches are triggered.
- If a fetch fails, an error message is shown with a **Retry** button at the bottom of the list.

## Implementation Notes

- Use the browser's `IntersectionObserver` API to detect when a sentinel element at the bottom of the list enters the viewport.
- The existing `GET /api/readings?page=&page_size=` endpoint continues to be used — only the frontend paging logic changes.
- The pagination UI (buttons, page numbers) is removed entirely.
- Page size for infinite scroll batches can be larger than the current value (e.g. 20).

## Notes

- Sorting remains newest-first (descending by timestamp).
- Pull-to-refresh behavior is out of scope for this feature.
