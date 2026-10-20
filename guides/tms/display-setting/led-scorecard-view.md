---
doc_id: tms.display-setting.scorecard-view
title: Score card view – the full-screen match or table scorecard, the reverse card, side order, timers, cards and live updates
routes:
  - tms/display-view-card
  - tms/:type/:event_id/:table_id
  - tms/:type/:event_id/:table_id/:sub_match_id
  - tms/:type/:event_id/:table_id/reverse
  - tms/:type/:event_id/:table_id/:sub_match_id/reverse
aliases:
  - display view card
  - view card
  - score card
  - scorecard display
  - reverse score card
  - reverse view card
  - match scorecard
  - table scorecard
  - game interval timer
  - player timeout display
  - previous game score
  - yellow card display
  - red card display
  - side toggle scorecard
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the display view card?
  - What is the difference between the view card and the reverse card?
  - What decides which side is on the left of the scorecard?
  - What does the timer on the score card show?
  - Which URL shows the scorecard of one table?
  - Why does the score card not update?
  - What is shown as Previous Game Score?
  - What do the yellow and red marks on a player mean?
backend_sources:
  - gateway/src/routers/match_router.py (match/v1/matches)
  - tms repository, branch staging: src/service/match_service.py (matches list)
source_files:
  - src/app/modules/tms/display-setting/display-view-card/display-view-card.component.ts
  - src/app/modules/tms/display-setting/display-view-card/display-view-card.component.html
  - src/app/modules/tms/display-setting/display-view-card-reverse/display-view-card-reverse.component.ts
  - src/app/modules/tms/display-setting/display-view-card-reverse/display-view-card-reverse.component.html
  - src/app/app.routes.ts
  - src/app/modules/tms/tms.module.ts
---
# Score card view

The **score card view** is a full-screen scorecard for one match, one sub match or one table. It is a display source for LED boards and public screens. It shows the names, the score, the games already finished, cards and timeouts, and a countdown timer. The page is public and needs no login.

There are two components with the same code: the **view card** and the **reverse card**. Their scripts are identical. The reverse card's template swaps the scoreboard blocks, so the same match is drawn mirrored.

## Addresses

- `/tms/display-view-card` is the page in the admin tree. With no match in the address it shows nothing.
- `/table/:event_id/:table_id` shows the match in progress on that table. Clicking **Link** for a table on the Display Setting screen opens this for sport ids other than 2.
- `/:type/:event_id/:table_id/:sub_match_id` shows one sub match of a team match.
- Adding `/reverse` at the end shows the reverse card. The reverse routes are matched first for those addresses.
- `/stream/match/...` and `/stream/table/...` are the stream overlay, not this card.

## Which match is shown

- For a **table** address, the card shows the match in progress on that table. For a team match it picks the sub match playing on that table.
- For a **match** address, the card shows that match. For a team match with a sub match id, it shows that sub match. Without one it shows the sub match that is live, else the one in progress, else the highest order.

## Side order

- Each match has a **switchSide** flag, derived from the live data: the card compares the participant on the left (`participantLeft`) with the two participants of the match. The first participant gives no toggle; the second gives a toggle.
- The view card shows the scoreboard blocks when the flag is off, and the reverse card shows them when it is on. The reverse card is used when the sides of a match should be mirrored on the display.

## Header and sides

- The header shows the category, the round and the start time, with the label **Start time** when that timer is running.
- For a team match the header shows the team names and the team score.
- Each side shows its player or team names in short form, and the parent abbreviations and flags.
- Templates change with the number of parents of a side: one parent, two or fewer, or more than two.

## Score area

- The current game score of each side is shown big.
- **Previous Game Score** lists the points of each game already finished, one column per game, for each side.
- For a team match, each sub match shows the sets or games won of its two sides.

## Cards and timeouts on a player

- Each side has a jersey in its colour, taken from the live data (a default colour is used when it is missing).
- A **yellow card** mark shows when the side has one or more yellow cards.
- A **red card** mark shows for one red card; two red cards show a second mark.
- A **T** mark shows when the side has taken a timeout (the timeout count is above zero).

## Timers

- The timer has three modes, each with its own label: **Game interval** (the break between games), **Player Timeout** (a timeout called by a player) and **Start time** (the countdown before the match).
- A timer starts when the live data changes a timeout or start flag from off to on. It starts from the configured length of that timeout.
- When the timer reaches zero it stops and shows 00:00.
- A new timer replaces a running one.

## Updates

- The card loads the match when it opens.
- For a table address, a live update is used only when it belongs to that table. For a sub match address, only updates of that sub match are used. For a match address, only updates of that match are used.
- A match that has a winner is removed from the card, and the card then loads the next match on the table.
- When an update arrives with no data, the card reloads from the server.
- The card stays on screen between updates; a card whose match no longer matches the address is not drawn.

## Permissions

- The page is public. It needs no login.

## Messages

- The page shows no error message. When the match cannot be loaded, the card stays empty.

## Frequently asked questions

**What is the display view card?** A full-screen scorecard for one match, sub match or table, used for LED and public screens.

**What is the difference between the view card and the reverse card?** The same data and code. The reverse card mirrors the sides, based on the match switchSide value.

**What decides which side is on the left?** The live data's participantLeft value, compared with the two participants of the match.

**What does the timer show?** The game interval, a player timeout or the start-time countdown, from the live data.

**Which URL shows the scorecard of one table?** `/table/:event_id/:table_id`. For sport id 2 the table link goes to the umpire view instead.

**Why does the score card not update?** The card needs a live connection to the server. Reload the page to load the match again.

**What is shown as Previous Game Score?** The points of each game already finished in the match, for each side.

**What do the yellow and red marks mean?** A yellow mark means the side has a yellow card; red marks show red cards.
