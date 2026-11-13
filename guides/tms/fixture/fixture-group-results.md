---
doc_id: tms.fixture.group-results
title: Group stage matches, standings and matrix view
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - group matches
  - group standings
  - matches standings
  - matrix view
  - group matrix
  - all rounds
  - tie details
  - set point system groups
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - Where do I see the matches of a group?
  - How do I filter the group matches by table or time?
  - What is the matrix view?
  - How do I see the tie details?
  - Why are my group matches not listed?
  - How do I enter a score in a group match?
backend_sources:
  - gateway/src/routers/group_router.py (get_group_matches)
  - gateway/src/routers/match_router.py (update_matches)
  - gateway/src/routers/scoring_router.py (update_score)
source_files:
  - src/app/modules/tms/fixture-configuration/groups-stage-view/matches-standings/groups-stage-matches-standings.component.html
  - src/app/shared/group-match-accordian/group-match-accordian.component.html
  - src/app/modules/tms/group-matrix-view/group-matrix-view.component.html
  - src/app/modules/tms/fixture-configuration/fixture-configuration.component.ts (grid views, replace and swap rules)
---
# Group stage matches, standings and matrix view

Once the group fixture is created, the **Matches and standings** part of the group stage shows the matches of each group, the standings, and the results grid (matrix). Scores are entered on the match row; the scoring guide covers the scoring rules.

## Group matches and standings: tabs and search

- Shown once the group matches are made (the stage is in **Final Edit**).
- Tabs: **All groups** (the standings of each group), **All matches** (the matches) and, for league events only, **All Rounds** (the matches listed by round).
- **Search participants** finds a player or a group in the open tab.
- On **All matches**, the view dropdown switches between **Table View** (the match list of each group) and **Standard View** (the matrix grid). **Table View** is the default.
- When filters are shown on **All groups**, the **Filters** box offers **Associatons**, **Clubs**, **Times**, **Name**, **Table** and **Dates**.
- When there are no groups, **No record found** is shown; create the groups first (see the group stage guide).

## Group standings table (All groups tab)

- Each group is a panel showing its number of **Participants**. Expand it to see the standings.
- Columns: **Flag**, **Back No.** (singles), **License ID** (not for teams), **Seeding**, **Participant name**, **Member Association** and **Club** (when the category uses them), **Match W/L**, **Sub Match W/L** (team categories only), **Game W/L**, **Score W/L** (not shown for Padel), **Points**, **Position** and **Qualifier**.
- Doubles and mixed doubles show both players of a pair. A forfeited player shows the forfeit mark and "(forfeited)".
- Row actions (when allowed): the swap icon opens the swap popup; the replace icon opens **Replace participant** (singles, doubles and mixed only, first stage only, not for a sample fixture, and not once all matches are completed).
- **Tie Details** in an expanded group shows how ties between players on equal standing were decided.

## Group match list (All matches tab, Table View)

- Each group is a panel that opens to show its matches. In league events a checkbox selects groups and matches.
- The columns: the two players, the table and time (for scheduled matches, depending on how they were scheduled), the score, and the status.
- A golden match is marked with an icon.
- A forfeited player is marked with a red "Forfeited Player" icon.
- For a sport with sets, the score shows the set points of each set; otherwise it shows the total score.
- Round-wise view: when the matches are listed by round, the **Round** column appears.

## Group matrix view (All matches tab, Standard View)

- Choose **Standard View** in the view dropdown of **All matches**.
- A grid with one row and one column per player of the group; each cell is the result of that pair.
- Double round robin groups show two rows per pair (one per meeting).
- A player's flag or logo is shown when the organisation has flags on.
- A walkover shows "walk over" or "double walk over" in the cell.
- For court sports the set scores are shown per cell; a set point value is shown where the set points are set.
- Click a cell's score to open the match's sets (filtered by match).
- Print view: the matrix has its own print header.

## Group standings: ranking order

- The standings order the players by the points and tie-breakers set in the rule settings (for example head-to-head: "Only matches between the tied players or teams are compared").

## Group matches and standings: messages

- A score that cannot be saved shows the message from the server (see the scoring guide).

## Group matches and standings: permissions

- Entering or changing scores needs the scoring permission (see the scoring guide).

## Frequently asked questions about group matches and standings

**Where do I see the matches of a group?** Open the **All matches** tab and expand the group panel. The standings are on **All groups**.

**How do I see the results grid?** On **All matches**, choose **Standard View** in the view dropdown.

**What is the matrix view?** A grid of every pair in the group with the result of each meeting.

**How do I see the tie details?** On **All groups**, expand the group and click **Tie Details**.

**How do I filter the group matches by table or time?** On the **All groups** tab, when filters are shown, the **Filters** box offers **Table**, **Times** and **Dates**, plus **Associatons**, **Clubs** and **Name**.

**Why are my group matches not listed?** The groups are not created yet, or the filters hide them. Clear the filters, or create the groups first.

**How do I enter a score in a group match?** Use the match row's action, or the score cell; see the scoring guide.
