# Feature 0010 — Energy Consumption Overview (Analytics)

## Summary

Add an analytics view that renders **energy consumption over time**, derived from the
intervals between consecutive readings. The purpose is to give the user an honest
"feeling" for when and how much energy the household consumes — not to produce exact
measurements.

The view is deliberately minimal and descriptive, not prescriptive:

- A large spike in a short time window implicitly signals a big consumer (e.g. electric
  vehicle charging).
- A long, flat stretch implies the house's baseline ground load.

The application never labels or categorizes consumers; the user reads that from the shape
of the data.

## Background & Goals

- There is **no smart meter** and **no automated ingestion**. All data comes from manually
  recorded meter readings.
- The meter reports a **cumulative energy counter (kWh)**. A reading stores energy, not power.
- **Power (kW) is always a derived average** over the interval between two consecutive
  readings (see `docs/domain-concept.md` → "Energy vs. Power").
- The headline metrics the user wants to observe are:
  - **Ground load** — the house's persistent baseline consumption (spot measurements suffice).
  - **Individual large consumers** — energy drawn during a temporary activity (car charging,
    hot water, etc.), captured by recording before/after readings.
  - **Comparison across time** — how much energy was consumed over certain hours, days,
    months, and years.

## Core concept: the interval

The fundamental unit of this feature is the **interval between two consecutive readings**:

| Metric         | Derivation                                                            |
|----------------|-----------------------------------------------------------------------|
| Energy (ΔkWh)  | `value_after − value_before`                                           |
| Duration (h)   | `timestamp_after − timestamp_before`                                   |
| Average power  | `ΔkWh ÷ duration` (kW)                                                |

Both **energy (kWh)** and **average power (kW)** are shown for every interval — the user
wants both views on the data.

## Visualization (MVP): raw intervals

- Each gap between two consecutive readings is rendered as one **bar/sliver**:
  - **Width / horizontal extent** is proportional to the *actual elapsed time* of the interval.
  - **Height** represents the **energy (kWh)** consumed in that interval.
- The average power (kW) of the interval is also presented (e.g. tooltip, list row, or a
  secondary annotation).
- Because the width reflects real elapsed time, a short, tall block is visually distinct from
  a long, flat stretch — the honest "feeling" the user asked for.

## Granularity boundary

The achievable granularity is bounded by the frequency of manual recordings:

- Log once a day → daily shape.
- Log before/after an activity → that activity's spike is visible.

The feature does **not** invent finer resolution than the gaps between readings.

## Explicitly out of scope (for now)

- **Consumer categorization / tagging** — the comment field remains free text; the app never
  classifies a consumer type. Peaks imply large consumers; nothing is labeled automatically.
- **Calendar aggregation** (day/week/month/year buckets) — **deferred**. Bucketing would
  *allocate* energy to calendar periods even though readings rarely fall on bucket boundaries,
  which conflicts with the "honest, not exact" principle. Start with raw intervals; revisit
  aggregation only if the raw view does not satisfy the user's needs.
- Exact, meter-grade measurement — approximation is explicitly accepted.

## Open questions

- Whether the analytics view is a separate page (via the global burger menu) or embedded on
  the main screen (to be decided during implementation planning).

## Status & next steps

> Last updated 2026-09-20.

Requirements brainstorm is complete and captured in this document. Key agreed decisions:
- Manual readings only (no smart meter / automated ingestion).
- Energy (kWh) is measured; power (kW) is a derived average over the interval between
  consecutive readings (see `docs/domain-concept.md`).
- Both energy and average power are shown per interval.
- No consumer categorization — free-text comment only; peaks imply large consumers.
- Start with the raw-interval visualization; calendar aggregation is deferred.

Remaining next actions:
1. (Optional) Decide the analytics-view placement (separate page vs. main screen).
2. Create a GitHub issue from this spec (use the `feature` issue template) and add it to the
   project board (`snwiem/kwh-meter` → Projects → `kwh-meter`), milestone MVP.
3. Implement:
   - **Backend**: endpoint that computes interval deltas (ΔkWh, duration, average kW) between
     consecutive readings for the active meter.
   - **Frontend**: raw-interval chart (bar width ∝ elapsed time, height = kWh; average kW
     secondary).