# Feature 0001 — Manage Energy Meter

## Summary

The application is configured with exactly one active energy meter via an external configuration file. The meter is not managed through the UI — it is read-only from the application's perspective.

## Configuration

- The energy meter is defined in a **mandatory JSON configuration file**.
- The path to the file is provided via an **environment variable** at application start.
- If the config file is missing or the environment variable is not set, the application must **refuse to start**.
- The config file must be mountable into the backend container at runtime (e.g. via a Docker volume mount).

### Required fields in the config file

| Field        | Type   | Description                          |
|--------------|--------|--------------------------------------|
| zaehler_nr   | string | Meter ID, unique within Germany (Zählernummer) |
| street       | string | Street name                          |
| house_number | string | House number                         |
| postal_code  | string | German postal code (PLZ)             |
| city         | string | City name                            |

All fields are required. Country is implicitly Germany and not included.

## Persistence behavior

- On every application start the configured `zaehler_nr` is used as the active meter identity.
- If the `zaehler_nr` changes between restarts, previously collected readings remain in the database linked to the old `zaehler_nr` and are **not deleted**.
- New readings are always assigned to the currently configured `zaehler_nr`.
- The UI only ever displays readings for the currently configured `zaehler_nr`.

## UI

- The **Zählernummer** is displayed prominently at the top of the main screen.
- No UI is provided to create, edit, or delete the meter — it is fully controlled via the config file.
