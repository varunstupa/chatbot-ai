---
doc_id: tms.leaderboard.winner-logic
title: Winner Logic sidebar – how the leaderboard breaks ties, the comparison method, the basis for each criterion, defaults by event type and saving
routes:
  - tms/leaderboard/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
  - tms/leaderboard/:participant_id/:category_id/:event_id
aliases:
  - winner logic
  - leaderboard winner logic
  - tie break
  - tiebreaker
  - tie breaker leaderboard
  - head to head
  - compare with all
  - win loss ratio
  - winner basis
  - final position order
  - leaderboard ranking rule
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Winner Logic on the Leaderboard?
  - What is the difference between Head-to-Head and Compare with All?
  - What do Won, Win/Loss Ratio and Win-Loss mean?
  - How are ties broken on the leaderboard?
  - What is the default for a league and for a tournament?
  - Why is Sub Match or Game not counted?
  - How do I save the winner logic?
  - Which permission do I need to change the winner logic?
backend_sources:
  - gateway/src/routers/match_router.py (get and update leaderboard winner logic)
  - tms repository, branch staging: src/router/match_router.py (winner logic routes)
  - tms repository, branch staging: src/service/match_service.py (update, get and resolve leaderboard settings)
  - tms repository, branch staging: src/utils/winner_logic_defaults.py (default ladder)
  - tms repository, branch staging: src/common/enums.py (ComparisonMethod)
source_files:
  - src/app/modules/tms/leaderboard/leaderboard.component.html
  - src/app/modules/tms/leaderboard/leaderboard.component.ts
  - src/app/modules/tms/leaderboard/leaderboard-winner-logic-defaults.ts
---
# Winner Logic sidebar

The **Winner Logic** sidebar sets how the leaderboard orders teams and players when their points are level. It is opened with the **Winner logic** button on the Leaderboard screen (the button with the recalculate icon, next to the search box). The sidebar has two parts: the **comparison method** and the **winner basis** for each criterion.

## Winner Comparison

- **Head-to-Head** – teams that are level on points are compared with each other only, using the results between them.
- **Compare with All** – teams that are level on points are compared with all the other teams in the group or category.
- Leagues use Compare with All by default; tournaments use Head-to-Head.

## Winner Basis (For Final Position)

Five criteria are listed in this order. Each can be switched on or off with its checkbox:

1. **Points** – the total points. It has no basis options.
2. **Match** – the match record. Options: **Won**, **Win/Loss Ratio** and **Win-Loss**.
3. **Sub Match** – the sub match record. The same three options.
4. **Game** – the game record. The same three options.
5. **Score** – the point score record. The same three options.

- **Won** counts the wins of the criterion.
- **Win/Loss Ratio** compares the wins with the losses as a ratio. A record with wins and no losses ranks above every ratio. A record of no matches counts as 0.
- **Win-Loss** compares the difference between wins and losses.
- For Match and Sub Match these are match and sub match records. For **Game** the records are sets won and lost, and for **Score** they are points won and lost.

When a criterion is switched off, its basis options are cleared and it is not used for ties.

## Defaults

- Leagues (event types L and BL): Compare with All, and Win-Loss as the basis.
- Other events: Head-to-Head, and Win/Loss Ratio as the basis.
- All five criteria start switched on in the form.
- A criterion that is saved as off stays off when the sidebar opens again.

## Saving

- **Update** saves the comparison method and the five criteria, then closes the sidebar and reloads the standings.
- The saved values apply to the category, not to a single stage.
- A failed save shows the server message in the error snackbar.

## What the saved logic does

- The saved criteria are used when the final standing is worked out. Teams are grouped by total points first. Inside a group of equal points, the enabled criteria break the tie in their saved order (Points is not used for this). With Head-to-Head the tied teams are compared with each other first; with Compare with All they are compared with the whole field.
- Changing the logic changes the standing order on the next load. It does not change any match result.

## Permissions

- Opening the sidebar needs the login.
- **Update** needs the Display Settings permission in edit mode. Without it the server refuses the save.

## Frequently asked questions

**What is the Winner Logic on the Leaderboard?** The rule that orders teams and players when their points are level.

**What is the difference between Head-to-Head and Compare with All?** Head-to-Head compares only the tied teams with each other. Compare with All compares them with every team in the category.

**What do Won, Win/Loss Ratio and Win-Loss mean?** They are the three ways to measure a record: the number of wins, wins divided by losses, and wins minus losses.

**How are ties broken on the leaderboard?** By the comparison method and the enabled criteria, in the order Points, Match, Sub Match, Game, Score.

**What is the default for a league and for a tournament?** League: Compare with All and Win-Loss. Tournament: Head-to-Head and Win/Loss Ratio.

**Why is Sub Match or Game not counted?** Its toggle is off in the saved logic.

**How do I save the winner logic?** Make the changes, then click **Update**.

**Which permission do I need?** Display Settings in edit mode.
