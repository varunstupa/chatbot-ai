---
doc_id: tms.printing.sheets
title: Printed sheets – score sheets, fixtures, schedule, back numbers, players list and team toss sheets
routes:
  - tms/printing/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - score sheet layout
  - printed score sheet
  - day wise sheet layout
  - toss sheet
  - print toss sheet
  - detailed result print
  - print detailed result
  - back no sheet
  - players print layout
  - print group wise sheet
  - knockout tree print
  - team sheet print
  - sheet headers
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is on a day wise score sheet?
  - How many score sheets fit on one page?
  - What is a toss sheet and when is it printed?
  - What does Print Detailed Result show?
  - What is printed on the back number list?
  - How are the players printed in Category Wise and Entity Wise views?
  - Why is the toss sheet printed only for one match?
backend_sources:
  - gateway/src/routers/playing_order_router.py (get_team_playing_order_with_matches)
  - gateway/src/routers/match_router.py (matches)
  - gateway/src/routers/planner_router.py (get_event_slots)
  - tms/src/service/print_service.py
source_files:
  - src/app/modules/tms/printing/printing.component.html
  - src/app/modules/tms/printing/printing.component.ts
  - src/app/modules/tms/printing/print-team-sub-matches.util.ts
  - src/app/modules/tms/day-wise-print/day-wise-print.component.html
  - src/app/modules/tms/day-wise-print/day-wise-print.component.ts
  - src/app/shared/common-print/common-print.component.ts
---
# Printed sheets

This guide describes what each printed sheet contains. The screen and its controls are in the Printing guide. The sheets are printed from the page in the browser. Their content comes from the match, the participant, the playing order and the print settings (see the Printing API guide).

## Layout by participant type

The participant type of the category decides the sheet:

- **Singles (type 1)** – one player on each side. The player's back number, name, Member Association and Club are printed next to the score boxes.
- **Doubles and mixed doubles (types 3 and 4)** – a pair on each side. Each player is printed with its back number, name, Member Association and Club, and the names of the pair are split by "/".
- **Team (type 2)** – a team on each side, with the team name and the players of the line-up. The team sheets also carry the playing order (the order of the games of the team match) and the team result.

Team categories print the toss sheet and the detailed result; singles, doubles and mixed do not.

## Day Wise Score Sheet

- One sheet per match, with the printed heading of the venue, the date and the round.
- The score boxes are grouped by game (set). The header letters **S**, **T**, **Y** and the year headers **1 YR** and **2 YR** are printed as they are shown in the sheet (the sheet uses them as its field headings).
- A **Back No.** column and an **Umpire(s)** field are printed.
- The number of sheets per page is set by the print option: one per page ("1 score sheet per page") or up to six per page ("Up to 6 score sheets per page").
- A group heading is printed when the matches are printed group-wise.
- A forfeited participant is marked with the forfeit icon on the printed sheet.
- The Badminton sheet is different (see the Badminton printing guide).

## Score Sheet (single match or list)

- The same score sheet layout as the day-wise sheet, for the matches chosen in the list.
- The **Group** and **Round** headings are printed from the match. Knockout matches show the round name (for example the position match name).
- **Print Without Score** leaves the score boxes empty.

## Team sheets

- **Team A** and **Team B** headings. The players of each team with their back numbers, and their **1 YR** and **2 YR** columns.
- **Match Result** and **Team Result**: the score of each game of the team match, the sets won by each side, and the team match score.
- **Golden** rows: the golden match of a team tie is printed as its own row when it exists.
- The playing order fields (**field side** values) are taken from the playing order of the team match.
- A sub-match is printed for each playing table of the team match (see the sub-match helper of the printing screen).

## Toss Sheet (team only)

- Printed for team categories. It lists the playing order of the team match: the players of each team for each game, and the line-up.
- **Print Toss Sheet** prints the sheet of the first chosen match only.
- **Print All Toss Sheet** prints one toss sheet for each day match of the list (this is the day-wise version).
- The toss sheet needs a playing order; without one the playing order fields are empty.

## Print Detailed Result (team only)

- The detailed result of a team match: each game with its players and scores, and the team totals. It is offered for team categories in the Fixtures view.

## Fixtures (group and knockout)

- **Group**: the group matches as a list or as a matrix. **Print Group-wise** prints one group per set of pages; the group heading is printed on each page.
- **Knockout**: the knockout tree, with its rounds as columns and the matches linked. The tree is printed as one section. The **Knockout Matches** tab prints the main tree; the **Position Matches** tab prints the position tree (for the matches that decide the places).
- Venue heading: the venue name is printed on the schedule and the tree when a venue is selected.

## Schedule

- The tables as columns and the time slots as rows, with the slot legend: **Unoccupied**, **Occupied**, **Selected**, **Blocked**.
- Each slot shows the match (round tag: **S** for stage, **K** for knockout, **G** for group, **R** for round) and the participants with **VS**.
- Tables are printed in blocks across the page; the table numbers continue from one block to the next.
- The schedule is printed from the slot data of the venue; a venue with no slots prints "No Record Found".

## Back Numbers

- A list of the participants with **S.No**, **Participant name**, **Participant No.** (the back number), **Seeding**, **Member Association**, **Club** and **Federation/Unaffiliated/Passport**.
- **Print list** prints the list on screen; **Print back no** prints all back numbers of the event.
- Pages of 10, 20, 30, 40, 50 or 100 rows, chosen by the page size.

## Players List

- **Category Wise** – columns: **S.No**, **License ID**, **Player Name**, **Elite**, **Member Association**, **Seed**, **Points**, **DOB**, **Club**, **Total Players** and **Registration Entry Date** (the date the player registered).
- **Entity Wise** – columns: **Parent Entity** (the Member Association or the Club, depending on the tab), **Gender** and the date of birth.
- Search filters the rows by name. **Print Players List** prints the list.

## Logos

- Each sheet can show up to six logos (**Logo 1** to **Logo 6**) at the top, when the print settings enable logos for the participant type.
- Back number logos are set in the print settings (see the Printing API guide).

## Frequently asked questions

**What is on a day wise score sheet?** The match heading, the venue and round, the participants with their back numbers, the score boxes by game, the umpires and the back number field.

**How many sheets fit on a page?** One, or up to six, as chosen in the print dialog.

**When is the toss sheet printed?** For a team category, from the Score Sheet or Day Wise mode, before the team match is played. It needs the playing order.

**Why is the toss sheet printed for one match only?** The Score Sheet toss print uses the first chosen match. Use **Print All Toss Sheet** in the day-wise mode for every match of the list.

**Where are the back numbers printed?** In the Back no. mode, as a list or as back number labels.
