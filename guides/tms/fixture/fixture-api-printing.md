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

Each section gives the gateway step, the TMS checks in order, and the message shown. The gateway checks the login and the permission (Print Settings, Edit) before it forwards the changes to the queue or the print status.

## Print queue: read (GET print/v1/get_print_queue)

- Gateway: needs a login.
- TMS: returns the matches waiting in the queue, filtered by category and search text, with a limit and the total count.
- A search with no matches returns an empty list with code 200.
- An empty queue returns an empty list with code 200.
- Errors return code 500 with the error text.

## Print queue: add or remove matches (PUT print/v1/update_queue_status)

- Gateway: needs Print Settings and Edit.
- TMS: the matches are added to the queue when the queue flag is true, and removed when it is false.
- Success: "Print Queue Updated" (200) with the IDs of the matches that changed.
- Errors return code 500 with the error text.

## Print status (PUT print/v1/update_print_status)

- Gateway: needs Print Settings and Edit.
- TMS: marks the matches as printed, for a single match or a whole day.
- Success: "Print Status Updated" (200). Errors return code 500 with the error text.

## Print settings (GET print/v1/get_print_settings)

- Gateway: needs a login.
- No event configuration: "No Event Found" (404).
- A named configuration that is not in the event print settings: "Configuration '{config}' not found in event print settings" (404).
- Success returns the print settings (or only the named part), with code 200.

## Print alert settings (GET print/v1/get_print_alert_settings)

- Gateway: needs a login.
- Returns the global alert settings when there is no event setting, otherwise the event setting. The alert settings include the number of seconds after which the match print popup closes by itself.
- Errors return code 500 with the error text.

## Match data for printing (GET match/v1/matches)

- Used by the print popup and the day-wise sheet to read the matches and their results. Its rules are described in the results and scoring API guides.
