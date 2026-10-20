---
doc_id: tms.schedular
title: Scheduler – place matches on tables and times, filter, reset and auto schedule
routes:
  - tms/schedular/:event_id/:participant_id/:category_id
aliases:
  - scheduler
  - scheduler page
  - schedular
  - schedule matches on tables
  - drag match to slot
  - match slots
  - auto schedule
  - reset scheduler
  - filter preferences scheduler
  - hide slots
  - remove slot
  - select tables
  - table grid
  - scheduler legend
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Scheduler page for?
  - How do I place a match on a table and time?
  - How do I auto schedule the matches?
  - What does Reset do on the Scheduler?
  - How do I filter the matches in the Scheduler?
  - Why does the Scheduler say "It seems that no matches have been created yet"?
  - What do the colours in the legend mean?
  - How do I hide a time slot?
  - Why does the Scheduler say "Slot not available"?
  - What is the difference between Reset and Reset Preferences?
  - Why is a match pending after Auto Schedule?
  - Why can't I schedule a later round first?
backend_sources:
  - gateway/src/routers/planner_router.py (get_day_schedule, assign_match_slots, auto_assign_match_slots, swap_match_slots, remove_match_slots, reset_match_slots, update_schedule_visibility, get_event_slots)
  - gateway/src/routers/match_router.py (matches)
  - gateway/src/routers/round_router.py (get_rounds)
  - tms/src/router/planner_router.py
  - tms/src/service/planner.py (assign_match_slots, swap_match_slots)
  - tms/src/service/auto_schedule_service.py (auto_assign_match_slots)
source_files:
  - src/app/modules/tms/schedular/schedular.component.html
  - src/app/modules/tms/schedular/schedular.component.ts
  - src/app/core/services/schedular-service/schedular.service.ts
  - src/app/core/constants/api-constant.ts
---

# Scheduler – place matches on tables and times

## Scope and purpose

The **Scheduler** page places event matches into venue table and time slots. Changes made here appear in the Planner and Day Planner. Umpire assignment is covered in the separate Scheduler Umpire guide (`tms.schedular.umpires`).

Route pattern: `tms/schedular/:event_id/:participant_id/:category_id`.

## Where to find it

Open **Schedule** from the sidebar.

## Opening the page and empty states

The page requires an event. If no event is selected, it shows a no-event-selected message.

The page displays the event category, its stages, and venue dates.

| Message | Meaning | Next step |
|---|---|---|
| `It seems that no matches have been created yet. Please create matches before scheduling them.` | The selected stage has no matches. | Select **Go to Fixtures** and create matches first. |
| `It appears that you have not created any daily plans. Please plan your day to schedule the matches effectively.` | The venue has no day plan. | Select **Go to Day Planner** and create a day plan. |
| `No matches found in all category` | The current filters hide all matches. | Review or reset the filters. |

## Header and top bar

- **Notify Users:** Opens the notification confirmation. It appears only when the event allows the notify action.
- **Live Match Center:** Opens the event's live match centre.
- **Category dropdown:** Toggles the selected category.
- **Category tabs:** Show child categories or sub-divisions and the number of children in brackets. The label is **Sub Division** for a league and **Sub Category** otherwise.
- **Stage tiles:** Tiles such as **S1**, **S2**, and so on select a stage. The stage shows its order.

## Venue, date, and month

- Use the **venue** dropdown to select a venue. Changing the venue reloads the available dates.
- Use the **month** and **year** dropdowns to filter the date list.
- Select a date in the date strip to display its slots.
- Use the arrows to move through the dates.

## Tabs: Matches, Umpire, and Day Planner

- **Matches:** The list of matches to place, alongside the table grid.
- **Umpire:** The umpire assignment view; see the Scheduler Umpire guide.
- **Day Planner:** Shows the venue's day plan, including intervals and breaks on the grid.

Matches are labelled according to stage format:
- Knockout stages use round labels, such as **R1**, or a position-match name.
- Group stages use group labels, such as **G1** and **G2**.
- Stages with format **2** show only the first two tabs.

## Match list (left panel)

- **Search:** Type to find a match; the list narrows as you type.
- **Checkbox:** Select an individual match.
- **Select all:** Select every match currently listed.
- **Round Name:** Shows the round.
- **Participants:** Shows the two players or teams with **VS** between them.
- **Group match count:** Shows the match count for a group.
- **Forfeited Player:** A forfeited participant is marked with a forfeited icon.
- **Leg dropdown:** Filters a round by its leg.

## Table grid (right panel)

Each table is a column. Its time slots are rows labelled with start and end times, for example `09:00–09:30`. Each column is headed **Table {n}**.

### Place a match

Drag a match from the list onto a free slot in the grid. The slot must be available and the placement must satisfy the scheduling rules.

### View slot details

Hover over a slot to see details such as:
- Participant type
- Category
- Round
- Match names
- Venue
- Date and time
- Umpires
- Mobile scorers
- Member association and club for each side

### Select and remove a slot

Select a slot by clicking it. **Remove** clears the matches from the selected slot after confirmation.

Confirmation message:

`Are you sure you want to delete this slot?`

### Select Tables for team matches

For a team match, use **Select Tables** to choose the number of tables:
- **With 1 Table**
- **With 2 Tables**

### Arrange and hide slots

- **Arrange horizontal** and **Arrange vertical** reorder the grid slots.
- **Hide** hides slots according to the chosen option, such as by time or by table and time.
- **Unhide** makes hidden slots visible again.
- Breaks, such as lunch, appear as rows with the break name and time.

## Legend

The legend explains slot state:
- **Unoccupied:** The slot is free.
- **Occupied:** The slot contains a match.
- **Selected:** The slot is selected.
- **Blocked:** The slot cannot be used.

Match tags identify:
- **S:** Stage
- **K:** Knockout
- **G:** Group
- **R:** Round
- **Category abbreviation:** The category label abbreviation

The legend can be minimised using its toggle.

The source material identifies these states and tags but does not specify particular colours. Do not assign colour meanings unless they are confirmed by the actual UI.

## Auto Schedule

Select **Auto Schedule** to place matches automatically.

- If matches are selected, only the selected matches are submitted for scheduling.
- If no matches are selected, the whole stage is submitted.
- Matches that cannot be placed are shown as pending for manual scheduling, with a reason.
- The pending reasons documented by the backend include:
  - `NO_HOME_PARTICIPANT`
  - `NO_HOME_VENUE_REGISTRATION`
  - `VENUE_AVAILABILITY_CANCELLED`
  - `NO_FEASIBLE_DATE`
  - `NO_FEASIBLE_SLOT`
- If auto scheduling fails, the server message is shown.

A pending match is not necessarily evidence that the entire auto-schedule operation failed. Check the pending reason for the individual match.

## Reset, Remove, and Undo

### Reset the scheduler

Select **Reset** to clear the slots for the selected venue. The page asks for confirmation:

`Are you sure you want to reset the entire scheduler for the selected venue?`

Confirmation actions:
- **Yes, Reset**
- **Cancel**

If nothing is scheduled, the page shows:

`No scheduled matches to reset`

### Remove a selected slot

**Remove** clears matches from the selected slot after confirmation. This is different from resetting the entire scheduler for the selected venue.

### Undo the last change

**Undo** reverts the last change. On success, the page displays:

`Action undone successfully!`

## Filter Preferences

Open **Filter Preferences** to filter the matches shown in the list and grid.

Available filters:
- Participant Type
- Category
- Stage
- Round
- Groups
- Umpire

Use **Add** to add each choice and the cross to remove it.

### Reset Preferences

**Reset Preferences** clears filters. The available reset options are:
- Date
- Group
- Participant Type
- Category
- Stage
- Round
- **ALL** (reset all matches)

A checkbox is used to confirm the selected reset option.

Filters change which matches are displayed in the list and grid; they do not change the schedule itself. **Reset Preferences** is therefore different from **Reset**, which clears scheduled slots for the selected venue.

## Messages and troubleshooting

| Message | Meaning / next step |
|---|---|
| `Match scheduled successfully` | The match was placed in a slot. |
| `Match swapped successfully` | Two matches were swapped successfully. |
| `Action undone successfully!` | The last change was undone. |
| `Please schedule a match to have an umpire assigned` | An umpire assignment was attempted before the match had a slot. Schedule the match first. |
| `Slot not available` | The selected slot cannot accept the match. Choose an available slot or review the scheduling conflict. |
| `It seems that one of the player is already playing at this time slot.` | A participant has another match at the same time. |
| `It looks like you haven't scheduled previous rounds. Are you sure you want to proceed with scheduling?` | A later round is being scheduled before an earlier round. Select **Yes** to continue if intended. |
| `Delete Slot?` | Confirmation before removing a slot; choose **Yes, Delete** or cancel. |
| `Delete Umpire?` | Confirmation before removing an umpire; see the Scheduler Umpire guide. |

The server's message is shown when it provides one. Some backend conflict messages may not have English translations and may appear as raw keys; see the Scheduler API guide for backend validation details.

## Frequently asked questions

### What is the Scheduler page for?

It places event matches into venue tables and time slots. Its schedule changes are reflected in the Planner and Day Planner.

### How do I place a match?

Find the match in the left panel and drag it onto an available slot in the table grid.

### How do I auto schedule matches?

Select the matches to schedule and click **Auto Schedule**. If no matches are selected, the whole stage is submitted for auto scheduling. Matches that cannot be placed are returned as pending with reasons.

### What does Reset do?

It clears scheduled slots for the selected venue after confirmation. **Undo** reverts the last change. **Reset Preferences** only clears the selected filters.

### How do I filter matches?

Open **Filter Preferences**, add the desired filters, and remove unwanted filter choices with their cross controls. Use **Reset Preferences** to clear filters.

### Why does the page say no matches have been created yet?

The selected stage has no matches. Select **Go to Fixtures** and create the matches before scheduling.

### Why does the page say no daily plans have been created?

The venue has no day plan. Select **Go to Day Planner** and create a plan before scheduling.

### How do I hide a time slot?

Select **Hide** and choose the applicable option, such as time or table and time. Select **Unhide** to show the slots again.

### Why can't I schedule a match in a slot?

The slot may be unavailable or the assignment may violate scheduling rules, such as a participant already playing at that time. Check the displayed message and the Scheduler API guide for the relevant validation.

## Natural-language and Hinglish query patterns

Treat these as equivalent intents when retrieving this document:

- "Scheduler page ka use kya hai?"
- "Match ko table aur time slot par kaise place karun?"
- "Drag karke match slot mein kyun nahi ja raha?"
- "Auto Schedule kaise chalana hai?"
- "Auto Schedule ke baad match pending kyun hai?"
- "Reset aur Reset Preferences mein kya difference hai?"
- "Scheduler mein filters kaise lagayein?"
- "No matches have been created yet ka matlab kya hai?"
- "Daily plan nahi bana hai to kya karun?"
- "Unoccupied, Occupied, Selected aur Blocked ka matlab kya hai?"
- "Time slot ko Hide ya Unhide kaise karun?"
- "Previous round schedule nahi hua to warning kyun aati hai?"
- "Slot not available error kyun aa raha hai?"

## Answering guidance for the TMS assistant

1. Identify whether the user is asking about navigation, match placement, auto scheduling, reset/remove, filters, slot visibility, or a validation message.
2. Use the exact UI labels and messages documented here.
3. Distinguish the empty-stage message from the missing-day-plan message and from a filter result with no matches.
4. Distinguish **Reset** (clears scheduled slots) from **Reset Preferences** (clears filters) and **Remove** (clears the selected slot).
5. For auto-schedule pending matches, explain the specific pending reason returned by the backend; do not guess.
6. For conflicts or unavailable slots, use the message returned by the server and the Scheduler API guide.
7. Do not invent the meaning of slot colours; the source lists state labels but does not specify colour mappings.
8. For umpire assignment details, refer to `tms.schedular.umpires`.
9. Do not claim that filters alter the actual schedule; they affect the displayed matches.

## Source references

- Scheduler gateway endpoints: `gateway/src/routers/planner_router.py`
- Match list: `gateway/src/routers/match_router.py`
- Rounds: `gateway/src/routers/round_router.py` (`get_rounds`)
- TMS planner router: `tms/src/router/planner_router.py`
- Slot assignment and swapping: `tms/src/service/planner.py`
- Auto scheduling: `tms/src/service/auto_schedule_service.py`
- Scheduler UI: `src/app/modules/tms/schedular/schedular.component.html`
- Scheduler component logic: `src/app/modules/tms/schedular/schedular.component.ts`
- Scheduler service: `src/app/core/services/schedular-service/schedular.service.ts`
- API constants: `src/app/core/constants/api-constant.ts`
