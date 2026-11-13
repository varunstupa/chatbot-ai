---
doc_id: tms.leaderboard.team
title: Team Leaderboard tab – the team standings table, the group and match views, View Details, Compare with Other Teams and Match Details
routes:
  - tms/leaderboard/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
  - tms/leaderboard/:participant_id/:category_id/:event_id
aliases:
  - team leaderboard
  - team standings
  - team table
  - team view details
  - compare with other teams
  - match details leaderboard
  - team stats
  - group standings
  - all groups
  - all rounds
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What columns are in the team leaderboard?
  - What do TM, W, T, L, G, SM, Set and Pts mean?
  - What does the G column mean?
  - How do I see a team's details?
  - What does Compare with Other Teams show?
  - How do I see the matches of a team?
  - What are All groups, All matches and All Rounds?
  - Why is there no team table on a knockout stage?
backend_sources:
  - gateway/src/routers/leadership_points_router.py (group-participants, leaderboard)
  - gateway/src/routers/match_router.py (match/v1/matches, leaderboard-ranking)
  - gateway/src/routers/group_router.py (get_groups, get_group_matches)
  - tms repository, branch staging: src/router/leadership_points_router.py
  - tms repository, branch staging: src/service/match_service.py (get_event_category_leaderboard)
source_files:
  - src/app/modules/tms/leaderboard/leaderboard.component.ts
  - src/app/modules/tms/leaderboard/leaderboard.component.html
  - src/app/modules/tms/leaderboard/leaderboard.component.scss
---
# Team Leaderboard tab

The **Team Leaderboard** tab (the default tab) ranks the teams of the chosen category. What it shows depends on the stage tab:

- **ALL** (final standing): one table of the whole category, ranked from the matches of all group (round robin) stages with the **Winner Logic**. Every team drawn into the fixture is listed from fixture generation, with zero records until it plays. Knockout stages and sample fixtures are not counted, so a knockout-only category has an empty table.
- **A stage** (S1, S2 ...): the standings of that stage, with the group, match and round views under it.
- **A knockout stage**: no table; the bracket is shown instead.

## Standings table

- Columns: **Position**, **Team Name**, **M.A.** or **Club** (only when the event's parent role is one of them), **TM**, **W**, **T**, **L**, **G** (only when the category has golden matches), **SM**, **Set**, **Pts**, and the action icons.
- **TM** – total matches. **W**, **T** and **L** – won, tied and lost matches.
- **G** – golden matches. The column is shown only when the category has them.
- **SM** – sub match record (won-lost of the team's sub matches). **Set** – set record. **Pts** – points.
- Each column header has a tooltip: TM "Total Matches", W "Won", T "Tied", L "Lost", G "Golden Match", SM "Sub Match W/L", Set "Set W/L".
- Each row has two icons at the end: the **edit** icon opens **View Details** for the team, and the **stats** icon opens the team stats view (see below).
- "Leaderboard data is not available" appears when the table has no rows.

## View Details (team sidebar)

- The sidebar opens from the edit icon and is titled **View Details**.
- The team name is shown at the top. The stats grid shows **Total Matches**, **Win**, **Lost**, **Tie**, **Matches W/L**, **Game W/L** (sets), **Balls** (points won-lost), **Club** (always "--" here), **Points** and **Golden Points** (golden matches won).
- **Total Members (n)** with the headers **Members**, **Participant Type** (shown as "Single"), **Club** and **Country**.
- The sidebar is read-only. Close it with the **X** at the top.

## Team stats view, Compare with Other Teams and Match Details

- The stats icon replaces the table with the team stats view. **Back** returns to the standings.
- The top table lists the team's players: **Player Name**, **Participant Type**, **M.A.** or **Club**, **Country**, the S and D W/L columns (as on the Player Leaderboard) and **Points**.
- **Compare with Other Teams** lists the team's matches against the others with the columns **S No.**, **Team A**, **Team B**, **Date & Time** ("--" when not scheduled), **Venue**, **Score** (sets won) and **Match Guide**.
- Each row has **Match Details**, which opens a dialog with the team match: the two teams, each sub match with its players, the sets won and the points of each set. A missing player name shows the placeholder "Player 1" (or "Player 1A" for the second pair).
- "Leaderboard data is not available" appears when no comparison rows exist.

## Group and match views (not the knockout stage)

- Toggles appear for a stage that is not a knockout (**All Rounds** only for league events):
  - **All groups** – one panel for each group. Opening a panel shows its teams with the columns **Flag**, **Back No.** (single events), **License ID** (other types), **Participant name**, **M.A.** or **Club**, **Match W/L**, **Sub Match W/L** (team events), **Game W/L**, **Score W/L**, **Points**, **Position** and **Qualifier**.
  - **All matches** – the group matches, with the sets and points of each match.
  - **All Rounds** (league events only) – the matches grouped by round.
  - Each group panel header shows the group name and its number of participants. An empty list shows "No record found".
- The search box filters these groups and matches by team or player name.
- The group and round tables are read-only here. The page sets the checkbox and action columns off, so there are no score-edit, swap or move-round icons. A golden match has a golden icon, and a forfeited player is marked.
- Column headers follow the flags the page sets: group-wise views show **Organisers**, round-wise views show **Table** and **Game Score**; a license ID column appears for non-team categories.

## Knockout stage

- A knockout stage (format 2) shows the bracket with its rounds, times, tables and scores instead of the standings table.
- The bracket is read-only here. It is drawn with the edit controls turned off, so there are no checkboxes, no edit icons and no score entry.
- The bracket's navigate-to-positions action has no handler on this page, so it does nothing here.

## Golden matches

- A **G** column and a golden-match marker in the match views appear when the category has golden matches.
- The **Match Details** dialog shows a second list of golden sub matches when the match has a golden match.

## Permissions

- Reading the team tables and opening the winner logic sidebar need only the login. Saving the winner logic needs the Display Settings permission in edit mode.

## Frequently asked questions

**What columns are in the team leaderboard?** Position, team name, M.A. or club, TM, W, T, L, G (golden, when present), SM, Set and Pts.

**What do TM, W, T and L mean?** Total matches, won, tied and lost.

**What does the G column mean?** The golden-match record. It is shown only when the category has golden matches.

**How do I see a team's details?** Click the edit icon on its row to open View Details, or the stats icon for its players and matches.

**Why is there no All Rounds toggle?** It is shown only for league events.

**What does Compare with Other Teams show?** The team's matches against other teams, with a Match Details button for each.

**What are All groups, All matches and All Rounds?** Three views of a group stage: the group tables, the group matches, and the matches by round.

**Why is there no team table on a knockout stage?** A knockout stage shows the bracket instead of standings.

**How do I see the matches of a team?** Click the team's stats icon. **Compare with Other Teams** lists its matches against the others. Click **Match Details** on a row to see each sub match with its players, sets and points.
