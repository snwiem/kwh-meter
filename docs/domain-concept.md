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
