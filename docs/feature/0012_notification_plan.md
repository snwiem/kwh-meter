# Feature 0012 — Notification Plan (Reading Reminders)

## Summary

The app relies on regular manual readings of the energy meter. This feature adds a
**notification plan**: a list of daily times at which the backend sends a push
notification (via a self-hosted [ntfy](https://ntfy.sh) server) reminding the user
to record a new reading. The plan is edited in the web UI and persisted in the
database.

## Decisions (refinement session, 2026-09-24)

1. **Transport:** self-hosted **ntfy** server, added as a service to the repo's
   `docker-compose.yml`. The backend sends a plain HTTP `POST` to the ntfy server
   at each planned time; the user's phone (ntfy app) subscribes to the topic.
   See [ADR 0004](../adr/0004_notification_transport_ntfy.md).
2. **Plan granularity:** a **simple list of daily times** (`HH:MM`) that fire
   every day, regardless of weekday. Per-weekday plans are explicitly out of
   scope for now.
3. **Configuration via UI, persisted in DB:** the plan is editable online on a new
   page `🔔 Benachrichtigungen` (burger menu). No config-file editing or restarts.
4. **Unconditional sending:** every planned time always fires a notification.
   No "smart" suppression (e.g. skipping when a reading was just recorded).
5. **Connection settings via environment variables** on the backend service:
   - `NTFY_URL` — internal compose-network URL used for sending (e.g. `http://ntfy:80`).
   - `NTFY_PUBLIC_URL` — externally reachable URL of the ntfy server, shown in the UI.
   - `NTFY_TOPIC` — topic to publish/subscribe to (default e.g. `kwh-meter-readings`).
6. **Connection info shown in the UI:** the Benachrichtigungen page displays
   everything needed to subscribe the ntfy phone app: the public server URL and
   the topic — ideally as a `ntfy://` deep link that opens the app directly.
7. **Notification message:** fixed base text plus a **dynamic reference to the
   last recorded reading** with German relative-date abstraction:
   - reading today → `Die letzte war heute um 16:00`
   - reading yesterday → `Die letzte war gestern um 16:00`
   - older → `Die letzte war am 20.09.2026 um 16:00`
   - no reading at all → a sensible fallback (e.g. `Noch keine Ablesung erfasst.`)

   Example message: `⏰ Zeit für eine Zählerablesung! Die letzte war gestern um 16:00`
8. **Scheduler:** the backend runs an in-process scheduler (e.g. APScheduler) that
   fires at each configured time in the server's local timezone. Plan changes in
   the DB must be picked up without a restart (reschedule on change or frequent
   reload).
9. **Empty plan = no notifications:** if the list of times is empty, nothing is
   sent. This acts as the implicit on/off switch; no separate enable flag.

## UI sketch

Page `🔔 Benachrichtigungen` (burger menu entry):

- List of planned daily times (`HH:MM`), each removable; an input + add button to
  append a new time. Sorted ascending, duplicates rejected.
- Info section: ntfy public server URL + topic, with subscribe hint / deep link.

## Backend sketch

- New table `notification_time` (single column `time` of type TIME, unique).
- CRUD endpoints, e.g. `GET/POST /api/notification-times`,
  `DELETE /api/notification-times/{id}`.
- Scheduler job per time; on fire: query the latest reading, build the message,
  `POST` to `NTFY_URL/NTFY_TOPIC`.

## Explicitly out of scope

- Per-weekday schedules.
- Message-text customization in the UI.
- Conditional/smart suppression of notifications.
- Multiple channels (email, Telegram, …) — ntfy only.
- Authentication/authorization of the ntfy topic (LAN deployment).

## Acceptance Criteria

- [ ] `docker-compose.yml` includes an `ntfy` service reachable from the backend
      and from the LAN (published port).
- [ ] New page `🔔 Benachrichtigungen` in the burger menu.
- [ ] Daily notification times can be added and removed in the UI; persisted in
      the database (survive restarts).
- [ ] At each configured time (server local timezone), a notification is sent to
      the configured ntfy topic — unconditionally.
- [ ] Message contains the fixed reminder text and the last-reading reference with
      `heute` / `gestern` / `am DD.MM.YYYY` abstraction (and a fallback when no
      reading exists).
- [ ] Plan changes take effect without restarting the backend.
- [ ] The Benachrichtigungen page shows the public ntfy server URL and topic for
      easy phone-app subscription.
- [ ] With an empty plan, no notifications are sent.
