---
doc_id: tms.event-settings.day-planner
title: Day Planner page — Organiser Guide and Troubleshooting
routes:
  - tms/event-settings/day-planner/:event_id
aliases:
  - day planner
  - planner
  - plan settings
  - match slots
  - time slots
  - breaks
  - lunch break
  - match schedule planning
  - playing hours
  - tournament timetable
  - reset planning
  - planner buttons not working
tenants: all
exclude_tenants: []
overrides: null
document_type: product_help
audience:
  - tournament organisers
  - event administrators
  - non-technical users
supported_languages:
  - English
  - Hindi
  - Hinglish
suggested_questions:
  - How do I plan the playing times for a day?
  - How do I add a lunch break?
  - How many matches fit in a day?
  - Why can I not change anything on the Day Planner?
  - What does Reset Planning do?
  - Why are my planner buttons not working?
  - How do I add a venue and dates?
  - Why are scheduled matches disappearing?
  - How do I undo deleting a plan?
  - How can I fit more matches into one day?
backend_sources:
  - gateway/src/locales/en/LC_MESSAGES/messages.po (PLANNER_* messages)
  - gateway/src/routers/planner_router.py (create/update_event_venue_planner_settings, create/update_event_venue_interval, reset_event_venue_changes)
  - tms/src/service/planner.py (create_event_venue_planner, update planner, reset_event_venue_changes)
source_files:
  - src/app/modules/tms/day-planner/day-planner.component.ts
  - src/app/modules/tms/day-planner/day-planner.component.html
  - src/app/modules/tms/day-planner/venue-name.validator.ts
  - src/app/core/services/day-planner/day-planner.service.ts
  - src/app/modules/admin/venue-management/venue-management-tms/venue-management-tms.component.html
  - src/assets/i18n/en.json
answer_notes: |
  Guidance for the assistant:
  - Understand the user's intent rather than requiring the exact wording shown in the interface.
  - Explain the solution in plain language and use the exact UI labels when telling the user what to click.
  - Give short, actionable steps. Mention important warnings before suggesting destructive actions.
  - If different causes could explain the same symptom, ask one focused follow-up question.
  - Do not claim to know the user's current plan, selected venue, schedule or permissions unless live application data is available.
  - Do not invent features, settings, limits or behaviour not documented here.
  - If the user mentions matches already played, explain that affected dates cannot be removed.
  - Keep **planning**, **scheduling matches**, and **venue registration** distinct. They are related but are not the same action.

  Intent: plan a day or set playing hours: Tell the user to select a venue, click a day, choose Plan Settings or Start Planning, set Day Duration, Single match duration, total tables and playing tables, then Save. Mention that matches are placed into slots separately using Open Scheduler.

  Intent: add a break: Use Interval → Add new, choose a break name, set start and end in `HH:mm`, then Save. Explain that matches are not placed during breaks and up to five breaks can be added at once.

  Intent: calculate match capacity: Use the estimate shown on the page and explain that capacity depends on usable time slots and available tables. Suggest checking playing hours, match duration, breaks and table availability. Do not calculate an exact capacity unless the necessary plan values are provided or available.

  Intent: planner is locked or buttons do nothing: First check whether Enable Venue Registration is switched on in Venue Management. When it is enabled, Day Planner controls are disabled. If the issue is saving rather than controls not responding, check the user's permissions and whether the session has expired.

  Intent: reset or restore planning: Explain that Reset Planning deletes all plans and breaks of the selected venue on all its dates, and that the server refuses it while any match is scheduled in that venue's slots. There is no Undo for Reset Planning; do not promise that reset can be undone. If a single plan or break needs changing, suggest editing that item instead.

  Intent: deleted a plan or break by mistake: Tell the user to click Undo within about five seconds after deletion. Do not confuse this short Undo action with Reset Planning, for which no Undo option is documented.

  Intent: add venue dates: Open the Choose Venue dropdown → Add venue (or the edit icon next to a venue), enter a venue name and time zone, choose dates within the event's Start Date and End Date, click Apply, then Save or Update. For a League with no dates, explain that venue and corresponding dates must be added first.

  Intent: scheduled matches are affected by date changes: Explain that confirming the event-date reset removes affected scheduled matches. If matches on a date are in progress or already scored, the date change is refused. Venue dates with scheduled matches cannot be removed in the Add venue panel.

  Intent: access denied or sign-in issue: For Access Denied, explain the relevant permission: Add Time Slot for plans or Add Interval for breaks. For Unauthorized Access, ask the user to sign in again and retry.

  When to ask a follow-up question:
  Ask one focused question if the user's message does not identify the relevant problem.

  - “It isn't working.” → “Are the Day Planner buttons not responding, or does saving show an error?”
  - “I can't add a time.” → “Are you setting the day's playing hours, changing match duration, or adding a break?”
  - “Matches are missing.” → “Did this happen after Reset Planning, after changing venue dates, or after editing match duration?”
  - “I can't select a date.” → “Are you adding dates to a venue, and is the date inside the event's Start Date and End Date?”
  - “I can't save.” → “What exact message appears: Access Denied, Unauthorized Access, or a validation message?”

  Do not ask for the event ID unless checking live event data or a support workflow actually requires it.

  Source-of-truth and escalation rules:
  - This document describes documented Day Planner behaviour. It does not confirm the current state of a particular event or venue.
  - Organisation setup may affect whether the Day Planner step is available.
  - Do not promise that Reset Planning can be undone; only the short Undo after deleting an individual plan or break exists.
  - If a user reports a permission error, direct them to an administrator to check the relevant permission.
  - If the issue depends on live schedule data or is not covered here, explain what needs to be checked in TMS or by support.
---

# Day Planner page — Organiser Guide and Troubleshooting

## Day Planner page: purpose and where to find it

The **Day Planner** is where an organiser decides when matches can be played at each venue on each day. You set the playing hours, how long each match should take, which tables are available, and when breaks happen.

These settings create **time slots**. The Scheduler then uses those slots to place matches into the timetable. Use **Open Scheduler** to place matches into the generated slots. Planning, scheduling matches and venue registration are related but separate actions.

1. Open **Event** from the sidebar.
2. Select **Day Planner** in the row of event setup steps at the top.

- **Route:** `/tms/event-settings/day-planner/<event_id>`, for example `/tms/event-settings/day-planner/1358`.
- The Day Planner step is shown only for organisations that use it.
- Page heading: **Day Planner**. Page description: "Manage time and intervals of the matches that you scheduled".
- For tournaments, a **Method** button chooses how matches are scheduled: **Manual Scheduling** (drag and drop, described in this guide) or **Auto Match Call Out** (see the Day Planner Match Call Out guide). Leagues always use Manual Scheduling. The plans, intervals and Reset Planning described here are only shown with Manual Scheduling.

## Day Planner page: choosing a venue and a day

- **Choose Venue** selects which venue you want to plan. Each venue has its own days and plan.
- The selected venue's days appear as **Day 1**, **Day 2**, and so on, with dates. They are grouped by month.
- Use the month and year dropdowns to move between dates.
- Click a day to plan it.

For a League, the page may say "Select Venue & dates for the event" and "Add days from add date button". If no dates have been added, it shows: "No dates added. Open the 'Choose Venue' dropdown and click 'Add venue' to add a venue and its dates".

**Plan Settings** stays greyed out until the venue has at least one date.

## Day Planner page: Add venue panel (venues and dates)

Open the **Choose Venue** dropdown and click **Add venue** at the bottom of the list, or click the edit icon next to a venue, to open the **Add venue** side panel. Both are greyed out while venue registration is on.

1. Click **Add venue** to add a row.
2. Enter a **Venue Name**. It is required; there is no character limit.
3. Choose a **Time Zone**. If you leave it empty, "Central European Time (GMT+1)" is used.
4. Add the venue's **Dates**. The calendar only allows dates between the event's Start Date and End Date.
5. Click **Apply** in the date calendar.
6. Click **Save** or **Update**.

Messages:
- "Please fill venue name" — a venue name is missing (or only spaces).
- "Plan Created Successfully" — the venues were saved.
- "Dates Updated Successfully." — the event dates were saved.
- Any other message comes from the server.

Venues and courts/tables can also be managed on the **Venue Management** step.

## Day Planner page: creating a daily plan (Plan Settings)

Select a venue, click the day you want to plan, and then click **Plan Settings**. If no plan exists for that day, the page says "No fields created yet." and shows **Start Planning**. The side panel is called **Add New Event** for a new plan or **Edit Event** when changing an existing plan. The panel shows the day, date, venue and its time zone.

Fill in:

- **Day Duration — Start Time and End Time:** the hours during which matches can be played. If End Time is earlier than Start Time, the server refuses with "Invalid Date Range" (new plan) or "Start time cannot be greater than end time" (editing).
- **Single match duration (min):** minutes reserved for one match, **10–300**.
- **Total number of tables:** **1–300**.
- **Select playing tables:** click the table numbers you want to use, or **Select all**. At least one table must be selected.

All fields are required. Click **Save** for a new plan or **Update** for an existing plan. When editing a plan, **Total Slots** shows how many time slots it generates.

## Day Planner page: plan messages and overlapping plans

- "Event Created Successfully" — the new plan was saved.
- "Event updated successfully" — the plan was updated.
- "Please fill all mandatory fields." — a required field is missing.
- "Please select a date for the event." — choose a day/date.
- "Please select at least one table." — select a table under Select playing tables.
- "Value must be at least 10." / "Value must not exceed 300." — match duration out of range.
- "Value must be at least 1." / "Value must not exceed 300." — total number of tables out of range.
- "Invalid Date Range" (new plan) / "Start time cannot be greater than end time" (editing) — End Time is earlier than Start Time.

A day can have several plans, such as morning and afternoon plans or plans using different tables. A plan's time range may overlap at most **3 other plans** on the same day; plans that only touch (one ends when the next starts) do not count. Beyond that the server refuses with "Cannot create setting: Maximum of 3 overlapping settings allowed" (when adding) or "Cannot update planner: Maximum of 3 overlapping settings allowed" (when editing the times or date). Change the time range or edit an existing plan.

## Day Planner page: how time slots and match capacity work

A **time slot** is a time window equal to the **Single match duration**. Slots start at the Start Time and follow each other every Single match duration. A slot that would touch a break at all is skipped; the following slots keep the same rhythm (they do not restart at the end of the break). Time at the end of the day that is shorter than one match duration is not used.

Each slot contains the tables available during that time, typically one match per available table. When plans overlap, a table already used by another plan is not counted again.

The text near the top of the page, such as "With the current entries, … matches will take place in a single day", estimates how many matches the current settings can accommodate. Each plan card under **Current Events** shows the time range, tables, match duration and slots generated. Click a card to see total tables, match duration, slots generated and playing tables.

**Approximate match capacity = number of usable time slots × number of available tables per slot.** Actual capacity depends on the configured times, breaks, table availability and overlapping plans.

## Day Planner page: fitting more matches into a day

Depending on the venue and event requirements, you can:
1. Extend the Day Duration by starting earlier or finishing later.
2. Add more tables if they are available.
3. Shorten Single match duration if that is appropriate for the competition.
4. Review breaks and overlapping plans.

Do not remove necessary breaks or shorten match duration without considering the competition's actual requirements.

## Day Planner page: editing a plan that already has scheduled matches

- Changing the times keeps every slot that still fits the new times, so matches in those slots stay scheduled.
- Changing **Single match duration** rebuilds all slots of that plan. This is only allowed while **no match is scheduled** in that plan. Otherwise the server refuses: "Cannot update planner: matches are scheduled, cannot change match duration".
- If new times would drop or shift a slot that holds a match: "Updating the planner timing will affect already scheduled matches. Please reschedule or remove the affected matches first."
- Unselecting a table that has a scheduled match: "Cannot remove tables: matches are scheduled on the tables being removed".
- Adding or changing a break over a slot with a match: "Cannot modify intervals: would affect slots with existing matches".
- Deleting a plan whose slots hold matches is also refused (the message shown is the match-duration one above).

Remove those matches from their slots in the Scheduler first, or keep the current values.

## Day Planner page: adding a break (Interval panel)

Click **Interval** to open the **Add New Interval** side panel ("Create intervals/breaks to be kept between the matches during a day"). When editing a break it is called **Edit Interval**.

1. Click **Add new** to add a break row.
2. Choose a **Break name**, such as Breakfast, Lunch, Snacks, Dinner, Break, Water Break or Prize Distribution.
3. Set **start** and **end** times in `HH:mm` format.
4. Click **Save** for a new break or **Update** to edit an existing break.

Rules and messages:
- Break name, start and end are all required; otherwise "Please fill all mandatory fields."
- Up to **5 breaks at once**: "You can add only 5 intervals".
- Breaks on the same day may not overlap each other: "Event interval already exists".
- A break whose start is later than its end: "Start time cannot be greater than end time".
- A break name can have at most 20 characters: "Break name cannot exceed 20 characters".
- "Plan Created Successfully" (new break) or "Plan Updated Successfully" (edited break) confirms the save.
- No matches are placed during a break. Breaks appear as named cards under **Current Events**.

Example, lunch break: select the venue and day, click **Interval** → **Add new**, choose **Lunch**, enter the times and click **Save**.

## Day Planner page: editing or deleting a plan or break

Each card under **Current Events** has an edit icon and a delete icon.

- **Edit:** opens the side panel with the saved values.
- **Delete plan:** asks "Delete Event?"
- **Delete break:** asks "Delete Interval?"

The confirmation warns that the changes will be lost. Click **Yes, Delete** to proceed.

After deleting, "You successfully deleted a cell!" appears with an **Undo** button for about **5 seconds**. Click **Undo** within that time to restore the item; "Action undone successfully!" confirms it. If you do not undo it, the deletion is saved.

## Day Planner page: Reset Planning — read before confirming

**Reset Planning** deletes all plans and all breaks of the selected venue, on **every** date of that venue, not only the selected day. The system asks:

"Are you sure you want to reset the planner? If you do so it will have a direct impact on the scheduler and the match you have scheduled will be removed."

If you confirm with **Yes, Reset**:
- If any match is still scheduled in that venue's slots, the server refuses: "Cannot reset event venue changes: matches exist in event venue planner". Nothing is deleted. Remove the matches from their slots in the Scheduler first, then reset again.
- Otherwise all plans and breaks of the venue are deleted and "Planner Reset Successfully" confirms it.

No Undo is offered for Reset Planning. To change one plan or one break, edit that item instead.

## Day Planner page: changing venue dates when matches are scheduled

**Event dates (Apply in the date calendar):**
- If a match on a removed date is in progress or already scored, the change is refused: "Dates with matches in progress or already scored cannot be removed", followed by the dates.
- If a venue would lose a day, or officials registered for that day would lose it, the popup "Changing these dates will reset the schedule" lists the days removed and the registrations that will be withdrawn. **Yes, reset** removes the matches scheduled on those days from the schedule and deletes the plans and breaks of those days.

**Venue dates (Save in the Add venue panel):** a date with matches scheduled at that venue cannot be removed: "Cannot remove dates with scheduled matches". Remove the matches from their slots first. Removing a date without matches also deletes that date's plans and breaks.

## Day Planner page: why the controls may not work

If **Enable Venue Registration** is switched on for the event in the **Venue Management** step, the Day Planner cannot be changed. These controls are greyed out and do nothing:

- Reset Planning
- **Add venue** and the venue edit icons in the **Choose Venue** dropdown
- Interval
- Plan Settings
- Start Planning
- Edit/delete icons on the cards

To plan again, turn off venue registration on the Venue Management step, if that suits the event's setup. **Plan Settings** is also greyed out while the selected venue has no dates.

## Day Planner page: permissions and sign-in errors

- Saving a plan requires **Edit** permission on **Add Time Slot**.
- Saving or deleting a break requires **Edit** permission on **Add Interval**.
- Reset Planning only needs you to be signed in; it has no separate permission.
- Without the required permission, saving fails with **Access Denied**. Ask an administrator to review access.
- **Unauthorized Access** can mean the sign-in session expired. Sign in again and retry.

## Day Planner page: common errors and fixes (plans)

- **"Invalid Date Range"** — the plan's End Time is not later than its Start Time. Choose a later End Time.
- **"Please fill all mandatory fields."** — review Day Duration, match duration, table count and playing tables; fill the missing values and save again.
- **"Please select a date for the event."** — return to the day list and select the date to plan.
- **"Please select at least one table."** — under Select playing tables, select table numbers or click Select all.
- **"Value must be at least 10." / "Value must not exceed 300."** — enter a match duration between 10 and 300 minutes.
- **"Value must be at least 1." / "Value must not exceed 300."** — enter 1 to 300 tables, and select at least one playing table.
- **"Cannot create setting: Maximum of 3 overlapping settings allowed"** — three plans already overlap that time range. Change the times or edit an existing plan.

## Day Planner page: common errors and fixes (breaks, venues, access)

- **"You can add only 5 intervals"** — add no more than five break rows at once.
- **"Break name cannot exceed 20 characters"** — use a break name of up to 20 characters.
- **"Please fill venue name"** — enter a venue name; there is no character limit.
- **"Access Denied"** — ask an administrator to check Edit permission on Add Time Slot (plans) or Add Interval (breaks).
- **"Unauthorized Access"** — the session may have expired. Sign in again and retry.

## Day Planner page: how users describe common problems

These are alternate phrasings of documented Day Planner tasks, not extra features.

- Plan a day / playing hours: "Where do I set match timings?", "Tournament ka schedule time kaise set karun?", "How do I set morning and afternoon sessions?", "Where do I configure the tables for a day?"
- Add a break: "How do I add lunch time?", "Lunch break kaise add karun?", "I need a tea or water break between matches.", "How can I stop matches during prize distribution?"
- Match capacity: "Can 50 matches fit into this day?", "Ek din mein kitne matches ho sakte hain?", "Why does it say only 20 matches can happen today?"
- Planner locked: "I cannot edit my plan.", "Day Planner ke buttons kaam nahi kar rahe.", "Why does Reset Planning do nothing?"
- Reset or restore: "Reset karne se matches delete honge?", "Can I undo a reset?", "My scheduled matches disappeared after reset."
- Deleted by mistake: "Break delete ho gaya, can I restore it?", "Where is the undo option?"
- Venue dates: "No dates are showing.", "Venue ki dates add nahi ho rahi.", "Matches already ho chuke hain; can I remove that date?"
- Access: "Access Denied aa raha hai.", "I can edit the screen but cannot save."

## Frequently asked questions about the Day Planner page (planning, part 1)

**How do I plan the playing times for a day?** Choose the venue, click the day, select **Plan Settings** (or **Start Planning** if no plan exists), fill Day Duration, Single match duration and the table settings, select the playing tables, then **Save**.

**How do I add a lunch break?** Click **Interval**, select **Add new**, choose **Lunch**, enter the start and end times in `HH:mm`, and click **Save**.

**How many breaks can I add?** Up to five break rows at once.

**What is the allowed match duration?** Between 10 and 300 minutes.

**How many tables can I use?** Between 1 and 300. At least one playing table must be selected.

**Why can I not add more overlapping plans?** A plan may overlap at most three other plans on the same day. Change the times or edit an existing plan.

**How many matches fit in a day?** Roughly the number of usable time slots × the tables available per slot. A slot is one **Single match duration**; breaks are not counted. The text at the top of the page gives the estimate.

**How can I fit more matches into one day?** Shorten **Single match duration** (10 to 300 minutes), use more tables, shorten breaks or lengthen the day duration.

**Where do I put matches into the slots?** Click **Open Scheduler**. The Day Planner creates the slots; the Scheduler places matches into them.

## Frequently asked questions about the Day Planner page (planning, part 2)

**How do I add a venue and dates?** Open the **Choose Venue** dropdown, click **Add venue**, enter the **Venue Name**, choose the **Time Zone**, pick dates between the event's Start Date and End Date, click **Apply** and then **Save**.

## Frequently asked questions about the Day Planner page (problems, part 1)

**Why can I not change anything on the Day Planner?** **Enable Venue Registration** is on for the event in the **Venue Management** step. While it is on, the Day Planner controls do nothing. Turn it off there to plan again.

**Why are my planner buttons not working?** The same cause: while **Enable Venue Registration** is on in the **Venue Management** step, the Day Planner controls are greyed out and do nothing. If the controls work but saving shows an error, check your permissions or sign in again.

**Why is Plan Settings greyed out?** The selected venue has no dates yet, or venue registration is on.

**What does Reset Planning do?** It deletes all plans and breaks of the selected venue on all its dates. It is refused while any match is still scheduled in that venue's slots ("Cannot reset event venue changes: matches exist in event venue planner"). It cannot be undone.

**How do I undo deleting a plan or break?** Click **Undo** in the message shown for about 5 seconds after deleting. "Action undone successfully!" confirms it. After that the deletion is saved.

**Why are scheduled matches disappearing?** Matches are removed from the schedule when event dates are changed and you confirm **Yes, reset** in "Changing these dates will reset the schedule". Dates with matches in progress or already scored cannot be removed. Reset Planning does not remove matches; it is refused while matches are scheduled.

## Frequently asked questions about the Day Planner page (problems, part 2)

**Why can I not pick a date in the venue calendar?** Only dates within the event's Start Date and End Date can be selected.

**Why can I not change the match duration?** Matches are already scheduled in that plan's slots ("Cannot update planner: matches are scheduled, cannot change match duration"). Remove them from the slots in the Scheduler first; then the change rebuilds the plan's slots.

**Why can I not delete a plan?** Its slots still hold scheduled matches, so the server refuses (showing the match-duration message). Remove the matches from those slots first.

## Frequently asked questions about the Day Planner page (problems, part 3)

**Why do I get "Access Denied" when saving?** Your role needs Edit permission on **Add Time Slot** (plans) or **Add Interval** (breaks).
