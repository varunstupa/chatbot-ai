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

- For a Badminton event the Printing page togglees the day-wise score sheet, the score sheet and the toss sheet to the Badminton layout.
- The Badminton layout is chosen from the sport of the event, not from the participant type. A singles, doubles or team Badminton category all use it.

## Layout of the Badminton sheet

- Each match has a block with the two sides. For singles each side is one player with its back number. For doubles each side shows the pair.
- **Games** is the heading of the score area. Each game is a column block: the points of side A and side B are written in rally boxes.
- **Rally boxes**: each game has 30 numbered boxes (1 to 30) for the points. The boxes are used by hand: the scorer ticks or writes each point.
- The number of game blocks follows the points stored for the match. A blank sheet (with no points) shows **three** game blocks, marked as the placeholder sides **A1** and **B1**.
- **vs** separates the two sides.
- **Result** is the number of games won by each side.

## Team Badminton sheets

- A team match prints each sub-match (a playing table of the tie) with its own games, the same as the other team sheets.
- The team logos are printed when the print settings enable the team logos (Logo 1 to Logo 6).
- The playing order of the team tie is read from the playing order of the match. The toss sheet is printed for team categories only.

## Print settings that matter for Badminton

- The **matches best of** count is kept in the print settings for each participant type (singles, doubles, teams). The default is 5 when none is saved.
- The logos are set per participant type. Badminton team sheets use the team logo settings.

## Printing without scores

- With **Without Scores** the rally boxes and the Result are left blank, so the scorer can write the points by hand.
- With **With Scores** the points saved for each game are printed in the rally boxes.

## Messages

- The Badminton sheet uses the same messages as the Printing page: "Please Select Match", "No records found" and "Settings updated successfully".

## Frequently asked questions

**How is a Badminton score sheet printed?** Choose the match or the day in the Printing page, select the matches, choose with or without scores, then print. The Badminton layout is used automatically.

**What are the rally boxes?** Thirty numbered boxes for each game, used to mark the points of the game during the match.

**How many games are on a blank Badminton sheet?** Three game blocks, with the placeholder sides A1 and B1.

**What does Result show?** The number of games each side has won.

**Why does the sheet look different from the other sports?** The Badminton sheet has rally boxes for the points of each game. The other sports use the score sheet layout of the day-wise and score sheets.
