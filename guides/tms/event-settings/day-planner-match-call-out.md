---
doc_id: tms.event-settings.day-planner-call-out
title: Day Planner page – Scheduling Method and Match Call Out planning
routes:
  - tms/event-settings/day-planner/:event_id
aliases:
  - scheduling method
  - category schedules
  - call out planner
  - minimum match rest time
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I switch to Auto Match Call Out?
  - How do I set the start time of a category for a day?
source_files:
  - src/app/modules/tms/day-planner/day-planner.component.html
  - src/app/modules/tms/day-planner/day-planner.component.ts
  - src/app/modules/tms/day-planner/match-call-out/match-call-out.component.html
  - src/app/modules/tms/day-planner/match-call-out/match-call-out.component.ts
  - src/app/modules/tms/day-planner/day-planner-sidebar/day-planner-sidebar.component.html
  - src/app/models/call-out/match-call-out.model.ts
  - src/assets/i18n/en.json
---
# Day Planner page – Scheduling Method and Match Call Out planning

## Day Planner Method button: choosing the scheduling method

For **tournaments**, the Day Planner has a **Method** button at the top, which shows the current method. Leagues do not have it and always use manual scheduling.

Click **Method** to open the **Event Scheduler** side panel: "Choose your preferred scheduling method. Manually place matches into time slots using drag and drop, or let the system automatically assign matches to available slots." Under **Schedule Method** ("Match Scheduling Preferences") pick one:

- **Manual Scheduling** – "Manually place matches into the desired time slots using drag and drop." The Day Planner shows plans, intervals and Reset Planning (see the main Day Planner guide). This is the default.
- **Auto Match Call Out** – "Let the system automatically call the next match whenever a table becomes available, regardless of the scheduled time slot." The Day Planner shows the call-out day grid described below.

Click **Save**. "Scheduling method updated" confirms it.

## Day Planner Method: changing the method when matches are scheduled

If matches are already scheduled, switching asks "Change scheduling method?" – "Are you sure you would like to change the scheduling method? If you change it, the scheduled matches will be removed." Click **Proceed** to switch, or **Cancel** to keep the current method.

After a switch the day plan of the old method is cleared and the page reloads it.

Server rules for the switch:
- While any match of the event is being played, the switch is refused: "The scheduling method cannot be changed while a match is live".
- Only matches not yet played lose their schedule (time slot, or place in the call-out queue). Scored matches keep their result and time.
- Switching to Auto Match Call Out removes the time slots of unplayed matches, together with their automatically assigned player umpires. If the event has no venue yet, a hall named "Hall" is created with the event's dates.
- Switching back to Manual Scheduling stops auto-queuing on all days.
- Changing the method needs **Edit** permission on **Schedule Match Access**.

## Day Planner Match Call Out: the day grid

With **Auto Match Call Out**, choose the venue and day as usual. The page description reads "Configure category start times, table capacity, and call-out priority for this event." At the top are **Category Schedules** and **Priority Settings**; Reset Planning is not shown.

The toolbar above the grid has:
- **Add Interval** (or **Intervals · N** once breaks exist)
- **Add Category** (or **Categories · N**)
- **Add Tables** (or **Tables · N** once a count is saved for the day)
- an arrow button, **Go to Scheduler**, which opens the Match Call Out scheduler.

The grid shows the day from 00:00 to 24:00 in 30-minute rows. Category cards appear in the row of their start time with a priority badge (**P1**, **P2** …); break cards show their name and times. Hover an empty row for **Add Category** and **Add Interval** at that time.

## Day Planner Match Call Out: Add Categories panel (one day)

Click **Add Category** (toolbar, a row, or a category card) to open **Add Categories** for the selected day: "Add categories and rounds to schedule on a queue basis. Once added, the system starts matches of a category first, across all tables, and queues remaining matches."

- **Add Category** adds a row: pick the **Category** and its **Start Time**. Opening it from a grid row fills in that row's time.
- Errors: "Select a category", "Select a time", "This category is already added for this day".
- The trash icon removes a row.
- "No categories added for this day" means the day has none yet.
- The link **Category Schedules** (after "Add categories for all dates in one place:") switches to the all-days panel.

Click **Save**; "Changes saved" confirms it. **Save** stays disabled while a row is invalid.

If you remove today's row of a category, its matches already called to tables go back to the queue. If one of them is being played, the save is refused: "Cannot remove this schedule: {count} of its matches are being played". A date that is not a day of the venue is refused with "{date} is not a day of this hall".

## Day Planner Match Call Out: Category Schedules (all days)

**Category Schedules** (top button) opens the **Day-wise Category Schedule**: "Categories that start at the same time are called in the order set on the planner." The counter **Categories N/M** shows how many of the event's categories are scheduled.

- One card per playing day (**Day N** and date) of the selected venue. **Add** (with a plus) adds a category row to that day; each row has **Category**, **Start Time** and a trash icon. "No categories for this day" means the day is empty.
- The first 5 days are shown; **+ N More · View All** shows the rest, **Show Less** hides them again.
- The same errors apply as in Add Categories. Click **Save Schedule**.

## Day Planner Match Call Out: ordering categories that start together

When two or more categories start in the same row, the row shows **Re-order Categories**.

1. Click **Re-order Categories**.
2. Drag the cards (or use the left and right arrow keys) into the order they should be called. The badge shows the new position (P1 first).
3. Click **Done** to save.

While re-ordering, the other row buttons and break cards are disabled.

## Day Planner Match Call Out: Add Interval panel (breaks)

**Add Interval** opens the **Add Interval** panel: "Create intervals/breaks to be kept in between matches during a day." It lists the day's existing breaks.

- **Add New** adds a row: **Break Name** (e.g. Lunch Break), **Start** and **End** in 24-hour time. The trash icon removes a row.
- Errors: "Enter a break name", "Use at most 20 characters", "Select a time", "End time must be after the start time", "Breaks can't overlap".
- Click **Save**; "Changes saved".

The **×** on a break card in the grid removes it at once: "<name> removed" with **Undo** for 5 seconds. Without Undo the break is deleted.

## Day Planner Match Call Out: Add Tables panel

**Add Tables** opens **Tables for <venue>**: "Set how many tables are on the floor this day."

- **Number of Tables**: type a whole number or use **−** / **+**. The page allows 1 to 999 ("Enter a whole number from 1 to 999"), but the server only accepts up to **500**; a higher number is refused and nothing is saved.
- A day that was never saved shows a default count from the server; the toolbar shows **Tables · N** only after a count is saved.
- Click **Save**; "Changes saved".

## Day Planner Match Call Out: Priority Settings panel

**Priority Settings** decides which waiting match is called first.

**Primary Priority Mode** (one):
- **By Category Elapsed Time** – "Earliest-started (longest waiting) categories first." 
- **By Round Progress** – "Earliest-outstanding round across all categories first."
- **By Category Block** – "One category fully dispatched before the next, in a configured search order."

**Priority Modifiers** (tick any, both off by default):
- **Doubles First:** "Dispatch doubles categories before singles to maximize player availability."
- **Finals Last:** "Hold finals matches until non-final matches conclude."

**Minimum Match Rest Time** – "Single value for all players; minimum gap between a player's matches." 0 to 99 **mins** ("Enter a whole number from 0 to 99").

Until the settings are saved once, the server uses **By Round Progress**, both modifiers off and **5** minutes rest; the panel opens with these values.

Click **Save Settings**; "Changes saved". Saving needs **Edit** permission on **Schedule Match Access**.

## Day Planner Match Call Out: side panels, unsaved changes and errors

- Each panel shows the day and date (or **All days** with the date range for Category Schedules) and the venue.
- Closing a panel with unsaved changes asks "Discard changes?" – "You have unsaved changes. Close without saving?" Click **Discard** to close or **Cancel** to stay.
- "Couldn't load the call-out plan. Please try again." – the plan could not be loaded; reload the page.
- "Something went wrong. Please try again." or a server message – a save failed; nothing was changed.

## Frequently asked questions about Day Planner Match Call Out

**How do I switch to Auto Match Call Out?** Click **Method**, choose **Auto Match Call Out** and click **Save**. If matches are scheduled, confirm with **Proceed**; they are removed.

**Why is there no Method button?** It is only shown for tournaments. Leagues always use Manual Scheduling.

**Why are Plan Settings and Reset Planning missing?** The event uses **Auto Match Call Out**. Switch the method to **Manual Scheduling** to use them.

**How do I set the start time of a category for a day?** Click **Add Category**, pick the category and its **Start Time**, then **Save**. For several days at once use **Category Schedules**.

**Can I add the same category twice on a day?** No: "This category is already added for this day".

**Which category is called first when two start at the same time?** The one with the lower P number. Change it with **Re-order Categories** and **Done**.

**How many tables can I set?** The page accepts 1 to 999, but the server saves at most 500 tables per day.

**Why can I not change the scheduling method?** A match is being played ("The scheduling method cannot be changed while a match is live"). Wait until no match is live.

**Where are matches actually called to tables?** In the scheduler: click **Go to Scheduler**.
