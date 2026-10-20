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
---
# Group stage matches, standings and matrix view

Once the group fixture is created, the **Matches and standings** part of the group stage shows the matches of each group, the standings, and the results grid (matrix). Scores are entered on the match row; the scoring guide covers the scoring rules.

## Matches and standings

- **Search participants** finds a player or a group.
- The **grid view** dropdown togglees between the list views. Choose the view that suits the screen.
- Filters (shown for groups): **Associations**, **Clubs**, **Times**, **Name**, **Table** and **Dates**. Each filter narrows the matches shown.
- For league events the **All Rounds** tab shows the matches of every round.
- The columns follow the event: **Seed** (when display seeding is on), **Participant**, **Member Association** and **Club** (as set in Settings), **Action** (the row actions, shown when you may change the match), and the forfeit mark.
- Doubles and mixed doubles show both players of a pair; teams show the team.
- For **Padel** one column is hidden.
- **Tie details** (the button in the header) shows how the ties of the group were decided.
- When there are no groups yet, the list is empty; create the groups first (see the group stage guide).

## Group match list (accordion)

- Each group is a panel that opens to show its matches. In league events a checkbox selects groups and matches.
- The columns: the two players, the table and time (for scheduled matches, depending on how they were scheduled), the score, and the status.
- A golden match is marked with an icon.
- A forfeited player is marked with a red "Forfeited Player" icon.
- For a sport with sets, the score shows the set points of each set; otherwise it shows the total score.
- Round-wise view: when the matches are listed by round, the **Round** column appears.

## Matrix view

- A grid with one row and one column per player of the group; each cell is the result of that pair.
- Double round robin groups show two rows per pair (one per meeting).
- A player's flag or logo is shown when the organisation has flags on.
- A walkover shows "walk over" or "double walk over" in the cell.
- For court sports the set scores are shown per cell; a set point value is shown where the set points are set.
- Click a cell's score to open the match's sets (filtered by match).
- Print view: the matrix has its own print header.

## Results, standings and ranking

- The standings order the players by the points and tie-breakers set in the rule settings (for example head-to-head: "Only matches between the tied players or teams are compared").

## Messages

- A score that cannot be saved shows the message from the server (see the scoring guide).

## Permissions

- Entering or changing scores needs the scoring permission (see the scoring guide).

## Frequently asked questions about group matches and standings

**Where do I see the matches of a group?** In the accordion; open the group panel.

**How do I filter the group matches by table or time?** Use the **Table** and **Times** filters above the list.

**What is the matrix view?** A grid of every pair in the group with the result of each meeting.

**How do I see the tie details?** Click **Tie details** in the header of the group.

**Why are my group matches not listed?** The groups are not created yet, or the filters hide them. Clear the filters, or create the groups first.

**How do I enter a score in a group match?** Use the match row's action, or the score cell; see the scoring guide.
