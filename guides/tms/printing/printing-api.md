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
---
# Backend logic – Printing APIs

Each section gives the gateway step, the checks in order, and the message. The gateway checks the login and the permission before it forwards each call. The data calls that the sheets read are listed at the end with the guides that describe them.

## Get print settings (GET print/v1/get_print_settings)

- Gateway: needs a login.
- TMS: reads the print settings of the event. No event configuration: "No Event Found" (404).
- A named configuration that is not in the event's print settings: "Configuration '{config}' not found in event print settings" (404).
- Success: the print settings, or only the named part, with code 200. Unexpected error: the error text (500).

## Update print settings (PUT print/v1/update_print_settings)

- Gateway: needs Print Settings and Edit.
- Body: up to three sections (singles, doubles, teams) and the back number logos. Each section holds the event details, the colour theme, the logos, the match details, the best-of count and a flag that the setting was updated.
- TMS: the saved settings of the event are read. Only the sections that are sent are replaced; the others keep their saved value. The back number logos replace the saved list when sent.
- When the event has no saved settings, the sent settings become the event settings.
- Success: "Print Settings Updated" (200). Unexpected error: the error text (500).
- The service also has a helper that copies the global (default) print settings into an event. The point in the flow where it runs was not traced.

## Update printed status (PUT print/v1/update_print_status)

- Gateway: needs Print Settings and Edit. Body: the match IDs, and whether the print was a day-wise print.
- TMS: the matches are marked as printed. The day-wise flag is passed on to the match update.
- Success: "Print Status Updated" (200). Unexpected error: the error text (500).
- The Printing page sends this call when the print dialog closes after a print. The page does not check that the paper was printed.

## Print queue (GET print/v1/get_print_queue, PUT print/v1/update_queue_status)

- Read: needs a login. Returns the matches waiting in the queue, filtered by category and search, with the total. A search with no match, or an empty queue, returns an empty list with code 200.
- Update: needs Print Settings and Edit. The query flag says whether the matches are added to the queue (true) or removed (false). Success: "Print Queue Updated" (200), with the IDs of the matches changed. Unexpected error: the error text (500).

## Print alerts (GET print/v1/get_print_alert_settings)

- Needs a login. Returns the alert settings of the event, or the global default when the event has none. The settings include the number of seconds after which the match print popup closes by itself (none means it stays open).
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

- Reading the settings and the queue needs a login only. Saving settings, marking printed status and changing the queue need the print settings permission (Edit). The server refuses the change without it.

## Calls not traced in this pass

- The copy of the global print settings into an event, the printed-status flags used by the day-wise filter, and the print data of the Badminton sheet beyond the settings above.
