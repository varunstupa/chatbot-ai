---
doc_id: tms.event-settings.print-settings.score-sheet
title: Print Settings – score sheet (Table Tennis, Padel, Tennis)
routes:
  - tms/event-settings/print-settings/:event_id
aliases:
  - score sheet fields
  - toss sheet
  - best of
  - match details
tenants: all
exclude_tenants: []
sports: [table_tennis, padel, tennis]
overrides: null
suggested_questions:
  - Which match details can I show on the score sheet?
  - How do I print a toss sheet for team matches?
  - What does Best Of change on the score sheet?
source_files:
  - src/app/modules/tms/print-settings/print-settings.component.html
  - src/app/modules/tms/print-settings/print-settings.component.ts
---
# Score sheet settings for Table Tennis, Padel and Tennis

This guide covers the **Print Layout → Score Sheet** panels for Table Tennis, Padel and Tennis organisations. Saving, printing, logos and back numbers are in the general Print Settings guide.

## Score sheet: Event Details and Best Of

- **Event Details** → **Event Title** – prints the event name at the top of the sheet.
- **Best Of** – choose 1 to 6. It sets how many game columns the sheet has for writing scores.

## Score sheet: Match Details (Singles and Doubles)

Tick what to print on the sheet:
- **Match Date** with a **Date Format** (DD/MM/YYYY, MM/DD/YYYY or YYYY/MM/DD).
- **Match Time** with a **Time Format** (24 Hours or 12 Hours).
- **Category**, **Table**, **Group**, **Stage**, **Round**, **Match ID**.
- **Umpire** – a field for the umpires and their signature.
- **Coach** – coach fields with Y and R boxes.
- **Winner** – the winner field and signatures of players/coaches.
- **S**, **T**, **Y**, **1YR**, **2YR** – extra boxes printed next to each player for marking during the match.
- **Cards** – card reason fields for both players.
- **Additional Details** – T-shirt colour, racket control (before/after) and ball selection.

## Score sheet: Teams

For **Teams** the panels are the same, plus:
- **Playing Order** – choose the team playing order format; the sheet lists its individual matches (singles and doubles) with Team A and Team B positions.
- **Referee** – referee field and signature.
- **Reserve Players** – reserve player fields for both teams.
- **T-shirt color** – for both teams.
- The sheet shows **Match Result** and **Team Result** columns and the team captains' signatures.
- Sheet choice: **Scoresheet** (results) or **Toss Sheet** (team captains and line-up before the match), or **Preview**.

## Frequently asked questions: score sheet

**Which match details can I show?** Date, time, category, table, group, stage, round, match ID, umpire, coach, winner, cards, the S/T/Y/1YR/2YR boxes and additional details.

**How do I change the date format?** Tick **Match Date** and choose the **Date Format**.

**How do I print a toss sheet?** Select **Teams**, save the layout, then choose **Toss Sheet** and print.

**Why is the team line-up empty on the sheet?** Choose a format under **Playing Order** and save.
