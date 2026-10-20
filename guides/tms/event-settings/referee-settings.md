---
doc_id: tms.event-settings.referee-settings
title: Referee Settings page
routes:
  - tms/event-settings/refree-settings/:event_id
aliases:
  - referee settings
  - refree settings
  - referee registration settings
  - referee step
  - add referee
  - assign referee
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I open referee registration for this event?
  - How do I add a referee manually?
  - How do I assign a referee to a match?
  - Why does my referee not appear in the list?
  - Why do I get "Registration Closed" when I add a referee?
backend_sources:
  - gateway/src/routers/events_router.py (update_event_referee_registration_settings)
  - gateway/src/routers/registration_router.py (register_event_referee, get_event_officials, update_event_officials, is_event_official_registration_validations, event_official_verification_logic)
  - gateway/src/routers/planner_router.py (assign_event_official_match_ids, remove_event_official_match)
  - tms/src/service/event_official_service.py (assign_event_official_match_ids, remove_event_official_match, register_event_officials, update_event_officials)
  - tms/src/crud/event_official_crud.py (register_event_officials, resolve_assignable_official_id_by_user_role, remove_event_official_match_mappings)
source_files:
  - src/app/modules/tms/refree-settings/refree-settings.component.ts
  - src/app/modules/tms/refree-settings/refree-settings.component.html
  - src/app/modules/tms/events-settings/events-settings.component.ts
  - src/app/core/services/registration-service/registration-service.service.ts
  - src/app/core/services/tournament-config/tournament-config.service.ts
  - src/app/core/utils/permission_directive/permissions.directive.ts
---
# Referee Settings page – user guide

This guide describes the **Referee Settings** step of an event in the Stupa Event Management System (admin panel). On this page the organiser sets up online registration for referees, adds referees by hand, and (for a League) assigns referees to matches.

## Where to find it

Open **Event** from the sidebar, then click **Referee Settings** in the row of setup steps at the top of the page.

## Referee Settings page: where it is and what it is for

- Page address: `/tms/event-settings/refree-settings/<event id>`, for example `/tms/event-settings/refree-settings/3453`. The address is spelled "refree".
- It is the **Referee Settings** step in the row of event setup steps. The step is only shown for organisations that use it.
- Page heading: **Referee Registration Settings**, with the text "The tournament organizer can control the registration settings and opt to manually close registrations in any category, regardless of the registration deadlines."
- On this page you can:
  - toggle on online registration for referees and set its rules (**Settings**),
  - add a referee yourself (**Add**),
  - remove a referee and bring a removed referee back (**Deleted**),
  - see each referee's bank details,
  - for a League: assign referees to matches.
- The page looks different for the two event types:
  - **Tournament**: a list of referees per event day.
  - **League**: a list of matches with a Referee column for each match.
- Referees and umpires are managed separately. Umpires are on the **Umpire Settings** step.

## Referee Settings page: buttons at the top

Next to the **Search by Name** box there are four buttons (Tournament) or three buttons (League):

- **Filter** – show only some referees (see "Filtering the referee list").
- **Settings** – opens the referee registration side panel.
- **Add** – opens the **Add Referee Manually** side panel.
- **Deleted** (Tournament only) – shows referees that were removed.

These buttons are greyed out when your role does not have **Edit** permission on **Referee Registration Settings**. Ask an administrator to give it on the event's **Access-Control** step or in role management.

## Referee settings side panel: switching on referee registration

Click **Settings**. The side panel **Referee Settings** opens (for a League its heading reads **Refree Settings**), with the text "You can manage referees for your event and enable online registration for them."

1. Turn on the **Registration** toggle ("You can enable registration, and the referees will be able to submit their registration online via the platform."). All sections below stay greyed out while the toggle is off.
2. Fill in **Eligible Role**, **Registration Date**, **Amount Type**, **Per Match Referee**, and optionally **Referee Verification** (explained in the next sections).
3. Click **Save**. The message "Settings updated successfully" confirms it.

Rules:
- Fields marked `*` are mandatory. If one is empty, the message is "Please fill all required details", and the field shows "*Required".
- **Save** is greyed out while the **Registration** toggle is off. Turning the toggle off therefore cannot be saved from this panel.
- Saved settings are loaded again the next time you open the panel.

## Referee settings side panel: Eligible Role and Registration Date

**\*Eligible Role** – "Select the user role that you want to allow to apply as a referee for this event". Tick one or more roles in **Select Role**. Only users with one of these roles can register as referee; an organiser adding a user with another role gets "Registration Not Allowed For Role" (the main administrator account is not checked).

**\*Registration Date** – "Select the start date and end date to specify when you want to enable referee registration, including the date to start and the date to close registrations."
- **Registration Start Date** and **Registration End Date** are picked in a calendar (DD/MM/YYYY). Both are mandatory.
- Only dates **before the event's start date** can be picked. The event start date and every later date are greyed out.
- Outside these dates referees cannot register, and organisers (except the main administrator) cannot add, remove or restore referees on this page: "Registration Not Started" before the start date, "Registration Closed" after the end date.
- To add or change referees after the end date, move the **Registration End Date** in **Settings**, or ask the main administrator.

## Referee settings side panel: Amount Type and Per Match Referee

**\*Amount Type** – **Free** or **Paid**. Tooltip: "You can select 'Paid', which means the referee can enter the amount they wish to request per match. In the 'Free' scenario, the referee cannot enter the amount they wish to receive per match."
- With **Paid**, the panel lists the bank details involved: Account Name Holder, Postal address of Bank, IBAN number, Swift-BIC number.
- On this page the cost field in **Add Referee Manually** stays editable with either type, and the **Cost** column is always shown.

**\*Per Match Referee** – **1** or **2** ("You can select the number of referees required per match."). The default is 1.
- It sets how many referees one match can have. Assigning more is refused with "Assignment would exceed per_match_limit for one or more matches".
- For a League, **2** adds a **Referee 2** and a **Cost 2** column to the match table.

## Referee settings side panel: Referee Verification (optional)

**Referee Verification** – "Select the user role who will verify the details for the referees, or you can select any specific user as well."

- **Verifier 1** and **Verifier 2** each have two dropdowns: first a role, then (optionally) a specific user with that role.
- If a role is chosen without a user, the verifier is taken from the referee's own linked (parent) user of that role, when there is one.
- With verifiers set, a new referee registration is **pending** until it is approved. With both verifiers set, both must accept. Verifiers approve requests on the **Event Referee Request** page (`/admin/manage/referee`).
- Without verifiers, registrations are accepted straight away.
- Registrations made by the main administrator account are always accepted.
- **The referee list on this page only shows accepted referees.** A pending referee appears after approval.

## Tournament: the referee list and day tabs

For a Tournament the page shows a row of day tabs and a table.

- Day tabs: **ALL / DAYS** first, then one tab per event day ("Day 1", "Day 2", … with the date). Use the arrows to scroll. Click a tab to see the referees registered for that day; **ALL** shows every day.
- Table columns: **S.No**, **Name** (with the e-mail below), **Cost**, **Date**, **DAYS**, **Status**, **Bank Details**, **Action**.
- A referee registered for several days has one row per day.
- Click a column heading to sort. The table shows 10 rows per page; use the page buttons below it.
- **Search by Name** filters the list by referee name as you type.
- "No record found" means no accepted referee matches the tab, search or filter.

## Tournament: adding a referee manually

1. Click **Add**. The side panel **Add Referee Manually** opens ("Search for the referee you want to add to your event.").
2. **Search Referee** – open **Search to Add Registered Referee** and pick a user. Type in the search box to narrow the list. "No result found" means no user matches.
3. **Cost per Day** – the amount per day ("Enter the amount you want to allocate to the referee.").
4. **Days** – open the day list (its placeholder also reads "Search to Add Registered Referee") and tick the days the referee is available ("Select the days you want the referee to be available for your event.").
5. Click **Add**. "Referee Added Successfully." confirms it and the list reloads.

Notes:
- The list offers users of the roles your organisation allows as referees. A user whose role is not in the event's **Eligible Role** is refused with "Registration Not Allowed For Role".
- Pick at least one day. One row per day is created.
- The person is not in the list yet? Click **Add New Referee Account** first (see "Creating a new referee account").
- With verifiers set, the added referee stays pending and does not appear in the list until approved.

## Tournament: removing and restoring a referee

- **Remove**: click the bin icon in the **Action** column. The question "Are you sure you want to Delete registration of <name>?" appears. Confirm to remove. "Referee deleted successfully" confirms it.
- Removing a referee also removes that referee from the matches they were assigned to on that date.
- **Restore**: click **Deleted** to see removed referees (heading **Deleted Referee**). Click the **+** icon on a row and confirm "Are you sure you want to Add registration of <name>?". "Referee Added Successfully." confirms it.
- Click the arrow left of **Deleted Referee** to return to the normal list.
- Removing and restoring follow the registration rules: outside the registration dates, or with Registration switched off, they fail with "Registration Closed", "Registration Not Started" or "Registration Not Allowed" (except for the main administrator).

## League: assigning referees to matches

For a League the page shows a participant type dropdown, the divisions (categories) as tabs, the stages of the selected division (**S1**, **S2**, …) and a match table.

1. Pick the division tab and the stage.
2. Each match has a **Referee 1** column (and **Referee 2** when Per Match Referee is 2). Open the dropdown in the empty referee cell and pick a referee. The assignment is saved at once.
3. The referee's name and e-mail replace the dropdown.

The dropdown lists the event's accepted referees. Other columns: **Match**, **Date**, **Venue**, **Cost 1** / **Cost 2**, **Bank Details**, **Action**. The table shows 10 matches per page. For a League, **Search by Name** searches this match table.

Messages when assigning:
- "This referee is already assigned to this match" – pick someone else.
- "Some matches don't have slots assigned" – the match has no time slot yet. Schedule it first.
- "Event official has overlapping assignments" – the referee already has a match at the same time.
- "Assignment would exceed per_match_limit for one or more matches" – the match already has the number of referees set in **Per Match Referee**.
- "No assignable event official found for user on this match" – the person has no active referee registration for this event.

## League: removing referees from a match

- **Per Match Referee = 2**: each assigned referee has a red **x** next to the name ("Remove Referee"). Click it and confirm "Are you sure you want to unassign <name>?" with **Yes, Unassign**. Only that referee is removed.
- **Bin icon in the Action column**: asks "Are you sure you want to unassign this referee?". It removes **every official assigned to the match**, including umpires assigned on the Umpire Settings step.
- With **Per Match Referee = 1** there is no **x**; use the bin icon.
- Rows without a referee show `--` in **Bank Details** and **Action**.
- Removing an assignment needs Edit permission on **Schedule Umpire Access**; without it the action fails with "Access Denied".

## League: adding a referee for chosen matches

1. Click **Add**. The side panel **Add Referee Manually** opens.
2. **Search Referee** – pick the user.
3. **Cost per match** – the amount for each chosen match.
4. **Matches** – open **Select Matches** and tick matches. The list shows the matches of the stage and page currently on screen, as "Team A VS Team B" ("TBD VS TBD" when the teams are not known yet). Use the search box; "No matches found for "<text>"" means nothing matches.
5. Click **Add**. "Referee Added Successfully." confirms it.

The referee is registered for those matches and assigned to them. Choosing a match the referee is already registered for gives "Official Already Registered".

## Filtering the referee list

Click **Filter**. A side panel opens:
- **Referees** – tick one or more referees (**Select Referee**).
- **Matches** (League only) – **Assigned Matches** or **Unassigned Matches**.

Click **Apply**. For a Tournament the list shows only the chosen referees. For a League the match table shows the matches of those referees, and only assigned or unassigned matches if chosen.

For a League an **×** appears on the **Filter** button while a filter is active. Click the **×** to clear the filter.

## Viewing a referee's bank details

- Click the **i** icon in the **Bank Details** column. A side panel **Bank Details** shows **Account Name Holder**, **Postal address of Bank**, **IBAN number** and **Swift-BIC number**, as the referee entered them. The fields are read-only. Click **Close**.
- League, match with two referees: choose the referee in **Select Referee** at the top of the panel ("Referee 1 - <name>", "Referee 2 - <name>").
- Empty fields mean the referee has not entered bank details.
- "No Referee for this match." means no referee is assigned.

## Creating a new referee account

Use this when the person has no account yet.

1. In **Add Referee Manually**, click **Add New Referee Account**. The side panel **Add New Member** opens.
2. **Select Role** – choose the role (only the eligible referee roles are offered). The fields for that role load. "No Associated Field for the role" means the role has no fields set up.
3. Fill in the fields. Fields marked `*` are mandatory. If a linked (parent) user is asked for, choose one. File fields accept "Upload from Device / Drag n Drop".
4. Click **Submit**.

Messages: "Please fill all required fields", "Please select at least one parent", "Only Alphabets and Spaces Allowed" / "Incorrect Format.", "File Exceed max limit of 5mb." (file too large). After a successful save the server's message is shown and the new user can be picked in **Search Referee**.

## Referee Settings page: other messages

- "Access Denied" – your role lacks Edit permission on **Referee Registration Settings** (saving settings, adding referees).
- "Wait For Verification" – your own admin account is not verified yet.
- "No Registration Settings Enabled" – referee registration was never saved for this event. Open **Settings**, toggle on **Registration** and **Save** first.
- "Registration Not Allowed" – the **Registration** toggle is off for this event.
- "Official Already Registered" – the referee is already registered for that day or match.
- "Failed to assign referee" – no referee was chosen, or the server refused without a message.
- "Unauthorized Access" – your session expired. Sign in again.
- "Some Error Occured" – the list could not be loaded. Reload the page.

## Frequently asked questions about the Referee Settings page

**How do I open referee registration?** Click **Settings**, turn on **Registration**, fill in Eligible Role, Registration Date, Amount Type and Per Match Referee, then click **Save**.

**Why can't I pick a registration date?** Only dates before the event start date can be chosen.

**How do I close referee registration?** Saving with the toggle off is not possible. Set the **Registration End Date** to an earlier date and save.

**How do I add a referee manually?** Click **Add**, pick the user in **Search Referee**, set the cost, choose **Days** (Tournament) or **Matches** (League), and click **Add**.

**Why does my referee not appear in the list?** The list only shows accepted referees. With verifiers set, the registration waits for approval on the Event Referee Request page.

**Why do I get "Registration Closed" when adding or deleting a referee?** The registration end date has passed. Move it in **Settings**, or ask the main administrator.

**Why do I get "Registration Not Allowed For Role"?** The user's role is not in **Eligible Role**.

**Why are the Settings, Add and Filter buttons greyed out?** Your role needs Edit permission on **Referee Registration Settings**.

**How do I assign a referee to a match?** League events only: pick the referee in the match's Referee column.

**Why can't I add a second referee to a match?** **Per Match Referee** is 1. Change it to 2 in **Settings**.

**What does the bin icon on a League match remove?** All officials of that match, referees and umpires.

**Are umpires and referees set up in the same place?** No. Umpires are on the **Umpire Settings** step, referees on this step. Each has its own registration settings.
