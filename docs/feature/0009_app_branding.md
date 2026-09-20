# Feature 0009 — App Branding (Logo & Tab Title)

## Summary

Improve the app's visual identity by adding a proper icon/logo to the top bar and updating the browser tab title to a more appropriate German-language name.

## Browser Tab Title

Change the HTML `<title>` from `kWh Meter` to **`Zählerstand`**.

Rationale: "Zählerstand" is the German term that directly describes what the app captures — the current reading of an energy meter. It is concise, familiar to the target audience, and unambiguous.

## App Icon / Logo

Add a small icon or logo to the left side of the top bar, alongside (or replacing) the plain text app name.

### Options (in order of preference)

1. **SVG icon** — a simple electricity / lightning bolt or meter gauge icon rendered inline in the top bar.
2. **Favicon** — a matching favicon (`/favicon.ico` or `favicon.svg`) so the icon is consistent in the browser tab as well.

### Requirements

- The icon must be visually meaningful (electricity / energy meter theme).
- It must be legible at small sizes (≥ 24px).
- It should work in both light and dark mode if applicable.
- No external image hosting — the icon must be bundled with the app.

## Notes

- The Zählernummer display in the top bar (implemented in MVP) remains in place.
- The favicon should match the top-bar icon for consistency.
