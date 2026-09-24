# Feature 0011 — Date/Time Range Selector for Analytics

## Summary

Add a date/time range selector **above** the analytics chart (Analyse page) so the
user can focus the raw-interval visualization on a chosen span. The range is
expressed as ordinary **datetime pickers** (not dropdowns of readings); the picked
datetime is snapped to actual readings, and the UI guarantees FROM is always
strictly before TO.

## Decisions (refinement session, 2026-09-24)

1. **Selector model:** two independent `datetime-local` pickers — „Von" (FROM) and
   „Bis" (TO). Free input; reading lists as dropdowns were rejected on UX grounds.
2. **Interval resolution (snap rules):**
   - FROM snaps to the **latest reading on-or-before** the picked datetime. Ties
     (identical timestamps) broken by reading id, oldest first. If no reading
     exists on-or-before FROM (picked time is before the first reading), clamp to
     the **earliest** reading.
   - TO snaps to the **earliest reading on-or-after** the picked datetime. Same
     tie-break. If no reading exists on-or-after TO, clamp to the **latest**
     reading.
   - Consequence: boundary intervals are shown in full — the chart never cuts an
     interval at the picker line.
3. **FROM < TO enforcement:** **auto-clamping, not validation.** Picking a FROM
   ≥ TO moves TO back to the last valid datetime before FROM (and vice versa).
   An invalid state can never persist; no error message appears.
4. **Initial state:** on page load, FROM = timestamp of the **oldest** reading and
   TO = timestamp of the **newest** reading (i.e. today's full-range view).
5. **Reset:** a single-tap reset button („Gesamter Zeitraum") restores the initial
   full-range selection.
6. **No persistence:** nothing stored in URL or local storage; every page load
   starts at the full range.
7. **Filtering is client-side.** `GET /api/analytics/intervals` is unchanged and
   fetched once; narrowing happens in the browser. Scope remains frontend-only.
   Rationale: filtering is trivial for any realistic data volume (manual
   readings); server-side `from`/`to` params can be added later as a pure
   optimization if scale ever demands it.

## Empty state

If the resolved span contains fewer than two readings (no intervals), the chart
area shows the hint „Keine Intervalle im gewählten Zeitraum" instead of an empty
SVG.

## Explicitly out of scope

- Calendar-bucket aggregation (still deferred, see feature 0010).
- Server-side range filtering.
- Persistence of the selection.

## Acceptance Criteria

- [ ] FROM and TO datetime pickers are placed above the chart on the Analyse page
- [ ] Initial selection covers the full range (oldest → newest reading)
- [ ] Auto-clamping guarantees FROM is always strictly before TO (and vice versa)
- [ ] FROM/TO snap to readings per the rules above (on-or-before / on-or-after,
      clamping at the edges, id tie-break)
- [ ] One-tap reset button restores the full range; no persistence
- [ ] Filtering is client-side; no backend changes
- [ ] Empty state hint when the selection contains fewer than two readings
- [ ] Mobile-first layout, consistent with the existing Analyse page

## Dependencies

- #32 (analytics overview page — done)
