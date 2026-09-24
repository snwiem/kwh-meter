# ADR 0004 — Notification Transport: Self-hosted ntfy

## Status

Accepted

## Date

2026-09-24

## Context

Feature 0012 (`docs/feature/0012_notification_plan.md`) requires the backend to
push reminder notifications to the user's phone at planned daily times. The
deployment is a local-network Docker Compose stack; the user already has the ntfy
app installed. Candidate mechanisms:

- **Self-hosted ntfy server** (container in docker-compose): backend POSTs a
  message; subscribed devices receive it. No account, LAN-local, tiny footprint.
- **Gotify**: similar, but Android-only (no official iOS client).
- **Apprise API**: gateway to 90+ channels; more flexible, more config overhead.
- **Telegram bot**: no extra container, works remotely, but requires internet,
  a bot token, and a third party in the loop.
- **Browser Web Push (PWA)**: push services (FCM/autopush) require internet —
  unsuitable for LAN-only.

## Decision

Use a **self-hosted ntfy server** added as a service to the repo's
`docker-compose.yml`. The backend publishes via plain HTTP `POST` to the internal
compose URL (`NTFY_URL`); the phone subscribes via the ntfy app to
`NTFY_PUBLIC_URL`/`NTFY_TOPIC`. The ntfy app supports multiple servers side by
side, so the existing default-server subscriptions stay untouched.

## Consequences

- One additional container in the stack; no external dependencies or accounts.
- Notifications work while the phone is in the LAN (WebSocket). Reliability
  outside the LAN or on iOS is limited without an upstream relay — acceptable for
  this single-user, local-network app.
- Publishing is a trivial HTTP call; no client library or push-certificate
  handling in the backend.
- If other channels are ever needed, an Apprise layer could be added later
  without changing the scheduler design.
