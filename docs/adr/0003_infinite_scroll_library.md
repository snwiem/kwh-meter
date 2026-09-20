# ADR 0003 — Infinite Scroll via @vueuse/core useInfiniteScroll

## Status

Accepted

## Date

2026-09-20

## Context

Issue #12 (`docs/feature/0008_infinite_scroll.md`) replaced the main screen's pagination with an infinite scroll list. An initial implementation used a hand-rolled `IntersectionObserver` plus a sentinel element. This exhibited an edge-case bug: once the sentinel element entered the viewport, it remained "intersecting" across successive loads, so the observer never re-fired and loading stalled.

## Decision

Use the `useInfiniteScroll` composable from `@vueuse/core` for scroll-driven loading, instead of a hand-rolled `IntersectionObserver`.

## Consequences

- Adds `@vueuse/core` as a runtime dependency (small, tree-shakeable, battle-tested).
- Scroll-position tracking, distance threshold, and debounce are handled by the library rather than in-house code.
- A small post-load re-check is still required to fill the viewport when the list is shorter than the screen, because scroll-event-driven loading does not fire when no scrollbar exists.