---
doc_id: tms.printing.api
title: Backend logic of the Printing APIs – print settings, printed status, print queue, alerts and the data the sheets read
routes:
  - tms/printing/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - printing api
  - print settings backend
  - save print settings rules
  - print status backend
  - why is a match marked printed
  - print queue backend
  - print alert backend
  - print data api
  - back number logos setting
  - print settings not found
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What does the backend do when I save the print settings?
  - Why does the print settings call say "No Event Found"?
  - What does the backend do when a match is marked as printed?
  - What does the backend say when the print queue is updated?
  - Which data calls does the Printing page make?
  - What permission is needed to change the print settings?
backend_sources:
  - gateway/src/routers/print_router.py (get_print_settings, update_print_settings, update_print_status, get_print_queue, update_queue_status, get_print_alert_settings)
  - tms/src/router/print_router.py
  - tms/src/service/print_service.py (get_print_settings, update_print_settings, update_print_status, set_queue_status, get_print_queue)
  - tms/src/schema/print_schema.py (PrintSettings, PrintSettingConfig, PrintAlertSettings)
  - tms/src/crud/config_crud.py (PRINT_SETTING configs)
source_files:
  - src/app/modules/tms/printing/printing.component.ts
  - src/app/core/services/event-service/event.service.ts
  - src/app/core/services/print-alert/print-alert.service.ts
  - src/app/core/constants/api-constant.ts
  - gateway/src/routers/print_router.py
---
# Backend logic – Printing APIs

Each section gives the gateway step, the checks in order, and the message. The gateway checks the login and the permission before it forwards each call. The data calls that the sheets read are listed at the end with the guides that describe them.

## Get print settings (GET print/v1/get_print_settings)

- Gateway: needs a valid login token, checked inside the route; without one the reply is 401 "Unauthorized Access". There is no feature permission check.
- An optional part name (singles, doubles or teams) returns only that part.
- TMS: reads the print settings of the event. No event configuration: "No Event Found" (404).
- A named configuration that is not in the event's print settings: "Configuration '{config}' not found in event print settings" (404).
- Success: the print settings, or only the named part, with code 200. Unexpected error: the error text (500).

## Update print settings (PUT print/v1/update_print_settings)

- Gateway: needs Print Settings and Edit (403 "Access Denied" without it, 401 "Unauthorized Access" without a valid login).
- Body: up to three sections (singles, doubles, teams) and the back number logos. Each section holds the event details, the colour theme, the logos, the match details, the best-of count and a flag that the setting was updated.
- TMS: the saved settings of the event are read. Only the sections that are sent are replaced; the others keep their saved value. The back number logos replace the saved list when sent.
- When the event has no saved settings, the sent settings become the event settings.
- Success: "Print Settings Updated" (200). Unexpected error: the error text (500).
- A new event gets no print settings: the step that would copy the global (default) print settings into a new event is switched off in the code. Until the first save, the read answers "No Event Found" (404).

## Update printed status (PUT print/v1/update_print_status)

- Gateway: needs Print Settings and Edit (administrators pass without the check). Body: the match IDs, and whether the print was a day-wise print.
- TMS: only matches with at least two real players (not a BYE) are marked; the others are skipped silently.
- Day-wise print: sets the day-wise printed mark only. The match stays in the print queue.
- Other prints: set the printed mark and take the match out of the print queue at the same time.
- Success: "Print Status Updated" (200), also when no match could be marked. Unexpected error: the error text (500).
- The Printing page sends this call when the browser print window opens. It does not check that the paper was printed, and shows no message when the call fails.

## Toss sheet printed status (PUT print/v1/update_toss_print_status)

- Gateway: needs Print Settings and Edit. Body: the match IDs whose toss sheets were printed.
- TMS: every listed match that is not deleted gets the toss printed mark (no player check). Success: "Toss Print Status Updated" (200). Unexpected error: the error text (500).
- The Printing page does not send this call.

## Print queue: read (GET print/v1/get_print_queue)

- Needs a login (401 "Unauthorized Access" without one). Query: the event, optional category IDs (comma separated), a search, and a page size and offset.
- Returns the queued matches that are not printed yet, newest first, with the total. Left out: matches with a BYE (also when the BYE came after queuing), team sub matches, and matches whose stage, group or round was deleted.
- The search matches the category name or short name, a player name, the match ID or the match number.
- The Printing page asks with size 0 to read only the count for the **Ready for Print** badge. A search with no match, or an empty queue, returns an empty list with code 200.

## Print queue: add or remove (PUT print/v1/update_queue_status)

- Needs Print Settings and Edit. The query flag says add (true) or remove (false).
- Adding keeps only matches with at least two real players; the others are skipped silently. Removing works for any match.
- Success: "Print Queue Updated" (200), with the IDs of the matches changed. Unexpected error: the error text (500).

## Print alerts: read (GET print/v1/get_print_alert_settings)

- Needs a valid login token (401 "Unauthorized Access" without one). Query: a global flag (true for the organisation default) and the event ID.
- Returns the saved settings under data (code 200). An event (or organisation) with nothing saved gets the built-in values: mode "DISABLE", sound on, no tone chosen, auto-dismiss after 30 seconds. It does not fall back to the global default.
- A new event gets a copy of the global default when it is created; later changes to the global default do not reach it.
- When the mode is "DISABLE", the Printing page hides **Ready for Print** and never shows the match ready popup. If the read fails, alerts are treated as on.

## Print alerts: save and reset (PUT update_print_alert_settings, PUT reset_print_alert_settings)

- Need Print Settings and Edit. These calls are made from the print alert settings, not from the Printing page.
- Save stores the sent settings as the event override (or as the global default). Success: "Print Alert Settings Updated" (200).
- Reset copies the current global default into the event (the built-in values when no global default is saved). Success: "Print Alert Settings Reset to Global Defaults" (200), with the settings.
- Unexpected error: the error text (500).

## Data read by the sheets

These calls are described in their own guides:

- **Match list and day-wise sheet** – match/v1/matches (results API guide and scheduler API guide).
- **Group matches and groups** – group/v1/get_group_matches and group/v1/get_groups (group stage API guide).
- **Stages** – stage/v1/get_stages (stage API guide).
- **Knockout tree and position matches** – fixture/v1/get_knockout_matches (knockout API guide).
- **Players and back numbers** – register/v1/get_event_participants (fixtures and shell API guides).
- **Schedule slots** – planner/v1/get_event_slots (scheduler API guide).
- **Venues for the day-wise sheet** – event/v1/event_venues (shell API guide).
- **Team playing order and toss sheets** – playing_order/v1/get_team_playing_order_with_matches and its bulk call (shell and results API guides).
- **Rule settings of the stage** – rule_setting/v1/get_rule_settings (results API guide).

## Permissions

- Reading the settings, the alerts and the queue needs a login only. Saving settings, marking printed status (score sheets and toss sheets), changing the queue and changing the alert settings need the Print Settings permission (Edit). Administrators always pass. Without it the server answers 403 "Access Denied".

## Calls not traced in this pass

- The print data of the Badminton sheet beyond the settings above.
