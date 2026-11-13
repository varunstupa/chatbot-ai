---
doc_id: tms.fixture.schedule-access
title: Scheduling matches to tables and times (Schedule Matches popup)
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - schedule matches
  - schedule popup
  - schedule criteria
  - by table
  - by duration
  - global settings schedule
  - match time
  - match table
  - remove slot
  - reset slots
  - match access
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I schedule matches to tables and times?
  - What is the difference between By Table and By Duration?
  - Why does the schedule say a table conflict was detected?
  - How do I clear the slot of a match?
  - Where did Match Access go?
backend_sources:
  - gateway/src/routers/planner_router.py (get_matches_scheduling_details, bulk_schedule_matches_from_fixture, remove_match_slots)
  - gateway/src/routers/resource_permissions_router.py (get_resource_user_roles_feature_permissions, bulk_upsert_resource_user_roles_feature_permissions, grant_auto_access_to_parents, revoke_resource_user_roles_feature_permissions)
  - gateway/src/routers/role_router.py (get_roles)
  - gateway/src/routers/user_router.py (list_all_users)
source_files:
  - src/app/shared/schedule-popup/schedule-popup.component.html
  - src/app/shared/schedule-popup/schedule-popup.component.ts
  - src/app/shared/confirm-popup/confirm-popup.service.ts
  - src/app/shared/point-system/point-system.component.html
  - src/app/modules/tms/fixture-configuration/fixture-configuration.component.html
  - src/assets/i18n/en.json
---
# Scheduling matches

The **Schedule Matches** popup on the fixtures page puts the matches you select in the fixture tree or the match list into venue, table and time slots. Match access (who may score which matches) is no longer set from the fixtures page; it is now in **Game Settings** (see the section below).

## Schedule Matches popup

- Title: **Schedule Matches**. The intro says "Select the following details to schedule this match. These changes will reflect in Planner & Scheduler."
- Select the matches first. With no match selected the popup says: "No matches selected. Please select matches from the fixture tree to schedule."
- Each row shows the round or leg (**Rnd** for knockout, **Grp** with the group for a group stage), the **Match ID**, the **Participants** (two players or teams, with **VS**), the **Venue Name**, **Match Date**, **Match Time**, **Match Duration**, **Match Table** and **Actions**.
- Per row: type or pick the venue ("Add / Select Venue"), the date, the time (24-hour), the duration and the table. **Clear** removes the slot of that row ("Slot removed successfully" when it was already scheduled).
- **Reset** clears all the saved slots of the listed matches. **Save** writes the schedule and closes the popup.

## Schedule Matches popup – GLOBAL SETTINGS and Schedule Criteria

- **GLOBAL SETTINGS** is shown only when more than one match is selected. Under **Basic Details** choose the venue and the date; **Apply** copies them to every row.
- The date can only be chosen within the event's start and end dates.
- **Schedule Criteria** chooses which value **Apply** copies:
  - **By Table** – a **Match Table** for all rows (clears the time and duration of the rows).
  - **By Duration** – a **Match Time** and a **Duration** for all rows (clears the table of the rows).
- A venue that does not exist yet can be typed in the venue box; "You are adding a new entry…" appears and **Add** creates the venue for the event.

## Schedule Matches popup – field rules

- Every row needs a venue, date, time, duration and table before **Save** works; missing fields are outlined in red.
- **Match Table** accepts only numbers and commas (several tables, for example 1,2).
- **Match Duration** accepts only numbers (optionally ending in "m") and is capped at 420 minutes.
- Two rows with the same venue, date, time and table are both outlined, with the message "Either tables have to be different or timings. Both cannot be same at the same time."
- A slot that overlaps a blocked interval of the venue's planner is refused: "Cannot schedule during blocked interval ({{name}}): {{start}} - {{end}} on {{date}}."

## Schedule messages

- A conflict is shown as "Scheduling failed: Participant conflict detected. No matches were scheduled." or "Table conflict"; the conflicting participants or table are outlined in the row. When the server gives no detail: "Scheduling failed due to conflicts. No matches were scheduled."
- On a conflict a warning popup titled **Alert!** shows the server message (or "It seems that one of the player is already playing at this time slot."). **Continue** schedules anyway, overriding the conflict; **Cancel** goes back to the popup. Only player conflicts can be overridden; a table already used at that time is always refused.
- A blocked interval that cannot be checked: "Unable to validate blocked intervals. Please try again."
- Clearing a slot: "Slot removed successfully"; a failure: the server message or "Failed to clear slot".
- Reset: "Slots removed successfully"; a failure: "Failed to remove slots".
- Reset with nothing scheduled: "No scheduled matches to reset".
- A save that fails with no message from the server shows "Something went wrong."

## Schedule messages – server checks

- The server checks every row before saving anything and stops at the first problem: a player already in another match at that time, a player twice in overlapping rows, a table already taken at that venue and time, a date outside the event dates ("Match date … is outside event date range …"), or a match or venue that no longer exists.
- If the event uses Match Call Out, saving is refused: "This event uses Match Call Out: time slots cannot be assigned".

## Match Access – moved to Game Settings

- The **Match Access** link and sidebar are no longer on the fixtures page.
- Match access is now set in **Game Settings** › **Scoring Management** › **Scoring Access** (the **Fixture Settings** panel). See the Game Settings guide for the Fixtures screen.
- For league events a notice next to **Game Settings** reads "Match Access is now available inside Game Settings › Scoring Management › Scoring Access." Close it with the X; it stays hidden for the rest of the session.

## Permissions

- Saving the schedule needs **Edit** permission on **Add Time Slot**. Clearing or resetting slots needs **Edit** permission on **Schedule Match Access**.
- Without the permission the change is refused with "Access Denied".

## Frequently asked questions

**How do I schedule matches to tables and times?** Select the matches in the fixture tree, then open **Schedule Matches**. Set the **Match Time**, **Venue** and **Table** (use **GLOBAL SETTINGS** and **Apply** to set all rows at once), choose the **Schedule Criteria** and click **Save**.

**What is the difference between By Table and By Duration?** With **By Table** each match is put on a table and its time follows that table. With **By Duration** each match gets a match duration and the next match starts after it.

**Why does the schedule say a table conflict was detected?** Another match already uses that table at that time, so no matches were scheduled. **Continue** cannot override a table conflict. Choose another table or time for the conflicting match and save again.

**Do scheduled matches show up in the Day Planner?** Yes. Saving creates (or reuses) a plan for each venue, date and match duration, with slots at the chosen times, and adds the date to the venue if needed.

**How do I clear the slot of a match?** In **Schedule Matches**, click **Clear** on the match's row to remove its slot. "Slot removed successfully" confirms it. **Reset** clears all the slots in the popup.

## Frequently asked questions – match access

**Where did Match Access go?** It is now inside **Game Settings** › **Scoring Management** › **Scoring Access**. The old Match Access sidebar on the fixtures page has been removed.
