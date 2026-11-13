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
  - src/app/modules/tms/printing/call-out-schedule-list.util.ts
  - src/app/modules/tms/day-wise-print/day-wise-print.component.html
  - src/app/modules/tms/day-wise-print/daywise-badminton/daywise-badminton.component.html
  - src/app/shared/match-print-popup/match-print-popup.component.ts
  - src/app/shared/print-queue-sidebar/print-queue-sidebar.component.ts
  - src/app/shared/match-print-popup/match-print-popup.component.html
  - src/app/shared/print-queue-sidebar/print-queue-sidebar.component.html
  - src/app/shared/no-event-selected/no-event-selected.component.html
  - src/assets/i18n/en.json
---
# Printing page

The **Printing** page (route `tms/printing/...`) prints the paper that goes with the matches: the score sheets of each day, the score sheets of a group or round, the fixtures (group and knockout trees), the schedule, the back number lists and the players list. It also shows the **Ready for Print** queue.

## Where to find it
Open **Printing** from the sidebar.

## What the URL means
- The example `tms/printing/0/0/0/0/1358` sets participant type 0, category 0, event 0, event category 0 and stage 1358.
- The data is loaded for the event saved in the browser session (the event saved when the user opened the event), not for the event number in the address.
- When the last number of the address is 0 (no event), the page shows "No record found" and "Create Event to begin with Printing." with a **Go to Event** button, and makes no event calls. When the event has no categories it shows "Add Categories in this event to begin with Printing." with the same button.
- Zero for the category means **all categories** of the event. The page lists the categories of the event in the category dropdown, and the matches shown are for the category or stage chosen there.

## Header and top bar
- Title: **Printing**.
- **Ready for Print** – opens the print queue (the list of matches waiting to be printed). The badge shows how many matches wait. The button is hidden when print alerts are disabled.
- The category tabs and their child categories ("Sub Category" or "Sub Division" for a league) choose the matches to print. Stage tiles (S1, S2 ...) choose the stage. The category tabs are not shown in the **Schedule**, **Back no.** and **Day Wise Score Sheet** modes, and the stage tiles are not shown in **Players**. In **Players**, **Entity Wise** greys out the category tabs.
- **Day Wise Score Sheet** has its own venue, month and year drop-downs and a date strip to choose the day.
- **Schedule** shows the venues under "Choose Venue" as tabs, with month and year drop-downs and a date strip.

## Printing page print modes: Day Wise Score Sheet, Score Sheet and Fixtures
The mode is chosen from the six print options: Day Wise Score Sheet, Score Sheet, Fixtures, Schedule, Back no. and Players. The default is **Day Wise Score Sheet**.

1. **Day Wise Score Sheet** – the matches of the chosen day and venue, with their tables and times. **Filter** opens the score sheet filters (start and end date and time, groups and rounds). Search: "Search by participants, round, and group". Actions: **Preview**, **Print All Toss Sheet** (greyed out unless the day has a team match), **Print all matches** and **Print** (greyed out until a match is ticked).
2. **Score Sheet** – the matches of the stage or category as a list, with **Filter**, the same search and **Preview** (greyed out when the list is empty). Actions: **Print round-wise** (knockout stages), **Print Group-wise** (group stages), **Print all matches**, **Print Toss Sheet** (team categories) and **Print** for the ticked rows (greyed out until a match is ticked).
3. **Fixtures** – the group matrix or the knockout tree. Group stages have the views **All groups**, **All matches** and **All Rounds**, a participant search, **Filters**, **Preview**, **Print**, and **Print Detailed Result** (team categories, not in the All groups view). Knockout stages show "Knockout Matches" and "Position Matches" tabs when the stage has position matches; **Preview** and **Print** print the tree.

## Printing page print modes: Schedule, Back no. and Players
4. **Schedule** – the tables and time slots of the venue, with the legend (Unoccupied, Occupied, Selected, Blocked), a grid view and a list view (the list view has a search). **Filter** narrows the slots. Action: **Preview** (greyed out when there is nothing to show), then print the schedule section.
5. **Back no.** – the participants with **S.No**, **Participant Name**, **Participant No.**, **Seeding**, **Member Association**, **Club** and **Federation/Unaffiliated/Passport**, with **Preview**, **Print list** (the list on screen) and **Print back no** (all back numbers).
6. **Players** – the players of the event in two views, **Category Wise** and **Entity Wise**. Entity Wise is split by **Member Association** or **Club**. Search is by name. Elite players carry an **Elite** badge. Actions: **Preview** and **Print**.

## Printing page for Match Call Out events
For a tournament whose schedule method is Match Call Out (not Manual Scheduling), two modes work differently. Leagues and other events are unchanged.

- **Schedule** has no grid: it shows the list view only, with the matches that are on a table (called or live) for the chosen venue and date, ordered by table. The slot filter and the search are not shown. The schedule print button is greyed out when no match is on a table.
- **Day Wise Score Sheet** lists every match of the venue and date (active and completed) that has both players known. The search box is not shown.
- In both modes **Filter** opens a call-out filter panel with one choice each for **Table**, **Category**, **Stage**, **Round** and **Group**. Choosing a new category clears stage, round and group; a new stage clears round and group. The cross on a choice clears that one, **Clear All** clears all, and closing the panel clears every filter.

## Print dialog: with scores or without
- Printing any score sheet first asks **Print Sheet?** with **Select Print Type**:
  - **With Scores** – "Prints the selected group's scoresheets with scores as in the System".
  - **Without Scores** – "Prints the selected group's scoresheets blank, without scores".
- For a normal print (not group-wise or round-wise) the dialog also asks the layout: **1 score sheet per page** ("Print 1 score sheet per page", the default) or **Up to 6 score sheets per page** ("Print up to 6 score sheets per page"). A small picture shows the chosen layout.
- Pick the options, then click **Print** in the dialog to open the browser print window.
- Closing the dialog with the cross, a click outside it or Escape cancels the print and nothing is marked as printed.
- The choice applies to the print only; it does not change the saved match scores.

## Choosing matches
- A tick box selects each match; **select all** ticks every row of the page.
- **Print all matches** prints every match of the list, not only the ticked ones.
- **Print** (selected) needs at least one ticked match; the button stays greyed out until one is ticked. Where a print starts with no match chosen, the page shows "Please Select Match".
- **1 score sheet per page** prints one per page; **Up to 6 score sheets per page** prints up to six per page (group-wise and round-wise print use the page breaks of the group).

## Printed status
- After the print step, the page marks the matches as printed. The mark is sent as soon as the browser print window is opened. The page does not check that the paper came out (cancelling the browser print window still marks them).
- A **Day Wise Score Sheet** print sets a separate day-wise mark. Every other print (Score Sheet mode, the print queue, the match ready popup) sets the normal printed mark.
- The **Print Status** column of the Day Wise Score Sheet list shows "Printed" when either mark is set. The Score Sheet list shows "Printed" only for the normal mark, so a match printed only day-wise shows "-" there. Other matches show "-".
- The server only marks matches that have two real players. A match with a missing player or a BYE is skipped, with no message.
- A normal print takes the matches out of the **Ready for Print** queue and the badge count is refreshed. A Day Wise Score Sheet print does not take them out of the queue.
- Marking needs the **Print Settings** permission in edit mode (administrators always have it). If it is refused ("Access Denied"), no message is shown.

## Ready for Print queue
- The queue holds matches added by **Queue** in the match print popup, or by the Ready for Print action.
- The sidebar is titled **Print Queue**. It has a search ("Search by player, match or category..."), a **Category** filter (pick several, remove one with its chip) and the columns **Category/Round/Match**, **Players** and **Time Added**.
- **Print All** (greyed out when the queue is empty) and **Print Selected** (greyed out until a row is ticked) print the queued matches.
- An empty queue shows "No queued matches found."
- The queue is kept on the server. Only matches with two real players can be queued; others are skipped with no message.
- The queue lists the newest matches first. It leaves out matches already printed (normal print), matches that became a BYE after they were queued, team sub matches, and matches whose stage, group or round was removed (for example after the fixture was drawn again).
- The search matches the category name or short name, a player name, or the match number.

## Printing page match ready popup
- When a score entered on this page makes new knockout matches ready, a popup appears: **New Match Ready** for one match, or "{round} Ready" with "{count} matches created in this category" for several.
- One match: **Print Now** or **Queue**. Several: **Print All matches** or **Queue All**, and "+ {count} more matches" opens the full list.
- The popup can close by itself ("Auto-dismissing in {seconds}s") when the organisation set an alert timeout.
- The popup is never shown for team categories, for non-knockout stages, or when print alerts are disabled. With alerts disabled, the **Ready for Print** button is hidden too.

## Preview
- **Preview** opens the same sheets on screen before printing. The preview uses the same choices as the print (with or without scores).

## Messages
- "Please Select Match" – no match is ticked (or the list is empty) when printing.
- "Print Settings Updated" – the server saved the print settings ("Settings updated successfully" is shown only if the server sends no message).
- "Error updating settings" – the save failed and the server sent no message; otherwise the server's message is shown (for example "Access Denied").
- "No records found" – the list is empty for the filters chosen.
- "No data available" – there is no data to show for the chosen print mode.

## Permissions
- Printing itself is a browser action. Saving print settings, marking matches as printed and adding matches to or removing them from the queue need the **Print Settings** permission in edit mode. Administrators always have it.
- Without it the server answers "Access Denied". For a print settings save that message is shown; for the printed mark nothing is shown.
- Reading the print queue needs only a login.

## Frequently asked questions: Printing page
**What is this page for?** Printing the score sheets, fixtures, schedules, back numbers and players lists of an event.

**Why does the page show nothing?** No event is selected, or the event has no categories. Open the event first, or click **Go to Event** and add categories.

**How do I print a day's score sheets?** Choose the venue and the day, tick the matches (or use **Print**), choose with or without scores, then print.

**What is the difference between with and without scores?** With scores fills the scores from the system; without leaves the boxes blank for hand writing. Choose one in the **Print Sheet?** dialog, then click **Print**.

**Why does a match say Printed?** The match was sent to print (the browser print window was opened). In the Score Sheet list only a Score Sheet, queue or popup print counts; the Day Wise list also counts a day-wise print. Print it again if the sheet was lost.

**How do I print the back numbers?** Open the Back no. mode and use **Print back no** or **Print list**.

**What is the Printing page for?** It prints the paper for the matches: score sheets of a day, group or round, the fixtures (group and knockout trees), the schedule, back number lists and the players list. **Ready for Print** opens the print queue.

## Frequently asked questions: Printing page (part 2)
**How do I print the score sheets of a day?** Choose the venue and the day, tick the matches (or print them all), choose with or without scores, then print.

**How do I print one match?** Tick the match and click **Print**. **Print all matches** prints every match of the list, not only the ticked one.

**How do I print the fixtures of a group or a knockout?** Choose the **Fixtures** print mode. Group stages use **Print Group-wise**; for a knockout stage **Print** prints the tree (with **Knockout Matches** and **Position Matches** tabs when the stage has position matches).

**How do I print the players list?** Choose the **Players** print mode, pick **Category Wise** or **Entity Wise**, and click **Print**.

**Why is the Print button greyed out?** No match is ticked. Tick at least one match, or use **Print all matches**.

**Why is Print All Toss Sheet greyed out?** The chosen day has no team match. Toss sheets are only for team matches.

**Why is the Ready for Print button missing?** Print alerts are disabled for the event.

**What does "Please Select Match" mean?** No match is ticked. Tick at least one match, or use **Print all matches**.

## Frequently asked questions: Printing page (part 3)
**What is shown on the print queue?** The matches waiting to be printed: those added with **Queue** in the match print popup or by the Ready for Print action. Open it with **Ready for Print** (the badge shows how many wait); **Print All** and **Print Selected** print the queued matches.

**Why is a match still in the print queue after I printed it?** It was printed from **Day Wise Score Sheet**. A day-wise print does not take a match out of the queue; a Score Sheet, queue or popup print does.

**Why did a match not go into the print queue?** Only matches with two real players can be queued. A match with a missing player or a BYE is skipped, with no message.
