---
doc_id: tms.printing.badminton
title: Printing for Badminton – the Badminton score sheet, rally boxes, games and team sheets
routes:
  - tms/printing/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
sports: [badminton]
aliases:
  - badminton print
  - badminton score sheet
  - badminton sheet
  - badminton day wise sheet
  - badminton rally boxes
  - badminton games sheet
  - badminton printing
  - badminton toss sheet
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How is a Badminton score sheet printed?
  - What are the rally boxes on the Badminton sheet?
  - How many games are on a blank Badminton sheet?
  - What does the Result column show on the Badminton sheet?
  - Why does the Badminton sheet look different from other sports?
  - How are the team logos printed on the Badminton sheet?
backend_sources:
  - gateway/src/routers/print_router.py (get_print_settings)
  - gateway/src/routers/playing_order_router.py (get_team_playing_order_with_matches)
  - tms/src/router/print_router.py
  - tms/src/service/print_service.py
source_files:
  - src/app/modules/tms/day-wise-print/daywise-badminton/daywise-badminton.component.html
  - src/app/modules/tms/day-wise-print/daywise-badminton/daywise-badminton.component.ts
  - src/app/modules/tms/printing/printing.component.html
  - src/app/modules/tms/printing/printing.component.ts
---
# Printing for Badminton

This guide applies to events whose sport is **Badminton** (sport ID 4). Badminton has its own score sheet, the **daywise Badminton sheet**, which the Printing page uses in place of the standard day-wise sheet. The other sheets (fixtures, schedule, back numbers and players list) are the same as for the other sports. The Printing guide and the printed sheets guide describe the common parts.

## Which sheet is printed

- For a Badminton event the Printing page switches the day-wise score sheet and the score sheet to the Badminton layout.
- The Badminton layout is chosen from the sport of the app, not from the participant type. A singles, doubles or team Badminton category all use it.
- **Up to 6 score sheets per page** prints a compact sheet for singles and doubles. Team matches always print the full one-page sheet, as does **1 score sheet per page**.

## Layout of the Badminton sheet

- The sheet starts with the match type (for example SINGLES) and a **Match Details** block: **Match Number**, **Match Date**, **Court Number** ("Table" and the table number, or "-"), **Round**, **Category**, **Commencement Time**, **Conclusion Time** and **Duration**.
- Each game is a block headed **Game 1**, **Game 2** and so on, with one row per side: the back number, the player name (both names for doubles, under **Player Names**), 30 numbered rally boxes and the game score.
- **Rally boxes**: 30 numbered boxes (1 to 30) per side and game. With scores, the boxes up to the side's points are shaded; without scores they are left plain for the scorer.
- The number of game blocks follows the points stored for the match. A match with no points shows **three** game blocks.
- **Winner** is the winner's name and **Result** the games won, winner first (for example 2-1). **Umpire Signature** and **Winner Signature** are empty boxes.
- The full sheet adds **Officials** (**Umpire** and **Referee** with name and **Signature**), **Service Judge**, **Misconduct Tracking** (a **Black Card** grid for Player A and Player B) and **Overall Result**.

## Team Badminton sheets

- A team match prints a **Submatches** section: each sub-match of the line-up, marked SINGLES or DOUBLES, with the players from the playing order (club or member association under the names), its games, its result (games won, for example 2-1) and its **Winner** when known.
- A team match with no line-up yet prints one blank SINGLES block with the placeholder sides **A1** and **B1**.
- The team logos are printed when the print settings enable the team logos (Logo 1 to Logo 6).
- The playing order of the team tie is read from the playing order of the match. The toss sheet is printed for team categories only.

## Print settings that decide the Badminton fields

- Each field of the sheet (match number, date, court, round, category, commencement and conclusion time, duration, winner, overall result, umpire, referee, service judge and misconduct tracking) is printed only when it is switched on in the print settings of the event.

## Print settings that matter for Badminton

- The **matches best of** count is kept in the print settings for each participant type (singles, doubles, teams). The default is 5 when none is saved.
- The logos are set per participant type. Badminton team sheets use the team logo settings.

## Printing without scores

- With **Without Scores** the rally boxes are not shaded and the game scores, **Winner** and **Result** are hidden, so the scorer can write them by hand.
- With **With Scores** the rally boxes up to the saved points are shaded and the game scores, winner and result are printed.

## Messages

- The Badminton sheet uses the same messages as the Printing page: "Please Select Match", "No records found" and "Settings updated successfully".

## Frequently asked questions

**How is a Badminton score sheet printed?** Choose the match or the day in the Printing page, select the matches, choose with or without scores, then print. The Badminton layout is used automatically.

**What are the rally boxes?** Thirty numbered boxes for each game, used to mark the points of the game during the match.

**How many games are on a blank Badminton sheet?** Three game blocks (Game 1 to Game 3) when the match has no points yet. A team match with no line-up shows a placeholder block with the sides A1 and B1.

**What does Result show?** The games won, winner first (for example 2-1).

**Why is a field missing from the Badminton sheet?** Each field is printed only when it is switched on in the event's print settings.

**Why does the sheet look different from the other sports?** The Badminton sheet has 30 rally boxes per side for each game. The other sports use the score sheet layout of the day-wise and score sheets.

**What does the Result column show on the Badminton sheet?** The games won by the winner and the loser, for example 2-1. It is hidden when printing without scores.

**How are the team logos printed on the Badminton sheet?** They are printed when the print settings enable the team logos (Logo 1 to Logo 6).
