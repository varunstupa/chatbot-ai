---
doc_id: tms.display-setting.led-live-card
title: LED live card – the LED display of the matches in progress, its five layouts, card styles, rotation and live updates
routes:
  - tms/display-live-card/:event_id
  - tms/stupa-live-card/:event_id
aliases:
  - led live card
  - live card
  - led display
  - led output screen
  - led layout display
  - display live card
  - stupa live card
  - score card layout display
  - led scoreboard
  - golden match card
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the LED live card?
  - Which layout does the LED card show when none is saved?
  - How many matches fit on one LED screen?
  - How often does the LED card change the matches?
  - Why does the LED card show a dash for the table?
  - What does the LED card show for doubles?
  - What does the G badge on a card mean?
  - Why does a finished match stay on the LED card?
backend_sources:
  - gateway/src/routers/ott_router.py (ott/v1/get_led_settings)
  - gateway/src/routers/match_router.py (match/v1/matches)
  - tms repository, branch staging: src/service/match_service.py (get_led_settings)
source_files:
  - src/app/modules/tms/display-live-card/display-live-card.component.ts
  - src/app/modules/tms/display-live-card/display-live-card.component.html
  - src/app/modules/tms/display-live-card/display-live-card.model.ts
  - src/app/modules/tms/tms.module.ts
---
# LED live card

The **LED live card** is the page the LED boards show. It lists the matches in progress for an event, one card per match (or per in-progress sub match for team matches), and it is what **LED Output** opens from the Display Setting screen. The route is `tms/display-live-card/:event_id`. For sport id 2 (Padel) the address `tms/stupa-live-card/:event_id` is used instead, served by a separate component that this guide does not cover. The page is public and needs no login. The event id comes from the address.

## Layout

- On opening, the page reads the saved LED setting of the event and uses its layout number (1 to 5).
- When no layout is saved, or the read fails, the page uses **layout 2**.
- The number of cards per screen follows the layout: **layout 1 shows 9**, **layout 3 shows 6**, **layout 5 shows 12**, and **layouts 2 and 4 show 4**.
- The layouts are drawn in three card styles: layouts 1 and 5 share one style, layout 3 has its own, layout 2 has its own, and layout 4 is a separate container.

## Which matches appear

- The page loads the matches with status "in progress" for the event, with their tables, sub matches and event categories.
- A team match gives one card for each in-progress sub match.
- Cards are sorted by table number, lowest first.
- The same match on the same table is shown once.
- A card with no table shows a dash in place of the table number.

## Card contents

- **Header**: "TABLE" and the table number, a dash, and the start time (hours and minutes). The round name and the category are shown in the card.
- **Golden match**: the card has a coloured border and a **G** badge in the header.
- **Team score** in the header: for a match on the set point system (and not a golden match) the team's match points; otherwise its sets won.
- **Sides**: the flag and short name of each player or team, and the parent abbreviations (club or member association) by the event's primary and secondary parent roles. For doubles, both players of a side are shown.
- **Scores**: the game score of each side in its score box, and the sets won (for sub matches, computed from the completed sets).
- **Serving indicator**: a marker next to the side that serves, from the match's service data.

## Rotation

- When there are more cards than fit on one screen, the cards are shown in batches.
- The batch changes every **20 seconds**, cycling through the batches.
- A new batch starts at the first batch when the page first loads a list, and keeps its place when the list refreshes.

## Updates

- The page loads the list when it opens, and again whenever a live update arrives on the server connection.
- A live update for a match updates its card in place. When the update is for a new in-progress match, or a match that is not yet on the screen, the list is reloaded.
- When a match finishes (it has a winner), its card is removed when the list reloads. A finished match stays on its table's card until a new live match appears on that table, so the table is not left empty.
- Only one list load runs at a time. A load requested during a load runs once more afterwards.

## Permissions

- The page is public. It needs no login and no feature permission.
- The layout is changed on the Display Setting screen, which needs the Display Settings edit permission.

## Messages

- The page shows no error message. When a load fails, the cards stay as they were.
- With no match in progress the card area is empty.

## Frequently asked questions

**What is the LED live card?** The LED board page with the matches in progress. LED Output opens it.

**Which layout does it show when none is saved?** Layout 2, which has four cards.

**How many matches fit on one screen?** Nine for layout 1, six for layout 3, twelve for layout 5 and four for layouts 2 and 4. More matches rotate in batches every 20 seconds.

**Why does a card show a dash for the table?** The match is not yet on a table, so no table number is known.

**What does the G badge mean?** The match is a golden match of the event, and its card has a coloured border.

**Why does a finished match stay on the screen?** Its table keeps the last card until a new live match appears on that table.

**How do I change the layout?** Open LED Settings on the Display Setting screen, click a layout, then click Save. Reload the LED card to see it.

**How often does the LED card change the matches?** When there are more matches than fit on one screen, the cards are shown in batches and the batch changes every 20 seconds.

**What does the LED card show for doubles?** Both players of each side are shown, with their flags, short names and club or member association.
