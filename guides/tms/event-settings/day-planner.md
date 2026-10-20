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
  - gateway/src/routers/planner_router.py (create/update_event_venue_planner_settings, create/update_event_venue_interval, reset_event_venue_changes)
  - tms/src/service/planner.py (create_event_venue_planner, update planner, reset_event_venue_changes)
source_files:
  - src/app/modules/tms/day-planner/day-planner.component.ts
  - src/app/modules/tms/day-planner/day-planner.component.html
  - src/app/core/services/day-planner/day-planner.service.ts
  - src/app/modules/admin/venue-management/venue-management-tms/venue-management-tms.component.html
---

# Day Planner page — Organiser Guide and Troubleshooting

## Purpose of this guide

The **Day Planner** is where an organiser decides when matches can be played at each venue on each day. You can set the playing hours, how long each match should take, which tables are available, and when breaks happen.

These settings create **time slots**. The Scheduler then uses those slots to place matches into the timetable.

This guide is intended for organisers who may describe a problem in everyday English, Hindi or Hinglish and may not know the exact name of a setting.

### Guidance for the assistant

- Understand the user's intent rather than requiring the exact wording shown in the interface.
- Explain the solution in plain language and use the exact UI labels when telling the user what to click.
- Give short, actionable steps. Mention important warnings before suggesting destructive actions.
- If different causes could explain the same symptom, ask one focused follow-up question.
- Do not claim to know the user's current plan, selected venue, schedule or permissions unless live application data is available.
- Do not invent features, settings, limits or behaviour not documented here.
- If the user mentions matches already played, explain that affected dates cannot be removed.
- Keep **planning**, **scheduling matches**, and **venue registration** distinct. They are related but are not the same action.

## Where to find Day Planner

1. Open **Event** from the sidebar.
2. Select **Day Planner** in the row of event setup steps at the top.

- **Route:** `/tms/event-settings/day-planner/<event_id>`
- Example: `/tms/event-settings/day-planner/1358`
- The Day Planner step is shown only for organisations that use it.
- Page heading: **Day Planner**
- Page description: “Manage time and intervals of the matches that you scheduled”.

Use this page to define playing hours, match duration, available tables and breaks. Use **Open Scheduler** to place matches into the generated slots.

## How the page is organised

### Choose a venue and day

- **Choose Venue** selects which venue you want to plan. Each venue has its own days and plan.
- The selected venue's days appear as **Day 1**, **Day 2**, and so on, with dates. They are grouped by month.
- Use the month and year dropdowns to move between dates.
- Click a day to plan it.

For a League, the page may say “Select Venue & dates for the event” and “Add days from add date button”. If no dates have been added, it may show: “No dates added. Click on the 'Venue' button to add Venue and corresponding dates”.

### Add a venue and dates

Click **Venue** to open the **Add venue** side panel.

1. Click **Add venue** to add a row.
2. Enter a **Venue Name** of no more than 20 characters.
3. Choose a **Time Zone**.
4. Add the venue's **Dates**. The calendar only allows dates between the event's Start Date and End Date.
5. Click **Apply** in the date calendar.
6. Click **Save** or **Update**.

Messages:
- “Venue name cannot exceed 20 characters” — shorten the venue name.
- “Please fill venue name” — a venue name is missing.
- “Dates Updated Successfully.” — the dates were saved.

Venues and courts/tables can also be managed on the **Venue Management** step.

## Create a daily plan

Select a venue, click the day you want to plan, and then click **Plan Settings**. If no plan exists for that day, the button may be **Start Planning**, and the page may say “No fields created yet.” The side panel is called **Add New Event** for a new plan or **Edit Event** when changing an existing plan.

The panel shows the day, date, venue and its time zone.

### Set the playing hours and tables

Fill in these fields:

- **Day Duration — Start Time and End Time:** the hours during which matches can be played. End Time must be later than Start Time. Otherwise, the server may show “Invalid Date Range”.
- **Single match duration (min):** how many minutes to reserve for one match. Allowed range: **10–300 minutes**.
- **Total number of tables:** the number of tables in the plan. Allowed range: **1–300**.
- **Select playing tables:** click the table numbers you want to use, or click **Select all**. At least one table must be selected.

Click **Save** for a new plan or **Update** for an existing plan.

Possible messages:
- “Event Created Successfully” — the new plan was saved.
- “Event updated successfully” — the plan was updated.
- “Please fill all mandatory fields.” — one or more required fields are missing.
- “Please select a date for the event.” — choose a day/date.
- “Please select at least one table.” — select at least one table under Select playing tables.
- “Value must be at least 10.” / “Value must not exceed 300.” — match duration is outside the allowed range.
- “Value must be at least 1.” / “Value must not exceed 300.” — the total number of tables is outside the allowed range.
- “Invalid Date Range” — End Time must be after Start Time.

When editing a plan, **Total Slots** shows how many time slots it generates.

A day can have multiple plans, such as morning and afternoon plans or plans using different tables. No more than **3 plans may overlap in time**. If the limit is exceeded, the system shows: “Cannot create setting: Maximum of 3 overlapping settings allowed”. Change the time range or edit an existing plan.

## How time slots and match capacity work

A **time slot** is a time window equal to the **Single match duration** setting. The Day Duration is divided into consecutive slots, excluding time covered by breaks.

Each slot contains the tables available during that time. More than one match can take place in the same slot when multiple tables are available—typically one match per available table.

When plans overlap, a table already used by another plan is not counted again.

The text near the top of the page, such as “With the current entries, … matches will take place in a single day”, estimates how many matches the current settings can accommodate. The plan card under **Current Events** shows the time range, tables, match duration and slots generated. Click a card to see total tables, match duration, slots generated and playing tables.

A useful rough estimate is:

**Approximate match capacity = number of usable time slots × number of available tables per slot.**

Actual capacity depends on the configured times, breaks, table availability and overlapping plans.

### How to fit more matches into a day

Depending on the venue and event requirements, you can:
1. Extend the Day Duration by starting earlier or finishing later.
2. Add more tables if they are available.
3. Shorten Single match duration if that is appropriate for the competition.
4. Review breaks and overlapping plans.

Do not suggest removing necessary breaks or shortening match duration without considering the organiser's actual requirements.

### Important when editing a plan

- Editing a plan keeps slots that still fit within the new times, so matches scheduled in those slots stay scheduled.
- Changing **Single match duration** regenerates all slots for that plan. Check the Scheduler afterward because the slot structure may have changed.

## Add a break or interval

Use **Interval** to open the **Add New Interval** side panel. Its description is “Create intervals/breaks to be kept between the matches during a day”.

1. Click **Add new** to add a break row.
2. Choose a **Break name**, such as Breakfast, Lunch, Snacks, Dinner, Break, Water Break or Prize Distribution.
3. Set **start** and **end** times in `HH:mm` format.
4. Click **Save** for a new break or **Update** to edit an existing break.

Limits and behaviour:
- You can add up to **5 breaks at once**. If exceeded, the message is “You can add only 5 intervals”.
- A break name can contain at most 20 characters. Otherwise, the system may show “Break name cannot exceed 20 characters”.
- No matches are placed during a break.
- Breaks appear as named cards under **Current Events**.

### Example: add a lunch break

1. Select the correct venue and day.
2. Click **Interval**.
3. Click **Add new**.
4. Choose **Lunch** as the Break name.
5. Enter the lunch start and end times in `HH:mm` format.
6. Click **Save**.

Make sure the break times match the day and venue plan you intend to use.

## Edit or delete a plan or break

Each card under **Current Events** has an edit icon and a delete icon.

- **Edit:** opens the side panel with the saved values.
- **Delete plan:** asks “Delete Event?”
- **Delete break:** asks “Delete Interval?”

The confirmation warns that the changes will be lost. Click **Yes, Delete** to proceed.

After deleting, “You successfully deleted a cell!” appears with an **Undo** button for about **5 seconds**. Click **Undo** within that time to restore the item. The message “Action undone successfully!” confirms the undo. If you do not undo it, the deletion is saved.

If you delete something by mistake, use Undo immediately. The documented Undo window is approximately five seconds.

## Reset Planning — read before confirming

**Reset Planning** clears the plan for the selected venue.

When clicked, the system asks:

“Are you sure you want to reset the planner? If you do so it will have a direct impact on the scheduler and the match you have scheduled will be removed.”

If you confirm with **Yes, Reset**:

- The planner is reset for the selected venue.
- Matches already scheduled into that venue's slots are removed from the schedule.
- Those matches must be scheduled again.

“Planner Reset Successfully” confirms the reset.

**Important:** Reset Planning is not just a visual refresh. It affects the Scheduler and removes matches already scheduled into the slots. If the user only wants to change one plan or one break, suggest editing that item instead of resetting the entire venue plan.

## Changing venue dates when matches are scheduled

If a venue's dates are changed and matches are already scheduled on dates being removed, the system warns that the schedule must be reset. Confirming with **Yes, reset** removes those scheduled matches from the schedule.

If matches on the dates have already been played, the change is refused and the system names the played dates.

Before recommending a venue-date change:
1. Check whether matches are scheduled on the dates being removed.
2. Explain that confirming the reset removes affected scheduled matches.
3. If matches have already been played on those dates, keep the dates; they cannot be removed.

## Why Day Planner controls may not work

If **Enable Venue Registration** is switched on for the event in the **Venue Management** step, the Day Planner cannot be changed. In this state, these controls do nothing:

- Reset Planning
- Venue
- Interval
- Plan Settings
- Start Planning
- Edit/delete icons

To plan again, turn off venue registration on the Venue Management step, if that is appropriate for the event's setup.

Do not tell the user that the buttons are broken without checking this setting first.

## Permissions and sign-in errors

- Saving a plan requires **Edit** permission on **Add Time Slot**.
- Saving a break requires **Edit** permission on **Add Interval**.
- Without the required permission, saving fails with **Access Denied**. Ask an administrator to review access.
- **Unauthorized Access** can mean the sign-in session expired. Sign in again and retry.

## Common errors and how to fix them

### “Invalid Date Range”

**Meaning:** The plan's End Time is not later than its Start Time.

**Fix:** Choose an End Time that is after the Start Time.

### “Please fill all mandatory fields.”

**Meaning:** A required field in the plan has not been completed.

**Fix:** Review Day Duration, match duration, table count, playing tables and the selected date. Fill the missing values and save again.

### “Please select a date for the event.”

**Meaning:** No day/date has been selected for the plan.

**Fix:** Return to the day list and select the date you want to plan.

### “Please select at least one table.”

**Meaning:** No table is selected for play.

**Fix:** Under Select playing tables, select one or more table numbers or click Select all.

### “Value must be at least 10.” / “Value must not exceed 300.”

**Meaning:** Single match duration is outside the allowed range.

**Fix:** Enter a duration between 10 and 300 minutes.

### “Value must be at least 1.” / “Value must not exceed 300.”

**Meaning:** Total number of tables is outside the allowed range.

**Fix:** Enter a number from 1 to 300, and select at least one playing table.

### “Cannot create setting: Maximum of 3 overlapping settings allowed”

**Meaning:** Three plans already overlap with the time range you are trying to add.

**Fix:** Change the new plan's start/end times or edit an existing plan so that no more than three plans overlap.

### “You can add only 5 intervals”

**Meaning:** More than five breaks were added in one attempt.

**Fix:** Add no more than five break rows at once.

### “Break name cannot exceed 20 characters”

**Meaning:** The break name is too long.

**Fix:** Use a shorter break name, up to 20 characters.

### “Please fill venue name” / “Venue name cannot exceed 20 characters”

**Meaning:** A venue name is missing or longer than the allowed length.

**Fix:** Enter a venue name with 1–20 characters.

### “Access Denied”

**Meaning:** The user does not have the permission required to save the plan or break.

**Fix:** Ask an administrator to check Edit permission on Add Time Slot or Add Interval, depending on what the user is saving.

### “Unauthorized Access”

**Meaning:** The user's session may have expired.

**Fix:** Sign in again and retry.

## Natural-language question patterns

The following are examples of how users may describe documented Day Planner problems. These are alternate phrasings, not additional product capabilities.

### Intent: plan a day or set playing hours

Possible user questions:
- “How do I plan the playing times for a day?”
- “Where do I set match timings?”
- “Tournament ka schedule time kaise set karun?”
- “I need to decide when matches start and finish.”
- “How do I set morning and afternoon sessions?”
- “Where do I configure the tables for a day?”

Answer direction:
Tell the user to select a venue, click a day, choose Plan Settings or Start Planning, set Day Duration, Single match duration, total tables and playing tables, then Save. Mention that matches are placed into slots separately using Open Scheduler.

### Intent: add a break

Possible user questions:
- “How do I add lunch time?”
- “Matches should stop for lunch.”
- “Lunch break kaise add karun?”
- “I need a tea or water break between matches.”
- “How can I stop matches during prize distribution?”

Answer direction:
Use Interval → Add new, choose a break name, set start and end in `HH:mm`, then Save. Explain that matches are not placed during breaks and up to five breaks can be added at once.

### Intent: calculate match capacity

Possible user questions:
- “How many matches can we play in one day?”
- “How can I fit more matches into the timetable?”
- “Can 50 matches fit into this day?”
- “Ek din mein kitne matches ho sakte hain?”
- “Why does it say only 20 matches can happen today?”

Answer direction:
Use the estimate shown on the page and explain that capacity depends on usable time slots and available tables. Suggest checking playing hours, match duration, breaks and table availability. Do not calculate an exact capacity unless the necessary plan values are provided or available.

### Intent: planner is locked or buttons do nothing

Possible user questions:
- “I cannot edit my plan.”
- “Day Planner ke buttons kaam nahi kar rahe.”
- “Why does Reset Planning do nothing?”
- “I can't add a venue or a break.”
- “The edit and delete icons don't work.”

Answer direction:
First check whether Enable Venue Registration is switched on in Venue Management. When it is enabled, Day Planner controls are disabled. If the issue is saving rather than controls not responding, check the user's permissions and whether the session has expired.

### Intent: reset or restore planning

Possible user questions:
- “What happens if I reset planning?”
- “Reset karne se matches delete honge?”
- “I want to start the timetable again.”
- “Can I undo a reset?”
- “My scheduled matches disappeared after reset.”

Answer direction:
Explain that Reset Planning clears the plan for the selected venue and removes matches already scheduled into its slots. Those matches must be scheduled again. The source documentation does not specify an Undo option for Reset Planning; do not promise that reset can be undone. If a single plan or break needs changing, suggest editing that item instead.

### Intent: deleted a plan or break by mistake

Possible user questions:
- “I deleted my plan accidentally.”
- “Break delete ho gaya, can I restore it?”
- “Where is the undo option?”

Answer direction:
Tell the user to click Undo within about five seconds after deletion. Do not confuse this short Undo action with Reset Planning, for which no Undo option is documented.

### Intent: add venue dates

Possible user questions:
- “No dates are showing.”
- “How do I add dates to a venue?”
- “I cannot select a date in the calendar.”
- “Venue ki dates add nahi ho rahi.”

Answer direction:
Use Venue → Add venue, enter a venue name and time zone, choose dates within the event's Start Date and End Date, click Apply, then Save or Update. For a League with no dates, explain that venue and corresponding dates must be added first.

### Intent: scheduled matches are affected by date changes

Possible user questions:
- “If I remove a date, what happens to the matches?”
- “Why is the system asking to reset the schedule?”
- “Matches already ho chuke hain; can I remove that date?”
- “My venue date change is rejected.”

Answer direction:
Explain that confirming the reset removes affected scheduled matches. If matches have already been played on a date, the date change is refused and the played date cannot be removed.

### Intent: access denied or sign-in issue

Possible user questions:
- “I can't save my plan.”
- “Access Denied aa raha hai.”
- “Why does it say Unauthorized Access?”
- “I can edit the screen but cannot save.”

Answer direction:
For Access Denied, explain the relevant permission: Add Time Slot for plans or Add Interval for breaks. For Unauthorized Access, ask the user to sign in again and retry.

## When to ask a follow-up question

Ask one focused question if the user's message does not identify the relevant problem.

- “It isn't working.” → “Are the Day Planner buttons not responding, or does saving show an error?”
- “I can't add a time.” → “Are you setting the day's playing hours, changing match duration, or adding a break?”
- “Matches are missing.” → “Did this happen after Reset Planning, after changing venue dates, or after editing match duration?”
- “I can't select a date.” → “Are you adding dates to a venue, and is the date inside the event's Start Date and End Date?”
- “I can't save.” → “What exact message appears: Access Denied, Unauthorized Access, or a validation message?”

Do not ask for the event ID unless checking live event data or a support workflow actually requires it.

## Frequently asked questions

### How do I plan the playing times for a day?

Choose the venue, click the day, select Plan Settings (or Start Planning if no plan exists), fill Day Duration, Single match duration and table settings, select the playing tables, then Save.

### How do I add a lunch break?

Click Interval, select Add new, choose Lunch, enter the start and end times in `HH:mm`, and click Save.

### How many breaks can I add?

Up to five break rows can be added at once.

### What is the allowed match duration?

Between 10 and 300 minutes.

### How many tables can I use?

The total number of tables can be between 1 and 300. At least one playing table must be selected.

### Why can I not add more overlapping plans?

A maximum of three plans may overlap in time. Change the times or edit an existing plan.

### What does Reset Planning do?

It clears the plan for the selected venue and removes matches already scheduled into its slots. Those matches must be scheduled again.

### I deleted a plan by mistake. Can I undo it?

Click Undo within about five seconds after deleting it.

### Why are all buttons on Day Planner doing nothing?

Check whether Enable Venue Registration is enabled on the Venue Management step. When it is on, the Day Planner controls listed in this guide do not work.

### Why can I not pick a date in the venue calendar?

Only dates within the event's Start Date and End Date can be selected.

### Where do I put matches into the slots?

Click Open Scheduler. Day Planner creates the available slots; the Scheduler is where matches are placed into them.

## Source-of-truth and escalation rules

- This document describes documented Day Planner behaviour. It does not confirm the current state of a particular event or venue.
- Do not claim to have inspected the current plan, schedule, permissions, dates or selected tables unless live application data is available.
- Organisation setup may affect whether the Day Planner step is available.
- Do not promise that Reset Planning can be undone; only the short Undo action after deleting an individual plan or break is documented.
- Do not claim an exact match capacity unless the required plan values are known.
- If a user reports a permission error, direct them to an administrator to check the relevant permission.
- If the user's issue depends on live schedule data or is not covered here, explain what needs to be checked in TMS or by support.
