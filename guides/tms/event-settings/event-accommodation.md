---
doc_id: tms.event-settings.event-accommodation
title: Accommodation page
routes:
  - tms/event-settings/event-accomodation/:event_id
aliases:
  - accommodation
  - accomodation
  - hotel
  - hotels
  - room booking
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I enable accommodation for this event?
  - How do I add a hotel and its rooms?
  - Who can request accommodation?
  - How do I withdraw a booking?
  - Why is the accommodation toggle greyed out?
backend_sources:
  - gateway/src/routers/events_router.py (update_event_accomodation_settings)
source_files:
  - src/app/modules/tms/event-accomodation/event-accomodation.component.ts
  - src/app/modules/tms/event-accomodation/event-accomodation.component.html
  - src/app/shared/accommodation-filter-sidebar/accommodation-filter-sidebar.component.html
  - src/app/shared/accommodation-edit-sidebar/accommodation-edit-sidebar.component.html
  - src/app/shared/travel-acco-add-member-sidebar/travel-acco-add-member-sidebar.component.html
  - src/app/shared/travel-acco-add-player-sidebar/travel-acco-add-player-sidebar.component.html
---
# Accommodation page – user guide

This guide describes the **Accommodation** step of an event in the Stupa Event Management System (admin panel). Here the organiser togglees accommodation on for the event, decides who may request it, creates hotels and rooms, and manages the bookings.

## Where to find it

Open **Event** from the sidebar, then click **Accommodation** in the row of setup steps at the top of the page.

## Accommodation page: where it is and what it is for

- Page address: `/tms/event-settings/event-accomodation/<event id>`, for example `/tms/event-settings/event-accomodation/1358`. The address is spelled "accomodation".
- It is the **Accommodation** step in the row of event setup steps. The step is only shown for organisations that use it.
- Top card: **Enable Accommodation** – "To configure & enable accommodation for the event", with a toggle and a **Settings** button.
- Once enabled, the page shows the **Bookings** dashboard ("Booking dashboard which provides details of event accommodation status"), the booking list, and **Manage Listings** for hotels and rooms.

## Enable Accommodation toggle

- Turn the toggle on to open accommodation for the event; turn it off to close it. The change is saved at once.
- **The toggle is greyed out** when accommodation is not enabled for your organisation in the global travel and accommodation settings. Ask your administrator to enable it there first.
- **Settings** is greyed out while the toggle is off.
- If saving fails, the server's message is shown and the toggle goes back to off.

## Accommodation Settings side panel: who can request and verification

Click **Settings** to open **Accommodation Settings**, then click **Update** to save.

- **Roles allowed for accommodation** – "Provide access to roles who can send a request for accommodation". Tick the roles.
- **Enable verification for accommodation** – requests must be approved before they count. "The system can support up to two levels of verification."
  - **Verification Type \***: **One-way verification** (one verifier) or **Two-way Verification** (two verifiers).
  - **Select Verifiers \***: for **Verification 1** (and **Verification 2** for two-way) choose a **Role** and then a **User** with that role.
  - Missing verifier fields give "Please fill all required fields" and nothing is saved.
- **Enable Self Registration** – "Enables users' personalized requests, regardless of pre-defined role permissions". Tick the roles that may register themselves.
- **Show Parents Info** – "The selected parent will be reflected in both listings and exports." Tick the parent roles (for example club or association) to show as extra columns. "No parent roles are configured for the Player role." means there is nothing to choose. If no parent role is ticked, the setting is saved as off.

## Registration Date for accommodation requests

- In the **Bookings** card, **Registration Date** shows the period in which accommodation can be requested (for example "01 Jun 26 - 15 Jun 26").
- Click it to pick a new start and end date in the calendar. The new dates are saved immediately.

## Bookings dashboard: the numbers

- **Number of Reservations**
- **Total rooms booked** – booked / available.
- **Total room-wise occupancy rate**
- **Total nights booked**
- **Revenue booked** (in euro).

## Booking list: Registered and Unregistered

- **Registered** – people with an accommodation booking. Columns: **Date Booked**, **Name**, parent columns (if Show Parents Info is on), **Role**, **Booking By**, **Check In**, **Check Out**, **Dietary Preferences**, **Options** (hotel name, rating, room), **Room Occupancy**, **Booking Status**, **Action**. "NA" means the value is missing.
- **Unregistered** – event participants listed from the event registration, for finding people who still need a booking.
- Search with the box (**Search Booking By** on Registered, **Search by Name** on Unregistered). Click a column heading to sort. "No Booking Found" means nothing matches.
- **Filter Preferences** – filter by **Role**, **Options**, **Room**, **Date**, **Booked By** and **Booking Status**, then **Apply**. **Clear** removes the filters; the number on the button shows how many are active.

## Booking actions: edit, history, withdraw, restore

In the **Action** column:
- **History** icon – shows the version history of the booking.
- **Edit** icon – opens **Accommodation Edit** with **Check In**, **Check Out**, **Dietary Preferences**, **Options** and **Room Type**.
- **Withdraw** icon – withdraws one booking at once: "Booking withdrawn successfully".
- To withdraw several: tick the bookings (or the select-all box) and click **Withdraw (n)**: "Bookings withdrawn successfully". With nothing ticked: "Please select bookings to withdraw".
- **Withdrawn** shows the **Withdrawn Requests** list. Use the restore icon to bring a booking back: "Booking restored successfully".
- Failures: "Failed to withdraw booking(s)" / "Failed to restore booking". Try again.

## Adding people and exporting

- **Add Member** → **Add Member**: choose a **User Role**, pick people from the list (**Name**, **Nationality**) and click **Add**. "Players added successfully!" confirms it; nobody selected gives "Please select at least one participant"; "Failed to add members" means the server refused.
- **Add Member** → **Add Temporary Member**: add a person who has no account (with **Gender** and an optional **Description**).
- **Export** → **Accommodation** (bookings) or **Accommodation + Travel** (bookings with travel details). "Error exporting bookings data" means the export failed.

## Manage Listings: adding a hotel

Click **Manage Listings** to open the **Hotels List** (search by hotel name, edit, add). Click **Add new hotels**.

**Hotel Details** tab:
- **Hotel Name \*** (40 characters), **Hotel Status \*** (toggle, **Active**), **Hotel Rating \*** (stars).
- **Description** (up to 200 characters: "Description cannot exceed 200 characters.").
- **Address \*** (**Street Address 1**, **Street Address 2**), **State/City \***, **Country**, **Zip Code \***.
- **Phone number \*** (country code and number), **Email Address**, **Website**, **Google Maps Link**.
- Click **Next**. "Hotel created successfully" (new) or "Hotel Updated Successfully" (edit). Missing required fields: "Please fill all required details".
- **Delete** removes the hotel.

## Manage Listings: rooms of a hotel

**Room Details** tab – "Configure the room details associated with the hotel":
- **Add Room** adds a room type. For each:
  - **Room Title \*** (40 characters: "Room title is required", "Room title must be at most 40 characters").
  - **Room Capacity \*** – guests per room, 1 to 10 ("Room capacity must be at least 1" / "Room capacity must be at most 10").
  - **Room Rates \*** – price per room; only shown when invoicing is enabled for the organisation ("Room rates are required").
  - **Room Inventory** – how many rooms of this type are available.
- **Save** on a room saves it; **Delete** removes it. Click **Save** at the bottom to save the rooms: "Rooms added successfully" / "Room updated successfully".
- In the Hotels List each room type shows its title, guests, price and "available/total Available".

## Accommodation page: permissions

- Saving the accommodation settings needs **Edit** permission on **Edit Accomodation Settings**. Without it the save fails with "Access Denied".
- An expired sign-in gives "Unauthorized Access". Sign in again.

## Frequently asked questions about the Accommodation page

**How do I enable accommodation for this event?** Turn on the **Enable Accommodation** toggle, then click **Settings** to choose roles and verification.

**Why is the accommodation toggle greyed out?** Accommodation is not enabled for your organisation in the global travel and accommodation settings.

**Who can request accommodation?** The roles ticked under **Roles allowed for accommodation**, plus self-registration roles if **Enable Self Registration** is on.

**How do I require approval of accommodation requests?** Turn on **Enable verification for accommodation**, choose one-way or two-way, and select the verifier role and user.

**How do I change the accommodation request period?** Click the **Registration Date** in the Bookings card and pick new dates.

**How do I add a hotel and its rooms?** **Manage Listings** → **Add new hotels**, fill **Hotel Details**, **Next**, add rooms on **Room Details**, **Save**.

**What is the maximum room capacity?** 10 guests per room.

**Why is there no Room Rates field?** Invoicing is not enabled for your organisation.

**How do I withdraw a booking?** Click the withdraw icon on the row, or tick several bookings and click **Withdraw**.

**How do I bring back a withdrawn booking?** Click **Withdrawn**, then the restore icon on the booking.

**How do I export the bookings?** **Export** → **Accommodation** or **Accommodation + Travel**.
