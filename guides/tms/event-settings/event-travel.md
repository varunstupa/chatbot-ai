---
doc_id: tms.event-settings.event-travel
title: Travel page
routes:
  - tms/event-settings/event-travel/:event_id
aliases:
  - travel
  - travel bookings
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I enable travel for this event?
  - Who can request travel?
  - How do I change the arrival details of several bookings at once?
  - How do I withdraw a travel booking?
  - Why is the travel toggle greyed out?
backend_sources:
  - gateway/src/routers/events_router.py (update_event_travel_settings, Edit Travel Settings)
  - gateway/src/routers/travel_bookings_router.py
source_files:
  - src/app/modules/tms/event-travel/event-travel.component.ts
  - src/app/modules/tms/event-travel/event-travel.component.html
  - src/app/modules/tms/event-travel/withdrawal-dialog/withdrawal-dialog.component.html
  - src/app/modules/tms/event-travel/edit-travel-bookings/edit-travel-bookings.component.html
  - src/app/shared/travel-acco-add-member-sidebar/travel-acco-add-member-sidebar.component.html
---
# Travel page – user guide

This guide describes the **Travel** step of an event in the Stupa Event Management System (admin panel). Here the organiser togglees travel on for the event, decides who may request travel, and manages arrival and departure bookings.

## Where to find it

Open **Event** from the sidebar, then click **Travel** in the row of setup steps at the top of the page.

## Travel page: where it is and what it is for

- Page address: `/tms/event-settings/event-travel/<event id>`, for example `/tms/event-settings/event-travel/534`.
- It is the **Travel** step in the row of event setup steps. The step is only shown for organisations that use it.
- Top card: **Enable Travel.** – "To configure and enable travel details for the event", with a toggle and a **Settings** button.
- Once enabled, the page shows the **Bookings** dashboard ("Booking Dashboard which provides details of event Travel status") and the booking list.
- The transport modes offered (for example flight, train, bus) are set up by the organisation in its global travel settings.

## Enable Travel toggle

- Turn the toggle on to open travel for the event; turn it off to close it. The change is saved at once ("Event settings updated successfully").
- **The toggle is greyed out** when travel is not enabled for your organisation in the global travel settings. Ask your administrator to enable it there first.

## Travel Settings side panel: roles, verification and self-registration

Click **Settings** to open **Travel Settings**, then click **Update** to save.

- **Roles allowed for travel** – "Provide access to roles who can send a request for travel". Tick the roles.
- **Enable verification for travel** – requests must be approved; "The system can support up to two levels of verification".
  - **Verification Type \***: **One-way Verification (Admin)** or **Two-way Verification**.
  - **Select Verifiers \***: for **Verification 1** (and **Verification 2** for two-way) choose a role and then a user.
  - Errors: "Verification type is required", "Select a role for verification 1", "Select a role for verification 2".
- **Enable self-registration for travel** – "Enable participants to submit their own travel requests." Tick the roles under **Role Allowed for Self Registration**.
- **Show Parents Info** – "The selected parent will be reflected in both listings and exports." Tick the parent roles to show as extra columns. "No parent roles are configured for the Player role." means there is nothing to choose.

## Registration Date and the Bookings dashboard

- **Registration Date** in the Bookings card shows the period in which travel can be requested (for example "01 Jun 26 - 15 Jun 26"). Click it and pick new start and end dates; they are saved immediately.
- The dashboard shows one card per transport mode with the number of **Arrival** and **Departure** bookings.

## Booking list: Registered and Unregistered

- **Registered** – people with a travel booking. Columns: **Date Booked**, **Name**, parent columns (if Show Parents Info is on), **Booking By**, **Arrival Mode**, **Arrival** (date and time), **Arrival Info**, **Departure Mode**, **Departure**, **Departure Info**, **Booking Status** (only when verification is on), **Action**. "NA" means the value is missing.
- **Unregistered** – event participants listed from the event registration, for finding people who still need a booking.
- Search with the box. Click a column heading to sort.
- Filters (Registered tab): **Booking By** (pick names), **Vehicle** (arrival and departure mode), **Booking Status** (ACCEPTED, PENDING, Rejected – only with verification), **Date** (arrival and departure date). Each active filter shows as a chip; click its × to remove it.

## Editing travel bookings

- **One booking**: click the edit icon in the **Action** column.
- **Several bookings**: tick them (or the select-all box) and click **Edit**.
- The **Edit** panel shows per person the **Booking ID** and **Booking By**, and lets you change **Arrival** (**Mode**, **Arrival Info**, **Date**, **Time**) and **Departure** (**Mode**, **Departure Info**, **Date**, **Time**).
- **Apply to all** copies the values to the other selected people (use **Select all** and **Apply**). Click **Update** to save.

## Withdrawing and restoring travel bookings

- **One booking**: click the withdraw icon in the **Action** column. It is withdrawn at once: "Booking withdrawn successfully".
- **Several bookings**: tick them and click **Withdraw**. Confirm "Are you sure you want to withdraw? All the data related to these entries will be deleted." with **Yes, confirm**.
- **Withdrawn** shows the **Withdrawn Requests** list; use the restore icon to bring a booking back.
- The **History** icon shows the version history of a booking.
- "Failed to withdraw booking" means the server refused; try again.

## Adding people and exporting

- **Add Member** → **Add Member**: choose a **User Role**, pick people and click **Add**. "Players added successfully!" confirms it; nobody selected gives "Please select at least one participant"; "Failed to add members" means the server refused.
- **Add Member** → **Add Temporary Member**: add a person who has no account.
- **Export** → **Travel** or **Travel + Accommodation**. "Failed to export travel users" means the export failed.

## Travel page: permissions

- Saving travel settings needs **Edit** permission on **Edit Travel Settings**. Without it the save fails with "Access Denied".
- An expired sign-in gives "Unauthorized Access". Sign in again.

## Frequently asked questions about the Travel page

**How do I enable travel for this event?** Turn on the **Enable Travel.** toggle, then click **Settings** to choose roles and verification.

**Why is the travel toggle greyed out?** Travel is not enabled for your organisation in the global travel settings.

**Who can request travel?** The roles ticked under **Roles allowed for travel**, plus self-registration roles if self-registration is on.

**How do I require approval of travel requests?** Turn on **Enable verification for travel**, choose the verification type and select the verifier roles and users.

**Why can I not filter by Booking Status?** The filter and column only exist when travel verification is on.

**How do I change the arrival details of several bookings at once?** Tick the bookings, click **Edit**, fill the arrival fields, use **Apply to all**, then **Update**.

**How do I withdraw several bookings?** Tick them, click **Withdraw** and confirm with **Yes, confirm**.

**How do I bring back a withdrawn booking?** Click **Withdrawn**, then the restore icon.

**Why is a transport mode missing?** Only the modes enabled in the organisation's global travel settings are offered.

**How do I export the travel list?** **Export** → **Travel** or **Travel + Accommodation**.
