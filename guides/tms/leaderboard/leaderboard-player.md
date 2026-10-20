---
doc_id: tms.leaderboard.player
title: Player Leaderboard tab – the player standings, the singles and doubles W/L columns, the top and bottom rules, the player paging and the player search
routes:
  - tms/leaderboard/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
  - tms/leaderboard/:participant_id/:category_id/:event_id
aliases:
  - player leaderboard
  - player standings
  - player points
  - singles wl
  - doubles wl
  - top and bottom
  - top bottom rule
  - player ranking table
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Player Leaderboard?
  - What do the S and D W/L columns mean?
  - What is the difference between Top W/L and Bottom W/L?
  - Why does a player show 0-0?
  - How is the player position worked out?
  - How do I search the player leaderboard?
backend_sources:
  - gateway/src/routers/leadership_points_router.py (leaderboard)
  - tms repository, branch staging: src/router/leadership_points_router.py (leaderboard route)
  - tms repository, branch staging: src/service/leadership_points_service.py (squad roster, leaderboard points)
source_files:
  - src/app/modules/tms/leaderboard/leaderboard.component.html
  - src/app/modules/tms/leaderboard/leaderboard.component.ts
---
# Player Leaderboard tab

The **Player Leaderboard** tab lists the players of the team categories, with their records and their points. Choose it with the **Player Leaderboard** tab in the tab selector. Each stage tab and **ALL** show the players of that stage, or of the whole category.

The tab is paged, and it has the same search box as the other tabs.

## Columns

- **Position** – the rank from the total points. Players with the same total share a position.
- **Player Name** – the player's name.
- **M.A.** or **Club** – the parent of the player, shown when the event's parent role is one of them.
- **Team** – the team the player belongs to. A dash is shown when the player has no team.
- The record columns (see below), then **Points** – the player's total points.

## Record columns

The columns depend on the event's rule setting for the stage:

- **Top and bottom rule** (rule value TOP_AND_BOTTOM): four record columns.
  - **S Top W/L** – singles matches in the top group of the rule (won-lost).
  - **S Bottom W/L** – singles matches in the bottom group.
  - **D Top W/L** – doubles and mixed matches in the top group.
  - **D Bottom W/L** – doubles and mixed matches in the bottom group.
- **Other rules**: two record columns.
  - **S W/L** – singles matches won and lost.
  - **D W/L** – doubles and mixed matches won and lost.

Each cell is written as won-lost, for example "3-1". A cell with no matches shows "0-0".

## What the records count

- The records are the points and results of the player's matches in the leadership points table. The points of each match are added to the player's total.
- A player who is in the squad of a team, but has played no match in the stage, is listed with zero points and "0-0" records.

## Position and ties

- The position is worked out from the total points. Players with equal points share the same position.

## Search and paging

- The search box filters the players by player name or team name. The list reloads from the server after a short pause.
- The table is paged. The page size and the page change reload the rows of that page.

## Empty state

- "Leaderboard data is not available" appears when the player table has no rows.

## Permissions

- Reading the player table needs the login. The table shows the same data to any user who can open the page.

## Frequently asked questions

**What is the Player Leaderboard?** The list of players of the team categories with their singles and doubles records, and their total points.

**What do the S and D W/L columns mean?** Singles (S) and doubles (D) matches, shown as won-lost. Doubles includes mixed doubles.

**What is the difference between Top W/L and Bottom W/L?** When the stage uses the top and bottom rule, the records are split between the top group and the bottom group of the rule.

**Why does a player show 0-0?** The player has no match in that stage or category for that record, so no result counts yet.

**How is the position worked out?** From the total points. Equal points share the same position.

**How do I search the player leaderboard?** Type a player or team name in the Search box.
