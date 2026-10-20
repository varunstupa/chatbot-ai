---
doc_id: tms.fixture.api-shell
title: Backend logic of the fixtures page APIs – events, venues, settings, print and export
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - fixture api
  - backend logic fixtures
  - what happens when I save the event
  - update event rules
  - event fetch
  - event configs
  - draw settings api
  - display seeding api
  - venue save rules
  - print settings api
  - export fixtures rules
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What happens in the backend when I update the event?
  - Why does the update event return "Event Already Exists"?
  - What does the event fetch return when no event matches?
  - What does the backend do when I save venues?
  - Why can I not remove a date from a venue?
  - What is the backend rule for print settings?
backend_sources:
  - gateway/src/routers/events_router.py (get_events, update_event, get_event_configs, upsert_event_configs, upsert_event_venues, get_event_venues)
  - gateway/src/routers/print_router.py (get_print_settings, get_print_alert_settings, get_print_queue, update_print_status, update_queue_status)
  - gateway/src/routers/export_format_router.py (get_export_formats)
  - gateway/src/routers/worker_router.py (export_fixtures)
  - gateway/src/routers/playing_order_router.py (get_team_playing_order_with_matches)
  - tms/src/router/events_router.py
  - tms/src/service/event_config_service.py (get_event_configs)
  - tms/src/service/events_service.py (get_events, update_event, upsert_event_venues, get_event_venues)
source_files:
  - src/app/modules/tms/tms-fixture/tms-fixture.component.ts
  - src/app/shared/export-sidebar/export-sidebar.component.ts
  - src/app/shared/print-queue-sidebar/print-queue-sidebar.component.ts
---
# Backend logic – events, venues, settings, print and export

Each section lists what the gateway does, what the TMS does in order, and the message the user sees. Messages are the English text from the server. The gateway checks the login and the feature permission before it forwards a request; the TMS does the business checks.

## Load events (GET event/v1/get_events)

- Gateway: needs a login. For a user who is not the admin role, the gateway limits the events to the ones the user is associated with, using the user's resource permissions.
- TMS: filters by event IDs, name, event type, status (one or more), verification status, search, season, category and dates. Paging is applied when page and page size are both sent.
- Venues are attached when the caller asks for them.
- Success: "Event Fetch" (code 200) with the events and the total.
- No matching event: "Event Fetch" with code 204 and an empty list.

## Update event (PUT event/v1/update_event)

- Gateway: needs Edit on Event Access.
- TMS checks, in this order:
  1. Event not found: "No Event Found" (404).
  2. Points already published and a ranking field is changing: the edit or delete is refused with code 403. The server message has no English text in the translation file yet, so the screen may show the raw message key.
  3. Extra fields and the event name are validated, unless the request is a delete.
  4. Another event already has this name: "Event Already Exists" (403).
  5. Umpire settings that conflict with the event: a 409 with the validation message.
  6. Delete: only the user role that owns the event may delete it: "Unauthorized Access" (403).
  7. Delegation turned on without the show users: "Delegation Show Users Required" (409).
  8. Date changes are checked against the venue dates.
- If every check passes, the event is saved. A change to the automatic fixture publish setting updates the stages of the event.

## Event configs – draw settings and display seeding (GET and PUT event/v1/get_event_configs, upsert_event_configs)

- GET: returns the configs of the event or category. For display seeding the value is the tenant-wide setting; when none is saved, the default is returned.
- GET with no saved config for other types: returns an empty list.
- Success message: "Configs Fetched Successfully" (200).
- Upsert: validates the config type. Invalid values are refused with code 400 and the reason in the message.
- Success message: "Config Upserted Successfully" (200).
- Unexpected server error: "Error upserting config" or "Error fetching configs" (500) with the error text.

## Venues (GET and POST event/v1/event_venues)

- GET: no venues for the event: "No Venue Found" (404). Success: "Success" (200). Reserved tables are added when requested.
- POST (save venues): each venue can be edited by only one item of a save; a repeat gives 422 "Each venue can be edited (venue_update) by only one item of a save".
- The event must exist: otherwise "No Event Found" (404).
- A date cannot be removed when matches are already scheduled on it: "Cannot remove dates with scheduled matches" (409).
- Any failing item saves nothing. Success: "Success" (200).

## Print settings and print queue (print/v1 endpoints)

- get_print_settings: when the event has no configuration: "No Event Found" (404). When a named configuration is asked for and does not exist: "Configuration '{config}' not found in event print settings" (404).
- get_print_alert_settings: returns the alert settings (global or per event). Errors return code 500 with the error text.
- get_print_queue: returns the matches waiting to print, filtered by category and search, with the total count. An empty queue returns an empty list with code 200.
- update_print_status: marks matches as printed. Success: "Print Status Updated" (200).
- update_queue_status: adds the matches to the queue (is_queued true) or removes them (false).

## Export of fixtures and export formats

- export_fixtures (POST worker/export/fixtures): needs Edit on Fixture Access. The gateway adds the export to the worker queue and returns the job. The worker itself is not in the repos, so its file rules are not described here.
- get_export_formats: the gateway checks the login (401 "Unauthorized Access" when missing). The TMS returns the formats with the message "Export Formats Retrieved Successfully" (200). Errors return code 500.

## Playing order with matches (GET playing_order/v1/get_team_playing_order_with_matches)

- Match not found: "Match Not Found" (404).
- No playing order data for the match: "Match Data Not Found In Playing Order" (404).
- Golden match: the golden match playing order is added when one exists.
- Success returns the team names, the playing order and the sub-match scores (when asked for) in one response.
