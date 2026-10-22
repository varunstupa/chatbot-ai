---
doc_id: tms.event-settings.print-settings.badminton
title: Print Settings – Badminton score sheet
routes:
  - tms/event-settings/print-settings/:event_id
aliases:
  - badminton score sheet
  - service judge
  - misconduct tracking
  - court number
tenants: all
exclude_tenants: []
sports: [badminton]
overrides: null
suggested_questions:
  - How do I add the service judge to the score sheet?
  - Can the score sheet show match duration?
source_files:
  - src/app/modules/tms/print-settings/badminton-print-setting/badminton-print-setting.component.html
  - src/app/modules/tms/print-settings/print-settings.component.html
---
# Score sheet settings for Badminton

Badminton organisations have their own score sheet layout under **Print Layout → Score Sheet**. Saving, printing, logos and back numbers are in the general Print Settings guide. For Teams, the **Toss Sheet** uses the standard team toss sheet.

## Badminton score sheet: panels

- **Event Details** → **Event Title**.
- **Logo(s)** – toggle, number of logos and uploads.
- **Officials** – tick what to print: **Umpire**, **Referee**, **Service Judge**, **Misconduct Tracking**.
- **Playing Order** (Teams) – choose the team playing order format; the sheet lists the **Submatches** (singles and doubles) for Team A and Team B.
- **Match Details** – **Match Number**, **Match Date** (with date format), **Court Number**, **Commencement Time** (with time format), **Conclusion Time**, **Duration**.
- Click **Save**; then **Print** appears.

## Badminton score sheet: what is printed

- Player names, the game-by-game **Result**, the **Overall Result** and the **Winner**.
- For Teams: the submatches with A1/B1 (singles) or A/A–B/B (doubles) positions.
- **Black Card** fields for Player A and Player B, and name/signature fields for the officials ticked.

## Frequently asked questions: Badminton score sheet

**How do I add the service judge?** Tick **Service Judge** under **Officials** and save.

**Can the sheet show how long the match took?** Yes, tick **Commencement Time**, **Conclusion Time** and **Duration**.

**Is the court number printed?** Tick **Court Number** under Match Details.

**Can the score sheet show match duration?** Yes. Tick **Commencement Time**, **Conclusion Time** and **Duration** in the score sheet settings.
