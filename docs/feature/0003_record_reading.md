# Feature 0003 — Record a Reading

## Summary

The user can add a new kWh reading for the currently configured energy meter. This is done on a dedicated separate page, navigated to via the "+" button on the main screen.

## UI — Add Reading Page

### Fields

| Field     | Type          | Required | Default            | Constraints                                      |
|-----------|---------------|----------|--------------------|--------------------------------------------------|
| Timestamp | Date + Time   | Yes      | Current date/time  | Selectable via standard date/time picker components |
| Value     | Decimal number | Yes      | Empty              | Positive number; max 1 decimal place; integer input automatically gets `.0` appended |
| Comment   | Text          | No       | Empty              | Max 255 characters                               |

### Timestamp input
- Defaults to the **current date and time** when the page is opened.
- The user can change both date and time using **standard UI components** (e.g. a calendar/date picker and a time selector).

### Value input
- Accepts decimal numbers with **at most 1 digit after the decimal separator**.
- Integer inputs are accepted and stored as `<value>.0`.
- Values are rounded to 1 decimal place if more decimals are entered.
- Only positive numbers are valid.
- The unit **kWh** must be clearly labeled next to the input field.

### Comment input
- Optional free-text field.
- Maximum **255 characters**.
- Intended for short notes (e.g. "car is currently charging").

## Behavior

- On successful submission the user is navigated back to the **main screen**.
- The newly added record must appear at the top of the readings list.
- On cancel/back the user is navigated back to the main screen without saving.

## Assignment

- The new reading is always assigned to the **currently configured `zaehler_nr`**.
- The user cannot select or change the meter — it is implicit.
