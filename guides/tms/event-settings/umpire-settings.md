---
doc_id: tms.event-settings.umpire-settings
title: Umpire Settings page
routes:
  - tms/event-settings/umpire-settings/:event_id
aliases:
  - umpire settings
  - umpire registration settings
  - umpire step
  - add umpire
  - assign umpire
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I open umpire registration for this event?
  - How do I add an umpire manually?
  - How do I assign an umpire to a match?
  - Why does my umpire not appear in the list?
  - Why do I get "Registration Closed" when I add an umpire?
backend_sources:
  - gateway/src/routers/events_router.py (update_event_umpire_registration_settings)
  - gateway/src/routers/registration_router.py (register_event_umpire, get_event_officials, update_event_officials, is_event_official_registration_validations, event_official_verification_logic)
  - gateway/src/routers/planner_router.py (assign_event_official_match_ids, remove_event_official_match)
  - tms/src/service/event_official_service.py (assign_event_official_match_ids, remove_event_official_match, register_event_officials, update_event_officials)
  - tms/src/crud/event_official_crud.py (register_event_officials, resolve_assignable_official_id_by_user_role, remove_event_official_match_mappings)
source_files:
  - src/app/modules/tms/umpire-settings/umpire-settings.component.ts
  - src/app/modules/tms/umpire-settings/umpire-settings.component.html
  - src/app/modules/tms/events-settings/events-settings.component.ts
  - src/app/core/services/registration-service/registration-service.service.ts
  - src/app/core/services/tournament-config/tournament-config.service.ts
  - src/app/core/utils/permission_directive/permissions.directive.ts
---
# Umpire Settings page – user guide

This guide describes the **Umpire Settings** step of an event in the Stupa Event Management System (admin panel). On this page the organiser sets up online registration for umpires, adds umpires by hand, and (for a League) assigns umpires to matches.

## Where to find it

Open **Event** from the sidebar, then click **Umpire Settings** in the row of setup steps at the top of the page.

## Umpire Settings page: where it is and what it is for

- Page address: `/tms/event-settings/umpire-settings/<event id>`, for example `/tms/event-settings/umpire-settings/3453`.
- It is the **Umpire Settings** step in the row of event setup steps. The step is only shown for organisations that use it.
- Page heading: **Umpire Registration Settings**, with the text "The tournament organizer can control the registration settings and choose to manually close registrations in any category, regardless of the registration deadline."
- On this page you can:
  - toggle on online registration for umpires and set its rules (**Settings**),
  - add an umpire yourself (**Add**),
  - remove an umpire and bring a removed umpire back (**Deleted**),
  - see each umpire's bank details,
  - for a League: assign umpires to matches.
- The page looks different for the two event types:
  - **Tournament**: a list of umpires per event day.
  - **League**: a list of matches with an Umpire column for each match.

## Umpire Settings page: buttons at the top

Next to the **Search by Name** box there are four buttons (Tournament) or three buttons (League):

- **Filter** – show only some umpires (see "Filtering the umpire list").
- **Settings** – opens the **Umpire Settings** side panel with the registration rules.
- **Add** – opens the **Add Umpire Manually** side panel.
- **Deleted** (Tournament only) – shows umpires that were removed.

These buttons are greyed out when your role does not have **Edit** permission on **Umpire Registration Settings**. Ask an administrator to give it on the event's **Access-Control** step or in role management.

## Umpire Settings side panel: switching on umpire registration

Click **Settings**. The side panel **Umpire Settings** opens ("You can manage the umpires for your event and enable online registration for them.").

1. Turn on the **Registration** toggle ("You can enable registration, and the umpires will be able to submit their registration online through the platform."). All sections below stay greyed out while the toggle is off.
2. Fill in the sections (each is explained in the next sections): **Eligible Role**, **Registration Date**, **Amount Type**, **Per Match Umpire**, and optionally **Umpire Verification**.
3. Click **Save**. The message "Settings updated successfully" confirms it.

Rules:
- Fields marked `*` are mandatory. If one is empty, the message is "Please fill all required details", and the field shows "*Required".
- **Save** is greyed out while the **Registration** toggle is off. Turning the toggle off therefore cannot be saved from this panel.
- Saved settings are loaded again the next time you open the panel.

## Umpire Settings side panel: Eligible Role

- **\*Eligible Role** – "Select the user role you want to allow to apply as an umpire for this event".
- Open **Select Role** and tick one or more roles. The roles offered are the roles your organisation allows to register as umpires.
- Only users with one of these roles can register as umpire for this event. The same rule applies when an organiser adds an umpire manually: a user with another role is refused with "Registration Not Allowed For Role" (the main administrator account is not checked).

## Umpire Settings side panel: Registration Date

- **\*Registration Date** – "Select the start date and end date to specify when you want to enable umpire registration, including the date to start and the date to close registrations."
- **Registration Start Date** and **Registration End Date** are picked in a calendar (format DD/MM/YYYY). Both are mandatory.
- Only dates **before the event's start date** can be picked. The event start date and every later date are greyed out.
- Outside these dates umpires cannot register, and organisers (except the main administrator) cannot add, remove or restore umpires on this page either:
  - before the start date: "Registration Not Started",
  - after the end date: "Registration Closed".
- To add or change umpires after the end date, move the **Registration End Date** in **Settings**, or ask the main administrator.

## Umpire Settings side panel: Amount Type and Per Match Umpire

**\*Amount Type** – **Free** or **Paid**. Tooltip: "You can select 'Paid', which means the umpire can enter the amount they wish to request per match. In the 'Free' scenario, the umpire cannot enter the amount they wish to receive per match."
- With **Paid**, the panel lists the bank details involved: Account Name Holder, Postal address of Bank, IBAN number, Swift-BIC number.
- With **Paid**, the umpire list shows a **Cost** column, and the cost field in **Add Umpire Manually** can be filled in. With **Free** the cost field is disabled and the cost is 0.

**\*Per Match Umpire** – **1** or **2** ("You can select the number of umpires required per match."). The default is 1.
- It sets how many umpires one match can have. Assigning more is refused with "Assignment would exceed per_match_limit for one or more matches".
- For a League, **2** adds an **Umpire 2** and a **Cost 2** column to the match table.

## Umpire Settings side panel: Umpire Verification (optional)

**Umpire Verification** – "Select the user role who will verify the details for the umpires, or you can select any specific user as well."

- **Verifier 1** and **Verifier 2** each have two dropdowns: first a role, then (optionally) a specific user with that role.
- If a role is chosen without a user, the verifier is taken from the umpire's own linked (parent) user of that role, when there is one.
- With verifiers set, a new umpire registration is **pending** until it is approved. With both verifiers set, both must accept. Verifiers approve requests on the **Event Umpire Request** page (`/admin/manage/umpire`).
- Without verifiers, registrations are accepted straight away.
- Registrations made by the main administrator account are always accepted.
- **The umpire list on this page only shows accepted umpires.** A pending umpire appears after approval.

## Tournament: the umpire list and day tabs

For a Tournament the page shows a row of day tabs and a table.

- Day tabs: **ALL / DAYS** first, then one tab per event day ("Day 1", "Day 2", … with the date). Use the arrows to scroll. Click a tab to see the umpires registered for that day; **ALL** shows every day.
- Table columns: **S.No**, **Name** (with the e-mail below), **Cost** (only when Amount Type is Paid), **Date**, **DAYS**, **Verification Status**, **Bank Details**, **Action**.
- An umpire registered for several days has one row per day.
- Click a column heading to sort. The table shows 10 rows per page; use the page buttons below it.
- **Search by Name** filters the list by umpire name.
- "No record found" means no accepted umpire matches the tab, search or filter.

## Tournament: adding an umpire manually

1. Click **Add**. The side panel **Add Umpire Manually** opens ("Search for the umpire you want to add to your event.").
2. **Search Umpire** – open **Search to add registered umpire** and pick a user. Type in the search box to narrow the list; more users load as you scroll ("Loading more umpires...").
3. **Cost per Day** – the amount per day ("Enter the amount you would like to allocate to the umpire."). Disabled when Amount Type is Free.
4. **Days** – open **Select Day** and tick the days the umpire is available ("Select the days you want the umpire to be available for your event.").
5. Click **Add**. "Umpire added successfully." confirms it and the list reloads.

Notes:
- The list offers users of the roles your organisation allows as umpires. A user whose role is not in the event's **Eligible Role** is refused with "Registration Not Allowed For Role".
- Pick at least one day. One row per day is created.
- The person is not in the list yet? Click **Add New Umpire Account** to create the account first (see "Creating a new umpire account").
- With verifiers set, the added umpire stays pending and does not appear in the list until approved (see "Umpire Verification").

## Tournament: removing and restoring an umpire

- **Remove**: click the bin icon in the **Action** column. The question "Are you sure you want to Delete registration of <name>?" appears. Confirm to remove. "Umpire deleted successfully." confirms it.
- Removing an umpire also removes that umpire from the matches they were assigned to on that date.
- **Restore**: click **Deleted** to see removed umpires (heading **Deleted Umpire**). Click the **+** icon on a row and confirm "Are you sure you want to Add registration of <name>?". "Umpire added successfully." confirms it.
- Click the arrow left of **Deleted Umpire** to return to the normal list.
- Removing and restoring follow the registration rules: outside the registration dates, or with Registration switched off, they fail with "Registration Closed", "Registration Not Started" or "Registration Not Allowed" (except for the main administrator).

## League: assigning umpires to matches

For a League the page shows a participant type dropdown, the divisions (categories) as tabs, the stages of the selected division (**S1**, **S2**, …) and a match table.

1. Pick the division tab and the stage.
2. In the table, each match has an **Umpire 1** column (and **Umpire 2** when Per Match Umpire is 2). Open the dropdown in the empty umpire cell and pick an umpire. The assignment is saved at once.
3. The umpire's name replaces the dropdown.

The dropdown lists the event's accepted umpires. Other columns: **Match** (team vs team), **Date**, **Venue**, **Cost 1** / **Cost 2**, **Bank Details**, **Action**. The table shows 10 matches per page. For a League, **Search by Name** searches this match table.

Messages when assigning:
- "This umpire is already assigned to this match" – pick someone else.
- "Some matches don't have slots assigned" – the match has no time slot yet. Schedule it first (Day Planner / scheduler).
- "Event official has overlapping assignments" – the umpire already has a match at the same time.
- "Assignment would exceed per_match_limit for one or more matches" – the match already has the number of umpires set in **Per Match Umpire**.
- "No assignable event official found for user on this match" – the person has no active umpire registration for this event.

## League: removing umpires from a match

- **Per Match Umpire = 2**: each assigned umpire has a red **x** next to the name ("Remove Umpire"). Click it and confirm "Are you sure you want to unassign <name>?" with **Yes, Unassign**. Only that umpire is removed.
- **Bin icon in the Action column**: asks "Are you sure you want to unassign this umpire?". It removes **every official assigned to the match**, including referees assigned on the Referee Settings step.
- With **Per Match Umpire = 1** there is no **x**; use the bin icon.
- Rows without an umpire show `--` in **Bank Details** and **Action**.
- Removing an assignment needs Edit permission on **Schedule Umpire Access**; without it the action fails with "Access Denied".

## League: adding an umpire for chosen matches

1. Click **Add**. The side panel **Add Umpire Manually** opens.
2. **Search Umpire** – pick the user.
3. **Cost per Day** – the amount for each chosen match. Disabled when Amount Type is Free.
4. **Matches** – open **Select Matches** and tick matches. The list shows the matches of the stage and page currently on screen, as "Team A VS Team B" ("TBD VS TBD" when the teams are not known yet). Use the search box to find a match.
5. Click **Add**. "Umpire added successfully." confirms it.

The umpire is registered for those matches and assigned to them. Choosing a match the umpire is already registered for gives "Official Already Registered".

## Filtering the umpire list

Click **Filter**. A side panel opens:
- **Umpires** – tick one or more umpires (**Select Umpire**).
- **Matches** (League only) – **Assigned Matches** or **Unassigned Matches**.

Click **Apply**. For a Tournament the list shows only the chosen umpires. For a League the match table shows the matches of those umpires, and only assigned or unassigned matches if chosen.

For a League an **×** appears on the **Filter** button while a filter is active. Click the **×** to clear the filter.

## Viewing an umpire's bank details

- Click the **i** icon in the **Bank Details** column. A side panel **Bank Details** shows **Account Name Holder**, **Postal address of Bank**, **IBAN number** and **Swift-BIC number**, as the umpire entered them. The fields are read-only. Click **Close**.
- League, match with two umpires: choose the umpire in **Select Umpire** at the top of the panel ("Umpire 1 - <name>", "Umpire 2 - <name>").
- Empty fields mean the umpire has not entered bank details.
- "No Umpire for this match." means no umpire is assigned.

## Creating a new umpire account

Use this when the person has no account yet.

1. In **Add Umpire Manually**, click **Add New Umpire Account**. The side panel **Add New Member** opens.
2. **Select Role** – choose the role (only the eligible umpire roles are offered). The fields for that role load. "No Associated Field for the role" means the role has no fields set up.
3. Fill in the fields. Fields marked `*` are mandatory. If a linked (parent) user is asked for, choose one.
4. Click **Submit**.

Messages: "Please fill all required fields" (a mandatory field is empty), "Please select at least one parent" (no parent chosen), "Only Alphabets and Spaces Allowed" / "Incorrect Format." (a field has the wrong format). After a successful save the server's message is shown and the new user can be picked in **Search Umpire**.

## Umpire Settings page: other messages

- "Access Denied" – your role lacks Edit permission on **Umpire Registration Settings** (saving settings, adding umpires).
- "Wait For Verification" – your own admin account is not verified yet.
- "No Registration Settings Enabled" – umpire registration was never saved for this event. Open **Settings**, toggle on **Registration** and **Save** first.
- "Registration Not Allowed" – the **Registration** toggle is off for this event.
- "Official Already Registered" – the umpire is already registered for that day or match.
- "Unauthorized Access" – your session expired. Sign in again.
- "Some Error Occured" – the list could not be loaded. Reload the page.

## Frequently asked questions about the Umpire Settings page

**How do I open umpire registration?** Click **Settings**, turn on **Registration**, fill in Eligible Role, Registration Date, Amount Type and Per Match Umpire, then click **Save**.

**Why can't I pick a registration date?** Only dates before the event start date can be chosen.

**How do I close umpire registration?** Saving with the toggle off is not possible. Set the **Registration End Date** to an earlier date and save.

**How do I add an umpire manually?** Click **Add**, pick the user in **Search Umpire**, set **Cost per Day**, choose **Days** (Tournament) or **Matches** (League), and click **Add**.

**Why does my umpire not appear in the list?** The list only shows accepted umpires. With verifiers set, the registration waits for approval on the Event Umpire Request page.

**Why do I get "Registration Closed" when adding or deleting an umpire?** The registration end date has passed. Move it in **Settings**, or ask the main administrator.

**Why do I get "Registration Not Allowed For Role"?** The user's role is not in **Eligible Role**.

**Why are the Settings, Add and Filter buttons greyed out?** Your role needs Edit permission on **Umpire Registration Settings**.

**How do I assign an umpire to a match?** League events only: pick the umpire in the match's Umpire column.

**Why do I get "Some matches don't have slots assigned"?** The match has no time slot yet. Schedule it first.

**Why can't I add a second umpire to a match?** **Per Match Umpire** is 1. Change it to 2 in **Settings**.

**What does the bin icon on a League match remove?** All officials of that match, umpires and referees.

**Why is the Cost per Day field disabled?** **Amount Type** is Free.

**Where do I see an umpire's bank details?** Click the **i** icon in the **Bank Details** column.
