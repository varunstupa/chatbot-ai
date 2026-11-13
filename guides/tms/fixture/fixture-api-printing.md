---
doc_id: tms.fixture.api-printing
title: Backend logic of the printing APIs – print queue, print status, print settings and match print data
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - print api
  - print queue api
  - print queue rules
  - print status rules
  - print settings api
  - print alert settings api
  - why is the match not in the print queue
  - print data api
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What does the backend do when I add a match to the print queue?
  - Why does the print queue show no matches?
  - What does "Print Queue Updated" mean?
  - What does the backend check for the print settings?
  - Who can change the print status in the backend?
backend_sources:
  - gateway/src/routers/print_router.py (get_print_settings, get_print_alert_settings, get_print_queue, update_print_status, update_queue_status)
  - gateway/src/routers/match_router.py (matches, used for print data)
  - tms/src/router/print_router.py
  - tms/src/service/print_service.py (set_queue_status, get_print_queue, get_print_settings, get_print_alert_settings)
source_files:
  - src/app/shared/match-print-popup/match-print-popup.component.ts
  - src/app/shared/print-queue-sidebar/print-queue-sidebar.component.ts
  - src/app/modules/tms/tms-fixture/tms-fixture.component.ts
---
# Backend logic – printing APIs

Each section gives the gateway step, the TMS checks in order, and the message shown. The gateway checks the login and the permission (Print Settings, Edit) before it forwards the changes to the queue or the print status. A read call without a valid login is refused with "Unauthorized Access" (401).

## Print queue: read (GET print/v1/get_print_queue)

- Gateway: needs a login.
- TMS: returns the queued matches that are not printed yet, newest first, filtered by category and search text, with a limit and the total count.
- Left out: matches with a BYE (also when the BYE came after queuing), team sub matches, and matches whose stage, group or round was deleted (for example after a new draw).
- The search matches the category name or short name, a player name, the match ID or the match number.
- A search with no matches, or an empty queue, returns an empty list with code 200. Errors return code 500 with the error text.

## Print queue: add or remove matches (PUT print/v1/update_queue_status)

- Gateway: needs Print Settings and Edit (administrators always pass; 403 "Access Denied" otherwise).
- TMS: the matches are added to the queue when the queue flag is true, and removed when it is false.
- Adding keeps only matches with at least two real players (no BYE, no missing player). The others are skipped with no error. Removing works for any match.
- Success: "Print Queue Updated" (200) with the IDs of the matches that changed. Errors return code 500 with the error text.

## Print status (PUT print/v1/update_print_status)

- Gateway: needs Print Settings and Edit.
- TMS: marks the listed matches as printed, but only those with at least two real players. A normal print also takes them out of the print queue. A day-wise print sets only the day-wise mark and leaves the queue as it is.
- The fixtures page (popup and print queue) always sends a normal print. A printed match is no longer offered in the match print popup.
- Success: "Print Status Updated" (200). Errors return code 500 with the error text.

## Print settings (GET print/v1/get_print_settings)

- Gateway: needs a login.
- No print settings saved for the event: "No Event Found" (404). A new event has none until they are first saved.
- A named configuration that is not in the event print settings: "Configuration '{config}' not found in event print settings" (404).
- Success returns the print settings (or only the named part), with code 200.

## Print alert settings (GET print/v1/get_print_alert_settings)

- Gateway: needs a login.
- Returns the event's saved alert settings. An event with nothing saved gets the built-in values (alerts disabled, sound on, auto-dismiss after 30 seconds); it does not fall back to the global setting.
- A new event gets a copy of the global setting when it is created. Later global changes do not reach it.
- When the alert mode is set to disabled for the event, the admin app hides **Ready for Print**, the print queue and the print popups.
- If the settings cannot be read, the admin app keeps the popup open with no sound and no auto-dismiss. Errors return code 500 with the error text.

## Print alert settings: change or reset (PUT print/v1/update_print_alert_settings, PUT print/v1/reset_print_alert_settings)

- Gateway: needs Print Settings and Edit.
- Change saves the sent settings for the event (or as the global setting): "Print Alert Settings Updated" (200).
- Reset copies the current global setting into the event (the built-in values when none is saved): "Print Alert Settings Reset to Global Defaults" (200).

## Match data for printing (GET match/v1/matches)

- Used by the print popup and the day-wise sheet to read the matches and their results. Its rules are described in the results and scoring API guides.
