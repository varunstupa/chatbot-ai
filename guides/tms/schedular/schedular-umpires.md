---
doc_id: tms.schedular.umpires
title: Scheduler umpire tab – assign umpires to matches, auto assign umpires and umpiring settings
routes:
  - tms/schedular/:event_id/:participant_id/:category_id
aliases:
  - scheduler umpire
  - umpire tab
  - assign umpire
  - assign umpire to match
  - auto assign umpire
  - umpiring settings
  - add umpire manually
  - remove umpire
  - reset umpire
  - umpire name list
  - umpire per table
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I assign an umpire to a match in the Scheduler?
  - How do I assign one umpire to all slots of a table?
  - How do I auto assign umpires?
  - Why does the Scheduler say "No match is assigned to this slot"?
  - Why can I not add an umpire to a table?
  - How do I delete an umpire from a match?
  - What are the umpiring settings?
  - Why can't I assign a third umpire to a match?
  - What does "Please schedule a match to have an umpire assigned" mean?
  - How do I undo an umpire assignment?
backend_sources:
  - gateway/src/routers/planner_router.py (assign_event_official_match, assign_event_official_match_ids, remove_event_official_match, reset_event_official_match)
  - gateway/src/routers/player_umpiring_router.py (umpire settings and event officials)
  - tms/src/router/planner_router.py
  - tms/src/service/event_official_service.py (assign, assign by ids, remove, reset)
source_files:
  - src/app/modules/tms/schedular/schedular.component.html
  - src/app/modules/tms/schedular/schedular.component.ts
  - src/app/core/services/schedular-service/schedular.service.ts
  - src/app/core/constants/api-constant.ts
answer_notes: |
  Answering guidance for the TMS assistant:
  1. Identify whether the user wants to assign to selected matches, assign across a table, auto-assign, change settings, remove an umpire, undo, or reset assignments.
  2. Check the key prerequisite: the match must already be scheduled in a slot.
  3. Explain the difference between a match without a slot and an empty slot without a match.
  4. State the two-umpire maximum when the user asks why another umpire cannot be added.
  5. For auto assignment, say it follows the event's Umpiring Settings, but do not invent the algorithm or setting fields.
  6. Use exact UI labels and validation messages from this guide.
  7. For server-side failures not explained here, refer to the Scheduler API guide rather than guessing.
---

# Scheduler umpire tab

## Scope and prerequisite

The **Umpire** tab in the Scheduler assigns umpires (event officials) to matches that are already scheduled on a table and time.

**A match must have an assigned slot before an umpire can be assigned to it.** If the match has no slot, schedule it first using the Scheduler guide.

The tab supports selecting umpires and matches, assigning an umpire to all scheduled matches on a table, auto-assigning umpires, configuring event-level umpiring settings, removing an umpire, undoing the last change, and resetting assignments.

## Quick reference

- **Assign to a match:** Select one or more umpires and matches, then select **Save**.
- **Assign to a table:** Choose **Assign to all slots on a specific Table**, select a table, and save.
- **Auto assign:** Uses the event's umpiring settings and works on matches that are already scheduled.
- **Maximum umpires:** Two umpires can be assigned to a match.
- **Empty slot:** Cannot receive an umpire until a match is assigned to it.
- **Remove:** Use the remove action beside the umpire and confirm the deletion.
- **Reset:** Clears umpire assignments after confirmation.

## The umpire view

The tab has two main lists:

- **Umpire Name:** The list of officials on the left, with a checkbox for each and a **Select all** option.
- **Matches:** The list on the right, with a match count, for example **Matches (12)**.

Each list has its own **Search** box.

Select a slot in the grid to choose the match whose umpire assignments you want to change.

A match can have up to **two umpires**. A match that already has two umpires cannot take another.

## Assign umpires to matches

1. Select one or more umpires in the umpire list.
2. Select one or more matches in the match list.
3. Select **Save**.

Each selected umpire is assigned to the selected matches, subject to the slot prerequisite and the two-umpire limit.

### Undo the last change

Select **Undo** to revert the last change.

Success message:

`Action undone successfully!`

### Match has no slot

If the match is not scheduled, the page displays:

`Please schedule a match to have an umpire assigned`

Schedule the match first, then retry the assignment.

### Slot has no match

If the selected slot is empty, the page displays:

`No match is assigned to this slot. Please assign one to add an umpire.`

The page offers two actions:
- **Go to Matches:** Opens the match list.
- **Add Umpire Manually:** Opens the manual-entry flow.

The key distinction is that an unscheduled match needs a slot, while an empty slot has no match assigned to it.

## Assign one umpire to all slots on a table

Use **Assign to all slots on a specific Table** to assign one umpire across the scheduled matches on a selected table.

1. Open the table-assignment dialog.
2. Select a table.
3. Review **Applied to**, which shows the number of matches affected, and the listed slots, such as **Slots on Table 2**.
4. Select **Save**.

The umpire is assigned to every match on that table, subject to the maximum of two umpires per match.

If there are no matches on the table, or all matches already have two umpires, the page displays:

`No Match Scheduled For this table or all matches already have 2 umpires assigned`

## Auto Assign Umpire

Select **Auto Assign Umpire** to open the automatic assignment dialog.

- Auto assignment works on matches that are already scheduled.
- The assignment follows the event's configured **Umpiring Settings**.

The source material does not specify the individual auto-assignment algorithm or the available umpiring-setting fields. Do not invent those details; refer to the event's settings or the relevant implementation if a more precise explanation is needed.

## Umpiring Settings

Select **Umpiring Settings** to open a side panel containing the umpire rules for the event.

The settings are saved for the event and are used by auto assignment.

This source does not list the individual settings or their possible values.

## Remove and reset umpire assignments

### Remove one umpire

Use the cross/remove action beside an umpire assigned to a match.

Confirmation dialog:
- Title: **Delete Umpire?**
- Message: `Are you sure you want to delete this umpire? All the changes made will be lost.`
- Actions: **Yes, Delete** and **Cancel**

Select **Yes, Delete** to confirm removal, or **Cancel** to leave the assignment unchanged.

### Reset umpire assignments

Reset clears the umpire assignments. The screen asks for confirmation before sending the reset request.

The source material does not specify more granular reset behavior, so do not assume that reset affects only a particular table or date unless the UI selection makes that scope explicit.

## Messages and troubleshooting

| Message | Meaning | What to do |
|---|---|---|
| `Please schedule a match to have an umpire assigned` | The match has no slot. | Schedule the match first, then assign the umpire. |
| `No match is assigned to this slot. Please assign one to add an umpire.` | The selected slot is empty. | Assign a match to the slot, or use the offered navigation/manual-entry action. |
| `No Match Scheduled For this table or all matches already have 2 umpires assigned` | There are no scheduled matches on the selected table, or all of them already have two umpires. | Choose a table with eligible scheduled matches, or check current assignments. |
| `Delete Umpire?` | Confirmation before removing an umpire. | Select **Yes, Delete** or **Cancel**. |
| `Action undone successfully!` | The last change was undone. | No further action is needed unless you want to make another change. |

Server-side assignment, removal, and reset messages are documented in the Scheduler API guide. The exact server response depends on the endpoint and request.

## Frequently asked questions

### How do I assign an umpire to a match?

Schedule the match first. In the Umpire tab, select the umpire and the match, then select **Save**.

### How do I assign one umpire to a whole table?

Open **Assign to all slots on a specific Table**, select the table, check the **Applied to** count and slots, then select **Save**.

### How do I auto-assign umpires?

Select **Auto Assign Umpire**. The operation applies to already-scheduled matches and follows the event's **Umpiring Settings**.

### Why can't I add an umpire to a slot?

If the slot is empty, the page displays `No match is assigned to this slot. Please assign one to add an umpire.` Assign a match to the slot first.

If a match exists but has no scheduled slot, the page displays `Please schedule a match to have an umpire assigned`. Schedule the match first.

### Why can't I assign another umpire?

A match can have at most two umpires. If it already has two, another umpire cannot be assigned.

### How do I remove an umpire from a match?

Use the remove/cross action beside the umpire, then select **Yes, Delete** in the confirmation dialog.

### What are Umpiring Settings?

They are event-level rules shown in the **Umpiring Settings** side panel. Auto assignment follows these settings. The individual fields are not detailed in this document.

### How do I undo an assignment?

Select **Undo**. A successful undo displays `Action undone successfully!`.

### Why does the Scheduler say "No match is assigned to this slot"?

The selected slot is empty. Assign a match to the slot first (**Go to Matches**), or use **Add Umpire Manually**.

### Why can't I assign a third umpire to a match?

A match can have at most two umpires. If it already has two, remove one before assigning another.

### What does "Please schedule a match to have an umpire assigned" mean?

The match has no table and time slot yet. Schedule the match first, then assign the umpire.

## Natural-language and Hinglish query patterns

Treat these as equivalent intents when retrieving this document:

- "Scheduler mein umpire kaise assign karun?"
- "Ek umpire ko table ke sabhi matches par kaise lagayein?"
- "Auto Assign Umpire kaise kaam karta hai?"
- "No match is assigned to this slot ka matlab kya hai?"
- "Match schedule kiye bina umpire assign kyun nahi hota?"
- "Ek match mein third umpire add kyun nahi ho raha?"
- "Umpire ko match se remove kaise karun?"
- "Umpiring Settings kahan milti hain?"
- "Umpire assignment undo kaise karun?"
- "Table par koi match scheduled nahi hai to kya karun?"

## Source references

- Gateway official assignment/removal/reset: `gateway/src/routers/planner_router.py`
- Umpiring settings and event officials: `gateway/src/routers/player_umpiring_router.py`
- TMS planner router: `tms/src/router/planner_router.py`
- Official assignment service: `tms/src/service/event_official_service.py`
- Scheduler UI: `src/app/modules/tms/schedular/schedular.component.html`
- Scheduler logic: `src/app/modules/tms/schedular/schedular.component.ts`
- Scheduler service: `src/app/core/services/schedular-service/schedular.service.ts`
- API constants: `src/app/core/constants/api-constant.ts`
