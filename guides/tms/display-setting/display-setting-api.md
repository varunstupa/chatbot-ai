---
doc_id: tms.display-setting.api
title: Backend logic of the Display Setting APIs – match lists, venues and days, match status, LED settings, the live update feed and the gateway routes
routes:
  - tms/display-setting/:event_id/:participant_id/:category_id
aliases:
  - display setting api
  - display setting backend
  - led settings api
  - led settings backend
  - match status api
  - hide unhide api
  - show on table api
  - display settings permission
  - venue days api
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - Which API loads the Display Setting match list?
  - Which API loads the venues and the event days?
  - Which API saves the LED layout and what does it store?
  - Which API hides a match from the table display?
  - What does the LED settings read return when nothing is saved?
  - Which permission is needed to change the display settings?
  - Where do the live updates on the display screens come from?
backend_sources:
  - gateway/src/routers/match_router.py (match/v1/update_match_status, match/v1/update_led_settings, match/v1/get_led_settings)
  - gateway/src/routers/ott_router.py (ott/v1/get_led_settings, ott/v1/matches)
  - gateway/src/schema/match_schema.py (UpdateLedConfig)
  - tms repository, branch staging: src/router/match_router.py (v1/update_led_settings, v1/get_led_settings)
  - tms repository, branch staging: src/service/match_service.py (update_led_settings, get_led_settings)
source_files:
  - src/app/modules/tms/display-setting/display-setting.component.ts
  - src/app/modules/tms/display-live-card/display-live-card.component.ts
  - src/app/modules/tms/display-setting/display-view-card/display-view-card.component.ts
  - src/app/modules/tms/display-setting/display-overlay/display-overlay.component.ts
  - src/app/core/services/common-service/common-service.service.ts
  - src/app/core/services/day-planner/day-planner.service.ts
  - src/app/core/services/websocket-service/websocket.service.ts
  - src/app/core/constants/api-constant.ts
---
# Backend logic of the Display Setting APIs

The display screens call the **gateway** (`environment.apiUrl`). The gateway forwards the calls to the TMS match service and the OTT service. The match and LED settings routes live in the TMS repository, branch `staging`. The live displays also receive pushed updates on a websocket (`environment.socket_url`).

This guide lists the calls each screen makes and what the backend does with them. The gateway route for `match/v1/matches` was not traced in this guide, so its login and permission rules are not stated here.

## Calls the Display Setting screen makes

| Screen action | Method and path | Notes |
|---|---|---|
| Venues drop-down | GET `event/v1/event_venues` | The event's venues. The first venue is selected. |
| Date strip, month and year | GET `event/v1/get_event_venue_days` | The event days of the chosen venue. |
| Live Matches list | GET `match/v1/matches` | Live filter on, status "in progress", sub matches loaded, paged by offset and limit. |
| All matches list and Tables list | GET `match/v1/matches` | Date, venue and table paging parameters. |
| Export (matches.xlsx, live, tables) | GET `match/v1/matches` | Export flag set; the reply is a file. |
| Hide/Unhide toggle | PATCH `match/v1/update_match_status` with query `show_on_table` | Body: match id, event id, stage id and `show_on_table` as "true" or "false". |
| Read LED settings | GET `ott/v1/get_led_settings` | Query `event_id`. |
| Save LED layout | PUT `match/v1/update_led_settings` | Query `event_id`. Body: event id, config type "LED_SETTING", status "active", layout id. |

## Calls the display pages make

| Page | Method and path | Notes |
|---|---|---|
| LED live card | GET `match/v1/matches` (in progress, table list, categories and point system) | Reloaded on each live update that needs it. |
| LED live card layout | GET `ott/v1/get_led_settings` | Layout 2 is used when no layout is returned. |
| Score card (view and reverse) | GET `match/v1/matches` | Loads by table, match or sub match, in progress. |
| Stream overlay | GET `ott/v1/matches` | In progress, by event, table or match. |
| All display pages | websocket feed | Each page filters the messages by event, table, match or sub match. |

## Matches list (GET match/v1/matches)

- The Live Matches list, the All matches list, the Tables list and the exports all use this route with different parameters.
- An empty result shows "No data found" or the sport's no-data text.

## Venues and days

- `event/v1/event_venues` returns the venues of the event; the screen uses the first one as the default.
- `event/v1/get_event_venue_days` returns the days of a venue. The day list is then grouped by month for the month drop-down and the date strip.

## Hide/Unhide (PATCH match/v1/update_match_status)

- The gateway first loads the event (400 with the event-not-found message when the event is missing) and the match.
- When `show_on_table` is true or false, the gateway updates the match's `show_on_table` value and returns the success message "match updated successfully". This branch returns before the publish, live stream and image update branches are checked.
- The screen does not read the reply and shows no message.

## The is_active variant of the same route

- The common service has a second call on the same route that sends the query `is_active`. The gateway handles `is_active` by updating the match's video stream in the OTT service.
- If the match has no video the gateway returns 404 with the video-not-found message.
- The method exists in the Display Setting component, but no template button calls it.

## Read LED settings (GET ott/v1/get_led_settings)

- The OTT route passes `event_id` to the match service LED read. In the gateway code this route has no login decorator, unlike the match route of the same name.
- The TMS reads the LED_SETTING configuration of the event.
- A saved configuration returns 200 with the message "LED settings fetched successfully" and the stored data (the layout id).
- No saved configuration returns 404 with "LED settings not found". The LED live card then uses layout 2.
- Server errors return 500 with the error text.

## Save LED layout (PUT match/v1/update_led_settings)

- The gateway checks the login and the Display Settings feature in edit mode. It then forwards the event id and the body.
- The TMS reads the existing LED_SETTING configuration of the event.
  - If one exists, it sets `layout__id` from the body when the body has one, and keeps the other stored values.
  - If none exists, it creates the configuration with `layout__id` from the body.
- The configuration is stored as the event's LED setting (object type EVENT, the event id as object id).
- Only the layout id is written. The config type and status in the body are accepted by the gateway, but the TMS keeps only the layout.
- Success: 200 with "LED setting updated". The screen shows this message in a snackbar and then reads the settings again.
- Error: 500 with the error text, shown in the error snackbar.

## Live updates (websocket)

- The Live card, the score card and the overlay each open one websocket subscription at start.
- Each message carries the match data. A message with no data makes the page reload its list.
- A message with a winner ends the match on the page; the page then reloads or removes the match, depending on its address.
- The websocket reconnects after 5 seconds when the connection drops.

## Permissions

- The gateway checks the Display Settings feature in edit mode for the LED save and the match status change. Without it the gateway refuses the change.
- The public display pages (LED live card, score card, overlay) need no login.

## Frequently asked questions

**Which API loads the match list?** GET match/v1/matches through the gateway, with the event, date and status parameters.

**Which API loads the venues and the days?** GET event/v1/event_venues for the venues, and GET event/v1/get_event_venue_days for the days of a venue.

**Which API hides a match from the table display?** PATCH match/v1/update_match_status with the query `show_on_table`. The gateway updates the match and returns "match updated successfully".

**What does the LED settings read return when nothing is saved?** 404 with "LED settings not found". The LED live card then shows layout 2.

**Which permission is needed to change the display settings?** Display Settings in edit mode. Without it the gateway refuses the save and the status change.

**Where do the live updates come from?** A websocket feed; each display page filters the messages it receives.
