---
doc_id: tms.printing
title: Printing page – score sheets, fixtures, schedule, back numbers and player lists
routes:
  - tms/printing/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - printing
  - printing page
  - print queue
  - print score sheet
  - print scoresheet
  - day wise score sheet
  - print all matches
  - print selected match
  - print with scores
  - print without scores
  - print schedule
  - print back no
  - print players list
  - print fixtures
  - print group wise
  - print round wise
  - preview print
  - print status
  - printed matches
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Printing page for?
  - How do I print the score sheets of a day?
  - How do I print one match?
  - What is the difference between printing with scores and without scores?
  - How do I print the fixtures of a group or a knockout?
  - How do I print the back numbers?
  - How do I print the players list?
  - Why does a match say "Printed"?
  - What does "Please Select Match" mean?
backend_sources:
  - gateway/src/routers/print_router.py (get_print_settings, update_print_settings, update_print_status, get_print_queue, update_queue_status, get_print_alert_settings)
  - gateway/src/routers/match_router.py (matches)
  - gateway/src/routers/group_router.py (get_groups, get_group_matches)
  - gateway/src/routers/stage_router.py (get_stages)
  - gateway/src/routers/fixture_router.py (get_knockout_matches)
  - gateway/src/routers/registration_router.py (get_event_participants)
  - gateway/src/routers/planner_router.py (get_event_slots)
  - gateway/src/routers/playing_order_router.py (get_team_playing_order_with_matches)
  - tms/src/router/print_router.py
  - tms/src/service/print_service.py
source_files:
  - src/app/modules/tms/printing/printing.component.html
  - src/app/modules/tms/printing/printing.component.ts
  - src/app/modules/tms/printing/print-team-sub-matches.util.ts
  - src/app/modules/tms/day-wise-print/day-wise-print.component.html
  - src/app/modules/tms/day-wise-print/daywise-badminton/daywise-badminton.component.html
  - src/app/shared/match-print-popup/match-print-popup.component.ts
  - src/app/shared/print-queue-sidebar/print-queue-sidebar.component.ts
  - src/assets/i18n/en.json
---
# Printing page

The **Printing** page (route `tms/printing/...`) prints the paper that goes with the matches: the score sheets of each day, the score sheets of a group or round, the fixtures (group and knockout trees), the schedule, the back number lists and the players list. It also shows the **Ready for Print** queue.

## Where to find it

Open **Printing** from the sidebar.

## What the URL means

- The example `tms/printing/0/0/0/0/1358` sets participant type 0, category 0, event 0, event category 0 and stage 1358.
- The event is **not** read from the URL. The page reads it from the browser session (the event saved when the user opened the event). With no event saved, the page shows the empty state and makes no event calls.
- Zero for the category means **all categories** of the event. The page lists the categories of the event in the category dropdown, and the matches shown are for the category or stage chosen there.

## Header and top bar

- Title: **Printing**.
- **Ready for Print** – opens the print queue (the list of matches waiting to be printed). The badge shows how many matches wait. The button is hidden when print alerts are disabled.
- The category dropdown and its child categories ("Sub Category" or "Sub Division" for a league) choose the matches to print. Stage tiles (S1, S2 ...) choose the stage.
- The venue dropdown ("Choose Venue") and the month and year dropdowns choose the day for day-wise printing.

## The six print modes

The mode is chosen from the print options. The default is **Day Wise Score Sheet**.

1. **Day Wise Score Sheet** – the matches of the chosen day and venue, with their tables and times. Filters: start and end date and time, groups and rounds (the score sheet filters). Actions: **Preview**, **Print**, **Print All Toss Sheet** (team categories only).
2. **Score Sheet** – the matches of the stage or category as a list. Actions: **Print all matches**, **Print Group-wise** (group stages), **Print round-wise** (knockout stages), **Print** for the selected rows, and **Print Toss Sheet** for a team category.
3. **Fixtures** – the group matrix or the knockout tree. Group stages use **Print Group-wise** and **Print Detailed Result** (team categories). Knockout stages show "Knockout Matches" and "Position Matches" tabs when the stage has position matches; **Print** prints the tree.
4. **Schedule** – the tables and time slots of the venue, with the legend (Unoccupied, Occupied, Selected, Blocked) and the list view. Action: **Preview**, then print the schedule section.
5. **Back no.** – the participants with their back numbers and seeds, with **Print list** (the list on screen) and **Print back no** (all back numbers).
6. **Players** – the players of the event in two views, **Category Wise** and **Entity Wise**. Entity Wise is split by **Member Association** or **Club**. Search is by name. Actions: **Preview** and **Print**.

## Print dialog: with scores or without

- Printing any score sheet first asks **Print Sheet?** with **Select Print Type**:
  - **With Scores** – "Prints the selected group's scoresheets with scores as in the System".
  - **Without Scores** – "Prints the selected group's scoresheets blank, without scores".
- The dialog is closed with the cross. Choosing one option prints at once.
- The choice applies to the print only; it does not change the saved match scores.

## Choosing matches

- A tick box selects each match; **select all** ticks every row of the page.
- **Print all matches** prints every match of the list, not only the ticked ones.
- **Print** (selected) needs at least one ticked match. With none ticked: "Please Select Match".
- Single score sheets print one per page; **Up to 6 score sheets per page** prints six per page (group-wise and round-wise print use the page breaks of the group).

## Printed status

- After the print step, the page marks the matches as printed. The **Print Status** column shows "Printed" for these matches and "-" for the others.
- The mark is set when the print dialog closes, as the page's code shows. The page does not check that the paper came out, so use the Print Status column to check before printing again.

## Ready for Print queue

- The queue holds matches added by **Queue** in the match print popup, or by the Ready for Print action.
- The sidebar lists them. **Print All** and **Print Selected** print the queued matches.
- The queue is kept on the server (see the printing API guide).

## Preview

- **Preview** opens the same sheets on screen before printing. The preview uses the same choices as the print (with or without scores).

## Messages

- "Please Select Match" – no match is ticked (or the list is empty) when printing.
- "Settings updated successfully" (or the server's message) – the print settings were saved.
- "Error updating settings" – the print settings could not be saved.
- "No records found" – the list is empty for the filters chosen.
- "No data available" – there is no data to show for the chosen print mode.

## Permissions

- Printing itself is a browser action. Saving print settings and updating the print status need the print settings permission (Edit). The server refuses the change without it, and its message is shown.

## Frequently asked questions

**What is this page for?** Printing the score sheets, fixtures, schedules, back numbers and players lists of an event.

**Why does the page show nothing?** No event is selected in the session. Open the event first.

**How do I print a day's score sheets?** Choose the venue and the day, tick the matches (or use **Print**), choose with or without scores, then print.

**What is the difference between with and without scores?** With scores fills the scores from the system; without leaves the boxes blank for hand writing.

**Why does a match say Printed?** The match was printed (the print dialog was closed after printing). Print it again if the sheet was lost.

**How do I print the back numbers?** Open the Back no. mode and use **Print back no** or **Print list**.

**What is the Printing page for?** It prints the paper for the matches: score sheets of a day, group or round, the fixtures (group and knockout trees), the schedule, back number lists and the players list. **Ready for Print** opens the print queue.

**How do I print the score sheets of a day?** Choose the venue and the day, tick the matches (or print them all), choose with or without scores, then print.

**How do I print one match?** Tick the match and click **Print**. **Print all matches** prints every match of the list, not only the ticked one.

**How do I print the fixtures of a group or a knockout?** Choose the **Fixtures** print mode. Group stages use **Print Group-wise**; for a knockout stage **Print** prints the tree (with **Knockout Matches** and **Position Matches** tabs when the stage has position matches).

**How do I print the players list?** Choose the **Players List** print mode, pick **Category Wise** or **Entity Wise**, and click **Print Players List**.

**What does "Please Select Match" mean?** No match is ticked. Tick at least one match, or use **Print all matches**.

**What is shown on the print queue?** The matches waiting to be printed: those added with **Queue** in the match print popup or by the Ready for Print action. Open it with **Ready for Print** (the badge shows how many wait); **Print All** and **Print Selected** print the queued matches.
