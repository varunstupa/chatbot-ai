---
doc_id: tms.leaderboard
title: Leaderboard screen – team and player standings, final standing, stage view, category and stage selection, search, paging and the empty states
routes:
  - tms/leaderboard/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
  - tms/leaderboard/:participant_id/:category_id/:event_id
aliases:
  - leaderboard
  - leaderboard page
  - leaderboard screen
  - team leaderboard
  - player leaderboard
  - standings
  - final standing
  - stage standing
  - league table
  - tms leaderboard
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Leaderboard screen for?
  - What is the difference between Team Leaderboard and Player Leaderboard?
  - What does the ALL button do?
  - How do I choose a category and a stage on the Leaderboard?
  - Why does the Leaderboard show no data?
  - Which categories appear on the Leaderboard?
  - How do I search the leaderboard?
backend_sources:
  - gateway/src/routers/match_router.py (leaderboard-ranking, winner logic routes)
  - gateway/src/routers/leadership_points_router.py (leaderboard, group participants)
  - tms repository, branch staging: src/router/leadership_points_router.py
  - tms repository, branch staging: src/service/match_service.py (get_event_category_leaderboard, winner logic)
source_files:
  - src/app/modules/tms/leaderboard/leaderboard.component.ts
  - src/app/modules/tms/leaderboard/leaderboard.component.html
  - src/app/modules/tms/leaderboard/leaderboard-winner-logic-defaults.ts
  - src/app/modules/tms/tms.module.ts
---
# Leaderboard screen

The **Leaderboard** screen (routes `tms/leaderboard/:participant_id/:category_id/:event_id/:event_category_id/:stage_id` and `tms/leaderboard/:participant_id/:category_id/:event_id`) shows the standings of the team categories of an event. It has two tabs: **Team Leaderboard** and **Player Leaderboard**. It also gives the match results and the group or round views of each stage.

The event id comes from the last segment of the address, like the other TMS screens. With no valid event the page shows the "no event selected" state and makes no event calls.

The address's participant segment is replaced by the team type (2) when the page starts. Categories shown are therefore team categories only.

## Where to find it

Open **Leaderboard** from the sidebar. It shows only when your organisation has the leaderboard turned on for the event type.

## Layout

- **Category row**: the categories of the event as tabs. A category with sub categories shows its children in a second row. Use the arrows at each end to scroll.
- **Stage row**: the stages of the chosen category, labelled **S1**, **S2** and so on with the stage name. The first option, **ALL**, shows the final standing of the whole category.
- **Tab selector**: **Team Leaderboard** and **Player Leaderboard**.
- **Search** box and the **Winner logic** button (the button with the recalculate icon) on the top row.
- The content below depends on the tab, the stage and the format of the stage (see the team and player guides).

## Choosing a stage

- Clicking a stage tab loads its participants, its matches and its groups or bracket.
- Clicking **ALL** shows the final standing of the category, built from the group matches of all stages.
- A knockout stage (format 2) shows the bracket instead of a standings table.
- The address is updated with the chosen category and stage, so a reload opens the same view.

## Search

- Typing in **Search** filters the rows by team or player name. The search waits about 400 ms after the last key press, then reloads the rows from the server.
- Switching tabs clears the search box.

## Paging

- The team and player tables are paged. The page sizes offered are 10, 20, 30, 40, 50 and 100.
- A page change reloads the rows of that page from the server.

## Empty and loading states

- **No event selected**: the page shows the no-event state and makes no calls.
- **No category**: the page shows the no-category state (add categories to the event first).
- **"Leaderboard data is not available"** is shown under the team, player, stage and compare tables when they have no rows. The group list shows "No record found" when it is empty.
- The no-event state title is "No record found" (the shared empty-state text).
- While data loads, a loader is shown over the page.

## Messages

- Snackbars for an error use the server's own message when it has one; otherwise "Something went wrong" is shown as a toast.
- Winner logic: a successful save closes the sidebar and reloads the standings.

## Permissions

- The page needs the login. Reading the standings needs no extra permission.
- Saving the winner logic needs the Display Settings permission in edit mode. The gateway refuses the change without it.

## Frequently asked questions

**What is the Leaderboard screen for?** Showing the team and player standings of each team category, and the match results behind them.

**What is the difference between Team Leaderboard and Player Leaderboard?** The team tab ranks teams (or the entries of the category). The player tab ranks the players, with their match and game records.

**What does the ALL button do?** It shows the final standing of the whole category, combining all group stages.

**How do I choose a category and a stage?** Click the category tab, then the stage tab. Use the arrows to scroll when there are many.

**Why does the Leaderboard show no data?** Check that the event is selected, the category has rounds and results, and the stage has participants. Without group matches the final standing is empty.

**Which categories appear?** Only team categories. Singles and doubles categories are not listed on this page.

**How do I search?** Type a team or player name in the Search box; the list updates after a short pause.

**Which categories appear on the Leaderboard?** Only team categories. Singles and doubles categories are not listed on the Leaderboard.
