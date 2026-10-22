---
doc_id: tms.fixture.schedule-access
title: Scheduling matches to tables and times, and match access for users and roles
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
  - match access sidebar
  - give permission to write
  - auto access
  - match permission
  - match organiser
  - select roles to set permissions
  - select users
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I schedule matches to tables and times?
  - What is the difference between By Table and By Duration?
  - Why does the schedule say a table conflict was detected?
  - How do I clear the slot of a match?
  - How do I give a user access to a match?
  - What is auto access?
  - How do I change the organiser of a match?
backend_sources:
  - gateway/src/routers/planner_router.py (get_matches_scheduling_details, bulk_schedule_matches_from_fixture, remove_match_slots)
  - gateway/src/routers/resource_permissions_router.py (get_resource_user_roles_feature_permissions, bulk_upsert_resource_user_roles_feature_permissions, grant_auto_access_to_parents, revoke_resource_user_roles_feature_permissions)
  - gateway/src/routers/role_router.py (get_roles)
  - gateway/src/routers/user_router.py (list_all_users)
source_files:
  - src/app/shared/schedule-popup/schedule-popup.component.html
  - src/app/shared/schedule-popup/schedule-popup.component.ts
  - src/app/shared/match-access-sidebar/match-access-sidebar.component.html
  - src/app/shared/match-access-sidebar/match-access-sidebar.component.ts
  - src/assets/i18n/en.json
---
# Scheduling matches and match access

Two screens from the fixtures page sit beside the fixture: the **Schedule Matches** popup, which puts matches into table and time slots, and the **Match Access** sidebar, which gives users and roles permission on each match. Both take the matches you select in the fixture tree or the match list.

## Schedule Matches popup

- Title: **Schedule Matches**. The intro says the slots reflect in the Planner and Scheduler.
- Select the matches first. With no match selected the popup says: "No matches selected. Please select matches from the fixture tree to schedule."
- **Global settings** (**GLOBAL SETTINGS**) apply one value to all the selected rows:
  - **Match Time** (date and time picker), and the **Venue** and **Table** choices.
  - **Apply** copies the global settings to the rows. **Add** (shown when you are adding a new venue) creates a venue in the list.
- **Schedule Criteria** chooses how the slots are made:
  - **By Table** – each match is put on a table; the time follows the table.
  - **By Duration** – each match gets a match duration; the next match starts after it.
- Each row shows the round (**Rnd** for knockout, **Grp** for group stage), the **Match ID**, the **Participants** (two players or teams, with **VS**), the **Venue Name**, **Match Date**, **Match Time**, **Match Duration**, and **Match Table**.
- Per row: change the time, the table or the venue. **Clear** removes the slot of that row.
- **Reset** clears all the slots in the popup. **Save** writes the schedule.

## Schedule messages

- A duplicate slot in the list shows its own error line under the list.
- A conflict is shown as "Scheduling failed: Participant conflict detected. No matches were scheduled." or "Table conflict". When the server gives no detail: "Scheduling failed due to conflicts. No matches were scheduled."
- A player already playing at that time is reported as "It seems that one of the player is already playing at this time slot."
- A blocked interval that cannot be checked: "Unable to validate blocked intervals. Please try again."
- Clearing a slot: "Slot removed successfully"; clearing several: "Slots removed successfully"; a failure: "Failed to remove slots".
- Clearing selected matches: "Selected matches cleared successfully".
- Reset with nothing scheduled: "No scheduled matches to reset".
- A save that fails with no message from the server shows "Something went wrong."

## Match Access sidebar

- Title: **Match Access**. It has tabs for the access you set (for example **Auto Access** and the manual tabs). Each tab can be opened from the sidebar.
- **Select match** (step 1) chooses the matches. Without one: "No Match is selected. Please select at least one match to set permissions manually. To set auto access, go to the Auto Access tab."
- **Select Roles** (step 2) chooses the roles. Without one: "No Role is selected. Please select at least one Role to set permissions manually."
- **Select Users** lists the users of the chosen role (**S.No**, **User**, **Role**) with a checkbox for each user and **Select all**.
- **Next** and **Back** move between the steps.
- **Give Permission to write** saves the permission for the chosen users on the chosen matches. It is greyed out until the form is valid.
- **Save** (manual view) saves the access for the selected users; a confirmation dialog is shown first.

## Manual match access (organiser)

- The list of users with scoring permission from Event Access is shown. Choose which users are the organisers of the match.
- **Select Match to Edit Organiser** lists the matches; without one: "No Match is selected. Please select at least one match to set manual access."
- The **Reset** button clears the selection; it is greyed out when no match is selected.
- **Save** in the update view is greyed out until a change is made.

## Auto access

- **Select Team & Organisation** lists the teams or organisations to give automatic access to.
- Choose one option (radio button), then **Select Parent Role** (required) and **All Role** to filter the users.
- Auto access is applied through the parent role you choose; check the result in the match list after saving.

## Messages

- "Please select at least one match to update permissions" – choose a match first.
- "Please select a parent role" – the parent role is required for auto access.
- "Please select an end date" and "End date must be after start date" – the date range of the access is not valid.
- "Match Start time is not available" – the match has no start time yet; set the time first.
- Server messages are shown on the screen when a save fails.

## Permissions

- Changing schedules or access is limited by the user's permissions on the event; when refused, the server message is shown.
- Without the permission the change is refused.

## Frequently asked questions

**How do I schedule matches to tables and times?** Select the matches in the fixture tree, then open **Schedule Matches**. Set the **Match Time**, **Venue** and **Table** (use **GLOBAL SETTINGS** and **Apply** to set all rows at once), choose the **Schedule Criteria** and click **Save**.

**What is the difference between By Table and By Duration?** With **By Table** each match is put on a table and its time follows that table. With **By Duration** each match gets a match duration and the next match starts after it.

**Why does the schedule say a table conflict was detected?** Another match already uses that table at that time, so no matches were scheduled. Choose another table or time for the conflicting match and save again.

**How do I clear the slot of a match?** In **Schedule Matches**, click **Clear** on the match's row to remove its slot. "Slot removed successfully" confirms it. **Reset** clears all the slots in the popup.

**How do I give a user access to a match?** Open **Match Access**, select the matches (step 1) and the roles (step 2), tick the users in **Select Users**, then click **Give Permission to write**.

**What is auto access?** Auto access gives match access through a parent role. On the **Auto Access** tab, choose the team or organisation, select the **Parent Role** (and filter with **All Role**), then save, and check the result in the match list.

**How do I change the organiser of a match?** In **Match Access**, use **Select Match to Edit Organiser** to choose the matches, pick the organisers from the users with scoring permission, then click **Save**.
