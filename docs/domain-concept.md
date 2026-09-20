# Domain Concept

This document describes the core domain objects and their meaning within the kwh-meter application.

## Energy Meter (Stromzähler)

An energy meter represents a physical electricity meter installed at a specific location in Germany.

### Identity

- The **Zählernummer** (meter number) is the globally unique identifier of a physical energy meter.
- It is assigned by the grid operator and is printed on the physical device.
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
| Zählernummer  | Zählernummer    | Globally unique meter identifier   | Yes      |
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
| Value         | The kWh value read from the meter display                | Yes      |
| Comment       | An optional free-text note about this reading            | No       |
