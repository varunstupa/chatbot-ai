---
doc_id: tms.display-setting.stream-overlay
title: Stream overlay – the on-screen match graphic for a live stream, by match, sub match or table, with scores, cards, timeouts and the golden match label
routes:
  - tms/stream/match/:event_id/:match_id/:sub_match_id
  - tms/stream/match/:event_id/:match_id
  - tms/stream/table/:event_id/:table_id
aliases:
  - stream overlay
  - overlay
  - live overlay
  - broadcast overlay
  - streaming overlay
  - stream match overlay
  - stream table overlay
  - golden match overlay
  - ttfi overlay
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the stream overlay?
  - Which URL gives the overlay of one match?
  - Which URL gives the overlay of a table?
  - Which URL gives the overlay of one sub match?
  - What does Golden mean on the overlay?
  - Why does the overlay show nothing?
  - What happens to the overlay when a match finishes?
  - Why do the overlay names have different widths?
backend_sources:
  - gateway/src/routers/ott_router.py (ott/v1/matches, cached 30 seconds, no login decorator)
  - tms repository, branch staging: src/router/match_router.py (matches list)
source_files:
  - src/app/modules/tms/display-setting/display-overlay/display-overlay.component.ts
  - src/app/modules/tms/display-setting/display-overlay/display-overlay.component.html
  - src/app/app.routes.ts
  - src/app/core/services/common-service/common-service.service.ts
---
# Stream overlay

The **stream overlay** is the match graphic a broadcaster puts over a live video. It shows the score, the names, the games or sets won, the points of the current game, the cards and timeouts, and the round. It follows the match in progress, and it is the page the streaming links point to. The page is public and needs no login.

## Addresses

- `/stream/match/:event_id/:match_id/:sub_match_id` shows one sub match of a team match.
- `/stream/match/:event_id/:match_id` shows one match.
- `/stream/table/:event_id/:table_id` shows whatever match is in progress on that table, and follows it as matches change.
- The event id comes from the address.

## What the overlay shows

- **Header** (non-TTFI tenants): the category description and the start time (hours and minutes with am or pm). A match that is a golden match shows the **Golden** label in the header.
- **Round** name of the match.
- **Two sides**: the country flag and the short country abbreviation, or the player names with the parent abbreviations. Parent abbreviations are cut to five characters in the header and seven elsewhere.
- **Score**: the current game score and the games or sets won by each side, plus the points of previous games.
- **Team matches**: the number of sub matches each team has won (for the team sub match count) and the sub match in progress.
- **Cards and timeouts**: the same marks as the score card (yellow and red cards, and timeout marks).
- **Serving indicator** on the side that serves.

## Header design for the TTFI tenant

- For the tenant named `ttfi`, a different header is used, with a red middle section.
- That tenant shows the overlay only when a match is in progress; with no match nothing is drawn, not even the placeholder.
- For all other tenants, with no match in progress, a blank placeholder of the header and two sides is drawn.

## Which match is drawn

- **Match address**: the match with that id. When it finishes (its live data has a winner), the overlay is cleared and stays empty.
- **Sub match address**: the one sub match. A sub match with status SCORED is not drawn; when it finishes the overlay is cleared.
- **Table address**: the sub match of a team match that is in progress on the table, or the single match in progress on the table. A finished match is removed. A new match on the table replaces the old one when no match is shown.

## Updates

- The overlay loads the live matches for its address when it opens.
- It then updates on each live update from the server connection. For a match or sub match address, only updates of that match are used. For a table address, only updates of matches on that table are used.
- When an update arrives with no data, the overlay reloads the list.
- The width of the name area is measured from the longest short name and cached, so the layout does not jump between updates.

## Scoreboard width

- The scoreboard is 29 times the viewport width by default.
- It is 36 times for a team match, and 34 for doubles or mixed doubles, when a side has two or more parents.

## Permissions

- The page is public and needs no login.
- The live matches come from the OTT matches route of the gateway (`ott/v1/matches`). That route has a 30-second cache and no login decorator in the gateway code.

## Messages

- The overlay shows no error message. When the list cannot be loaded, the overlay keeps its previous state.

## Frequently asked questions

**What is the stream overlay?** A match graphic for a live video, with the score, names, round and cards, updated while the match is played.

**Which URL gives the overlay of one match?** `/stream/match/:event_id/:match_id`. Add the sub match id for one sub match of a team match.

**Which URL gives the overlay of a table?** `/stream/table/:event_id/:table_id`. It follows the match in progress on that table.

**What does Golden mean on the overlay?** The match is a golden match of the event, and its header shows the Golden label.

**Why does the overlay show nothing?** No match is in progress for that event, match or table. On the TTFI tenant the overlay draws nothing until a match is in progress.

**What happens when a match finishes?** On a match or table address the match is removed. On a match address the overlay is cleared and stays empty.

**Why do the names have different widths?** The overlay measures the longest name of the match and uses that width for the name area.
