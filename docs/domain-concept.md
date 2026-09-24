# Domain Concept

This document describes the core domain objects and their meaning within the kwh-meter application.

## Energy Meter (Stromzähler)

An energy meter represents a physical electricity meter installed at a specific location in Germany.

### Identity

- The **Zählernummer** (meter number) is the unique identifier of a physical energy meter within Germany.
- It is assigned by the grid operator and is printed on the physical device.
- Uniqueness is guaranteed at country level (Germany) only — not internationally.
- Within this application, the Zählernummer is the **primary reference** that links all collected readings to a specific physical meter.
- The application is configured with exactly **one active meter** at any point in time (via an external config file).

### Behavior on configuration change

- The active meter is read from a mandatory configuration file on every application start.
- If the Zählernummer in the config file changes (e.g. due to a meter replacement or a corrected typo), the previously collected readings are **never deleted** — they remain in the database linked to their original Zählernummer.
- New readings are always assigned to the **currently configured** Zählernummer.
- The UI only ever displays readings belonging to the currently configured Zählernummer. Records from other meter IDs are not visible through the UI.

### Attributes (MVP)

| Field         | German term     | Description                        | Required |
|---------------|-----------------|------------------------------------|----------|
| Zählernummer  | Zählernummer    | Meter identifier, unique within Germany | Yes      |
| Street        | Straße          | Street name of the meter location  | Yes      |
| House number  | Hausnummer      | House number of the meter location | Yes      |
| Postal code   | Postleitzahl    | German postal code (PLZ)           | Yes      |
| City          | Stadt           | City of the meter location         | Yes      |

> Country is implicitly Germany. No country field is needed.

---

## Energy vs. Power (Energie vs. Leistung)

The application records **energy**, not power. The two are often conflated in everyday language; here they are kept strictly separate:

| Term   | German   | Unit      | Meaning |
|--------|----------|-----------|---------|
| Energy | Energie  | Wh / kWh  | A **cumulative** quantity — the total amount of electricity transferred. This is what the meter counts and what every `Reading.value_kwh` stores. |
| Power  | Leistung | W / kW    | The **rate** at which energy flows — energy per unit of time. Not measured directly by the meter. |

### Key consequence

The meter only ever reports a cumulative energy counter, so a `Reading` is an **energy value (kWh)**, not a power value (kW). Power can only be **derived as an average** over the interval between two consecutive readings:

```
average power (kW) = (value_after − value_before) [kWh] ÷ (timestamp_after − timestamp_before) [h]
```

This derived average power is the basis for all analytics (ground load, individual-consumer measurements, and time-period comparisons) described in the feature docs.

---

## Reading (Ablesung)

A reading represents a single manually recorded value taken from the energy meter at a specific point in time.

### Attributes (MVP)

| Field         | Description                                              | Required |
|---------------|----------------------------------------------------------|----------|
| Zählernummer  | Reference to the meter this reading belongs to          | Yes      |
| Timestamp     | Date and time the reading was taken                      | Yes      |
| Value         | The kWh reading shown on the meter display; stored to one decimal place | Yes |
| Comment       | An optional free-text note about this reading            | No       |

### Business rules

- Readings are time-ordered and the value is **monotonically non-decreasing**: a reading's value must be greater than or equal to the immediately preceding reading (if any) and less than or equal to the immediately following reading (if any). This reflects that an electricity meter only ever counts upward.
- This invariant is enforced by the backend on both create and update (a value that violates the ordering is rejected with a validation error).

---

## Notification Plan (Benachrichtigungsplan)

The notification plan reminds the user to record readings regularly. It is a small persisted entity of its own (table `notification_times`), edited in the web UI on the `🔔 Benachrichtigungen` page.

### Attributes

| Field | German term | Description                                                     | Required |
|-------|-------------|-----------------------------------------------------------------|----------|
| Time  | Uhrzeit     | A daily time (`HH:MM`) at which a reminder is sent, in the server's local timezone | Yes      |

### Business rules

- The plan is a simple list of **daily times**: each time fires every day, regardless of weekday. Times are unique and always presented sorted ascending.
- Sending is **unconditional**: every planned time always produces a reminder — there is no suppression based on recently recorded readings.
- An **empty plan disables notifications** entirely; it acts as the implicit on/off switch (no separate enable flag).
- Each reminder references the latest reading of the active meter using the German relative-date abstraction (*heute* / *gestern* / *am DD.MM.YYYY*).
- Transport is a self-hosted [ntfy](https://ntfy.sh) server running in the same compose stack; plan changes take effect without restarting the backend.

See [feature 0012](feature/0012_notification_plan.md) and [ADR 0004](adr/0004_notification_transport_ntfy.md).
