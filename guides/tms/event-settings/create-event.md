---
aliases:
- event details
- details step
- create event
- edit event
- tournament setup
- event setup
- event not live
- event not publishing
- tournament poster upload
- add category
audience:
- tournament organisers
- event administrators
- non-technical users
backend_sources:
- gateway/src/routers/events_router.py
- gateway/src/main.py (file_upload)
- tms/src/service/events_service.py
- tms/src/service/event_status_calculator.py
- tms/src/service/points_state_guard.py
- tms/src/utils/event_date_sync.py
doc_id: tms.event-settings.create-event
document_type: product_help
routes:
- "tms/event-settings/create-event/:event_id"
source_files:
- src/app/modules/tms/create-tournament/create-tournament.component.ts
- src/app/modules/tms/create-tournament/create-tournament.component.html
- src/app/shared/ai-banner-generator-dialog/ai-banner-generator-dialog.component.html
- src/app/shared/ai-banner-generator-dialog/ai-banner-generator-dialog.component.ts
- src/app/modules/admin/venue-management/event-venue/event-venue-section.component.html
- src/app/shared/components/category-view/category-view.component.html
suggested_questions:
- How do I create a tournament?
- How do I add categories to this event?
- Why do I get "Event Already Exists"?
- Why is the status stuck on INCOMPLETE?
- Why can't I publish my event?
- Why is my event not visible to players?
- What size should the banner and thumbnail be?
- Why can't I edit or delete my event?
- Why did changing the event dates remove schedules?
- Why is my image upload failing?
supported_languages:
- English
- Hindi
- Hinglish
tenants: all
title: Event Details page --- Organiser Guide and Troubleshooting
answer_notes: |
  How the assistant should answer questions about this page:
  -   Understand the user's intent rather than requiring the exact wording
      used in the interface.
  -   Use the actual UI label when giving instructions, then explain it in
      plain language.
  -   Start with the most likely documented cause and give clear steps.
  -   If different causes require different solutions, ask one short
      follow-up question.
  -   Do not claim to have checked the user's actual event, status,
      permissions, or configuration unless live application data is
      available.
  -   Do not invent buttons, settings, permissions, or behaviour.
  -   If the answer depends on organisation-specific configuration,
      explain that the configuration may vary and recommend contacting the
      organisation's administrator or support when appropriate.
  -   Keep event creation, verification, and publishing distinct. They are
      separate actions.

  Intent: create an event: Explain where to open Details, list the mandatory fields, mention the required banner, thumbnail and logo, and tell the user to click Create. Then explain that categories and other required setup sections must be completed separately.

  Intent: event not visible or not live: Do not assume the event has one specific problem. Explain that saving, verification and publishing are separate. Check whether the event is saved, whether the Event Level requires verification, whether verification is accepted, and whether the user is in Edit mode and looking at the bottom action bar. If the user means player registration is unavailable rather than event visibility, ask about registration separately.

  Intent: event stuck on INCOMPLETE: In Auto mode, first check that at least one category has been saved. If verification is pending, check dates, a saved category, organiser details and a linked venue. If the event should show REGISTRATION OPEN, check registration start and end times on the Registration step. Status may recalculate approximately once an hour, but waiting will not fix missing setup requirements. In Manual mode, the status does not change automatically.

  Intent: category missing or not saved: Explain that clicking `+` only adds a category to the current list. The user must click Create or Update at the bottom of the panel to save it. If the Class list is empty, choose Category Levels and Participant Type first. If the category is saved but players still cannot register, the issue may involve another step; ask what the user sees on the Registration page rather than assuming the Details page is the cause.

  Intent: image or poster upload failure: First identify which image field the user means if it is unclear. Explain the correct format, size limit and dimensions for that field. For a thumbnail, use PNG/JPG/JPEG, exactly 379 × 200 px, less than 1 MB; WEBP is rejected by the server. For the banner, recommend 1200 × 360 px and allow up to 15 MB. For the logo, use PNG/JPG/JPEG up to 1 MB.

  Intent: cannot edit or delete an event: Distinguish view mode, missing permissions, creator-only deletion and restrictions after ranking points are published to OTT. Tell the user to click Edit if the page is in view mode. If the button is missing, an administrator may need to check permissions. If points are published, explain which changes are locked.

  Intent: date changes or schedule reset: Explain the reset confirmation before the user accepts it. A confirmed reset removes planning and schedule data on affected dates. Days with played matches cannot be removed. Explain that Tournament venue days follow the event dates, while League venues retain their agreed days except dates outside the new event range.

  Intent: verification pending or rejected: Explain the meanings of Pending, Accepted and Rejected. For a rejected event, use View Feedback, fix the listed issues and resubmit. If Send Verification is disabled, check Edit mode, saved event state, section completion and whether the event has already been accepted. Do not invent a review timeline; none is specified in this guide.

  Intent: duplicate name or invalid event name: Explain that the same Event Name and Event Type combination cannot already exist, and names cannot consist only of numbers. Suggest a descriptive alternative, such as `Open 2026`, without claiming that an unverified name is available.

  When to ask a follow-up question:
  Ask a brief, focused question when the user's wording does not
  distinguish between problems with different solutions.

  Examples:

  -   "I can't change it." → "Which field are you trying to change: the
      event name, dates, category or something else?"
  -   "The image isn't uploading." → "Are you uploading the Event Banner,
      Thumbnail or Logo?"
  -   "My event isn't working." → "What is happening: is the event status
      INCOMPLETE, is the Publish button missing, or can players not
      register?"
  -   "Category isn't showing." → "Is the category missing from the Add
      Class/Category list, or is it saved there but missing from
      registration?"
  -   "I can't delete it." → "Do you see an error message, or is the
      Delete button missing?"

  Do not ask for information that is already provided in the user's
  question. Do not ask the user to provide an event ID unless checking
  live event data or a support workflow actually requires it.
---

# Event Details page --- Create, Edit and Troubleshoot an Event

## Purpose of this guide

This guide explains how to create and edit an event in the Stupa
Tournament Management System (TMS). It covers the fields, buttons,
rules, common errors, and next steps on the **Details** page.

It is written for organisers who may describe a problem in everyday
English, Hindi, or Hinglish. Users may not know the exact name of a
button or setting. Match their meaning to the documented behaviour, then
explain the solution in simple language.

## Quick navigation

-   [Where to find the page](#where-to-find-the-page)
-   [Page sections](#page-sections)
-   [Create or edit an event](#create-or-edit-an-event)
-   [Event fields](#event-details-panel-fields)
-   [Banner, thumbnail and logo](#banner-thumbnail-and-logo)
-   [Generate a banner with AI](#generate-a-banner-with-ai)
-   [Add, edit and reorder categories](#add-classcategory-or-division)
-   [Extra information sections](#extra-information-sections)
-   [Venue details](#venue-details)
-   [Verification and publishing](#verification-and-publishing)
-   [Understand automatic event
    status](#understand-automatic-event-status)
-   [Change event dates safely](#change-event-dates-safely)
-   [Errors and troubleshooting](#common-errors-and-how-to-fix-them)
-   [Editing and deleting after points are
    published](#editing-or-deleting-after-points-are-published)
-   [Natural-language question
    patterns](#natural-language-question-patterns)
-   [When to ask a follow-up
    question](#when-to-ask-a-follow-up-question)

## Where to find the page

1.  Open **Event** from the sidebar.
2.  Open the **Details** step, the first step in event setup.

-   **Page route:** `/tms/event-settings/create-event/<event_id>`
-   Example: `/tms/event-settings/create-event/1358` opens event 1358.
-   An event ID of `0` means a new event that has not been saved yet.
-   **Page heading:** Details
-   **Breadcrumb:** Tournaments \> Event
-   The setup steps may include Registration, Playing Order, Draw
    Settings, Payment & Invoice, Umpire Settings, Referee Settings, Day
    Planner, Print Settings, Access-Control, Documents and Sponsors. The
    steps available depend on the organisation's configuration. Create
    the event on the Details step first.
-   The left-hand menu (Event, Players, Fixtures/Results, Schedule,
    Scoring and Streaming, Awards and Standing, Printing, Display
    Settings, Export/Share Results) relates to the event as a whole, not
    only to the Details page.

Use this page to enter event information, add categories or divisions,
complete any extra information sections, link a venue, request
verification when required, and publish the event.

## Page sections

The Details page contains collapsible panels. Select a panel title to
open it; only one panel is open at a time.

1.  **Event Details** --- event name, status, type, dates, level,
    season, banner, thumbnail, logo, description and any custom fields.
2.  **Add Class/Category** --- categories participants can enter. For a
    League, this panel is called **Add Division**.
3.  **Extra information sections** --- organisation-specific fields,
    such as organiser or contact details. Names and fields vary by
    organisation and event type.
4.  **Venue Detail** --- the venue linked to the event.

Each panel has a status icon:

-   **Grey tick:** the section is not complete.
-   **Blue tick:** the section is complete.

The Event Details panel is complete once the event has been created. Add
Class/Category is complete after at least one category is saved. Extra
sections are complete when all mandatory fields are filled. Venue Detail
is complete when a venue is linked.

## Create or edit an event

### Create a new event

1.  Open the Details step for a new event.
2.  Fill in all mandatory fields. Fields marked with a red `*` are
    required.
3.  Upload the required banner, thumbnail and logo.
4.  Click **Create** at the bottom of the Event Details panel.
5.  After the event is created, add at least one category and save it.
6.  Complete any mandatory extra information sections.
7.  Link a venue if required.
8.  If the event level requires verification, complete all sections and
    send the event for verification.
9.  Once verification is accepted, use the **Publish** toggle when it
    becomes available.

Mandatory fields for creating an event include Event Name, Event Status,
Event Type, Start Date, End Date, Event Levels, Event Banner, Thumbnail
and Logo, plus any organisation-defined mandatory custom fields.

### Edit an existing event

Existing events open in **view mode**, so fields look greyed out and
cannot be changed.

1.  Click **Edit** at the top right.
2.  Change the required fields.
3.  Click **Update** in the panel you changed.

Each panel saves separately. Clicking Update in one panel does not save
unsaved changes in another panel.

There is no dedicated **Cancel edit** button. To discard unsaved
changes, leave or reload the page without clicking Update.

### Edit and Delete permissions

If **Edit** or **Delete** is missing, the user's role may not have Edit
permission for **Event Management (Event Details)**. Ask an
administrator to check the user's access.

Only the user who created an event can delete it. An event whose ranking
points have been published to OTT cannot be deleted.

### Delete an event

1.  Click **Delete** at the top right of an existing event.
2.  Confirm the prompt: "Are you sure you want to delete this event?"
3.  On success, the message "The Tournament is deleted successfully"
    appears and the user returns to the events list.

Deleting an event removes it from event lists. Its name can be reused.
Calculated ranking lists that have not been published for the event are
removed. Deletion does not show the schedule-reset confirmation.

## Event Details panel fields

Fields marked with a red `*` are mandatory.

-   **Event Name**\* --- free text, maximum 50 characters. It must not
    contain only numbers. For example, `2026` is not allowed, but
    `Open 2026` is allowed.
-   **Event Status**\* --- controlled by the Auto/Manual toggle.
    -   **Manual:** the user chooses a status from the organisation's
        configured list. The system does not change that status
        automatically, even when dates pass.
    -   **Auto:** the system manages the status. A newly created event
        starts as `INCOMPLETE`.
-   **Event Type**\* --- Tournament or League. Default: Tournament. It
    cannot be changed after the event has been created. Changing the
    type before creation reloads the extra sections for that type.
-   **Start Date**\* --- choose a date from the calendar.
-   **End Date**\* --- unavailable until a Start Date is chosen and
    cannot be earlier than the Start Date. Changing the Start Date
    clears the End Date, so select the End Date again.
-   **Event Levels**\* --- choose from the levels configured by the
    organisation. The selected level determines whether verification is
    required before publishing. It cannot be changed after event
    creation.
-   **Link Event (Master)** --- optional toggle for linking this event
    to a master event. It is not shown for every organisation.
-   **Season** --- optional. Only active seasons are listed. Choosing a
    season loads the licences available for that season.
-   **License** --- optional multi-select field shown only for
    organisations using licences. The list stays empty until a Season is
    selected.
-   **Event Description** --- optional free text.
-   **Custom fields** --- the organisation may add fields at the bottom
    of this panel. A red `*` indicates a mandatory field.

### Linking a master event

1.  Turn on the **Master** toggle. The **Link Master Tournament** side
    panel opens.
2.  Search by typing at least two characters, or scroll the list. More
    events load as the list is scrolled.
3.  Select the event and click **Save**.
4.  The linked event name appears as a link. Click it to change the
    selection.
5.  Click **Create** or **Update** in Event Details to store the link.

Turning the toggle off removes the link. Closing the side panel without
selecting an event turns the toggle back off.

## Banner, thumbnail and logo

The banner, thumbnail and logo are different image fields and have
different rules.

### Event Banner

-   Recommended dimensions: **1200 × 360 px**.
-   Maximum file size: **15 MB**.
-   You can upload an image, select a predefined image, or use
    **Generate with AI**.
-   Predefined images may be grouped by sport, such as Table Tennis,
    Padel, Tennis and Badminton.
-   To replace a banner, hover over it and select **Reupload**.
-   When creating a new event, selecting a banner also fills the
    Thumbnail automatically unless a custom thumbnail has already been
    uploaded.
-   On an existing event, changing the banner does not change the
    thumbnail.
-   A file larger than the allowed limit may show: "File Exceed max
    limit of 15mb."

### Thumbnail

-   Required dimensions: **exactly 379 × 200 px**.
-   File size: **less than 1 MB**.
-   Use **PNG, JPG or JPEG**.
-   The field may list WEBP, but the server rejects WEBP. Use PNG or JPG
    instead.
-   Select **Change** to replace the thumbnail.

Possible errors:

-   "Only PNG, JPG, JPEG, and WEBP files are allowed" --- the file type
    is not allowed by the screen. Even if WEBP passes this initial
    check, the server rejects it.
-   "Thumbnail size should be less than 1MB" --- reduce the file size.
-   "Thumbnail dimensions must be exact 379x200px" --- resize the image
    to exactly 379 × 200 pixels.

### Logo

-   Allowed formats: **PNG, JPEG or JPG**.
-   Maximum file size: **1 MB**.
-   Select **Change** to replace the logo.

Possible errors:

-   "Only PNG, JPEG, and JPG files are allowed"
-   "Logo size should be less than 1MB"

### Server upload rules

The server accepts files with these types: PNG, JPG, JPEG, HEIC, HEIF,
AVIF, PDF, DOC and DOCX. The server's maximum size is 15 MB, while the
screen applies stricter limits for thumbnail and logo. WEBP is not
accepted by the server.

The file's actual content must match its extension. Renaming a WEBP file
to `.png` does not convert it and will not make it valid. The user must
be signed in; an expired session can also cause upload failure.

If an upload shows **File upload failed**:

1.  Confirm that the correct file type is used for that field.
2.  Check the field-specific size limit.
3.  For thumbnails, confirm the exact dimensions are 379 × 200 px.
4.  Make sure the file has not simply been renamed to a different
    extension.
5.  Try again after confirming the user is signed in.
6.  If it still fails, contact support.

## Generate a banner with AI

The **Generate with AI** button beside Event Banner opens the **Generate
Banner with AI** window.

1.  Enter a description under **Describe your event banner**, or choose
    a Quick suggestion.
2.  Click **Generate**. A preview appears while "Painting pixels..." is
    displayed.
3.  If the image is suitable, click **Use as Event Banner**. The image
    is uploaded and selected as the event banner.
4.  Click **Cancel** to close without using the generated image.
5.  To try another image, change the description and click **Generate**
    again.

Notes:

-   The generator is tuned for table tennis images.
-   "Generation failed. The model may be loading. Try again in a
    minute." --- wait about a minute and retry.
-   "AI Image API Not Configured" --- the feature is not configured for
    this installation. Contact support.
-   The banner is stored with the event only after **Create** or
    **Update** is clicked in the Event Details panel.

## Add Class/Category or Division

The **Add Class/Category** panel controls which categories participants
can enter. For a League, the panel is called **Add Division**, and
categories are called divisions.

The event must be created first, and the page must be in Edit mode.

### Add a category

1.  Select **Category Levels**. For a League, the field is called
    **Division**.
2.  Select **Participant Type**: Singles, Teams, Doubles or Mix-Doubles.
    For a League, only Teams is available.
3.  Select **Class**. The list is populated after Category Levels and
    Participant Type are selected. Use the search box if needed.
4.  Optionally enter an **Abbreviation** (maximum 50 characters).
5.  Optionally choose a **Color**.
6.  Click the **+** button. The category appears in the list.
7.  Click **Create** for the first save or **Update** for later changes
    at the bottom of the panel.

**Important:** Clicking `+` only adds the category to the on-screen
list. It does not save the category permanently. You must click Create
or Update.

Errors when adding a category:

-   "Please select Participant Type" --- choose a participant type.
-   "Please select Category" --- choose a Class.
-   "Please select Category Levels" --- choose the level first.
-   "Category Already Added In List" --- the same class is already in
    the event.

If the Class list is empty, select Category Levels and Participant Type
first. If it says "No matching data found," try another search term or
confirm that the required selections are correct.

### Primary Display Selection

Choose **Class** or **Abbreviation** at the top of the panel. This
determines which label appears for categories across the event's
screens. Save the choice with Create or Update.

### Edit a category

1.  Click the pencil icon for a category that has already been saved.
2.  The **Edit category** side panel opens. For a League, it is called
    **Edit Division**.
3.  Review the required fields: Name, Participant Type, Gender Selection
    and Category Level. Other fields include Abbreviation, Born After,
    Born Before, Minimum Points, Maximum Points and Color.
4.  Click **Save**.

"Please fill all required fields" means one or more required fields are
empty.

The pencil icon is only available for categories that have already been
saved.

### Reorder categories

1.  Enter Edit mode.
2.  Drag a category row using the dotted handle on the left.
3.  Place it in the required order.
4.  Click **Update** to save the new order.

The saved order is used wherever event categories are listed.

### Delete a category

1.  Click the red bin icon and confirm "Are you sure you want to delete
    this category?"
2.  Click **Update** at the bottom of the panel to make the deletion
    permanent.

Until Update is clicked, reloading the page restores the previously
saved category. Deleting a category removes all participants entered in
it. This cannot be undone from this screen.

A category cannot be deleted if fixtures have already been generated for
it; delete its stages on the Fixtures screen first. Deletion is also
blocked if ranking points for that category have been published to OTT.

A newly added category inherits its minimum and maximum points, Born
After and Born Before dates, and gender from the selected class.

A category with participant type **Teams** makes the team leaderboard
available for the event.

### Category changes after points are published

For a category whose ranking points have been published to OTT:

-   Deleting the category is blocked.
-   Changing its Abbreviation, Color or Category Level is blocked.
-   Reordering it or saving it unchanged is allowed.
-   Some category changes may be skipped while other changes are saved.
    The system may display: "Category changes saved. N category
    change(s) were skipped because points for those categories are
    already published on OTT."
-   If every attempted change affects a category with published points,
    a points-published restriction message may appear.

## Extra information sections

Additional sections may appear below the category panel. They are
configured by the organisation for the selected event type. They become
editable only after the event has been created and the page is in Edit
mode.

-   Supported field types can include text, email, number, date,
    dropdown and image upload.
-   Text fields allow up to 50 characters.
-   Number fields accept digits only on the screen.
-   Click **Create** for the first save or **Update** for later saves.
    Each section is saved separately.
-   A missing required field may show: `"<field name> Is Required ."`.
-   An invalid email may show: "Invalid email format".
-   Sections containing an **Organiser** field have a **Publish**
    toggle. Turn it on and save to publish that section's information.
    Turn it off and save to unpublish it.

## Venue details

The Venue Detail panel says: "Select a venue created in Venue Management
to view its form or create your own."

1.  Choose a venue from the **Select Venue** dropdown. The dropdown
    includes search.
2.  Review the venue's details, which are read-only in this panel.
3.  Click **Update** to link the venue to the event.
4.  The panel's tick turns blue after a venue is linked.

If the list says **No venues found**, no matching venue is available in
the list. Check the search term or use **Add new venue** to create a
venue without leaving the page.

Other rules:

-   The first venue linked to an event becomes the primary/default
    venue.
-   For a Tournament, a newly linked venue receives all the event's
    dates.
-   For an event waiting for verification, a venue is needed before Auto
    status can move from INCOMPLETE to UNVERIFIED when the other
    required conditions are met.
-   "No Venue Found" means the venue was deleted. Choose another venue.
-   "Cannot remove dates with scheduled matches" means matches are
    scheduled on a date being removed from that venue. Unschedule those
    matches first.

For a League, venue days are managed differently; see [Changing event
dates safely](#changing-event-dates-safely).

## Verification and publishing

Verification and publishing are different steps.

### Send an event for verification

Some Event Levels require the event to be approved before it can be
published. The selected Event Level determines whether verification is
required.

If verification is required, **Send Verification** appears in the bottom
action bar. It is enabled only when:

-   The page is in Edit mode.
-   The event has been created.
-   All sections show a blue tick.
-   The event has not already been accepted.

Possible messages:

-   "Please save the event first before sending for verification"
-   "Please complete all sections before sending for verification"
-   "Event sent for verification successfully"

After sending the event for review, a status banner appears:

-   **Event Pending** --- waiting for review.
-   **Event Accepted** --- approved. **View Details** shows
    "Verification Successful".
-   **Event Rejected** --- not approved. **View Feedback** shows
    "Verification Failed" and the reviewer's feedback. Fix the issues
    described in the feedback and send the event for verification again.

Events whose level does not require verification are accepted
automatically when created. An event created by the main administrator
account is verified automatically.

### Publish the event

The **Publish** toggle is in the bottom action bar.

It appears only after the event is saved and its verification status is
Accepted. For an event level that requires verification, the event must
first be approved. The user must be in Edit mode to use the toggle.

-   Turn the toggle on to publish the event.
-   Turn it off to unpublish the event.
-   The change is saved immediately and a confirmation message appears.

If Publish is missing, check:

1.  Has the event been created and saved?
2.  Does the Event Level require verification?
3.  If required, has the event been accepted?
4.  Are you in Edit mode?
5.  Are you checking the bottom action bar on the Details step?

Do not tell users that sending the event for verification automatically
publishes it. Verification approval and publishing are separate actions.

## Understand automatic event status

In **Auto** mode, the system calculates Event Status. It recalculates
after relevant event, category or verification changes and approximately
once an hour. Status timing uses the venue's time zone.

The system checks these conditions in order:

1.  Verification rejected → **REJECTED**.
2.  No active category on the event → **INCOMPLETE**.
3.  Verification pending → **UNVERIFIED** if the event has dates, at
    least one category, an organiser and a venue; otherwise
    **INCOMPLETE**.

If none of those conditions applies, the status is selected from the
event's current state:

-   **RECENT** --- today is after the End Date.
-   **ONGOING** --- today is between the Start Date and End Date and
    registration is not open.
-   **UPCOMING** --- the day before the Start Date, if registration is
    not open and no draw exists.
-   **REGISTRATION OPEN** --- registration is open for at least one
    category. This takes precedence even after the Start Date.
-   **DRAWS OUT** --- a draw (fixtures) exists and the event has not
    started.
-   **REGISTRATION CLOSED** --- the last registration end time has
    passed and the event has not started.
-   **VERIFIED** --- verification is accepted, or the Event Level does
    not require it.

### Manual status mode

In **Manual** mode, the system does not change the status automatically.
The status stays as selected, even after the event dates pass.

-   Switching from Manual to Auto and saving recalculates the status
    immediately.
-   Switching from Auto to Manual keeps the current status until the
    user changes it.
-   If Auto status remains INCOMPLETE, first check whether at least one
    category has been saved.
-   If verification is pending and the event remains INCOMPLETE, check
    that the event has dates, a category, organiser details and a linked
    venue.
-   If registration is not showing as open, check registration start and
    end times on the Registration step.
-   A status update may also take time because the system recalculates
    approximately once an hour. Do not suggest waiting as the only fix
    when a required setup item is missing.

## Changing event dates safely

Changing Start Date or End Date can affect venue days, planning, matches
and officials.

If the event already has venue days, plans or schedules on dates being
removed, the system displays:

**"Changing these dates will reset the schedule"**

The message explains that event planning and match schedules will be
cleared for affected days. It lists the venues and the number of days to
be removed, as well as official registrations that will be withdrawn.

-   Click **Yes, reset** to apply the date change and clear affected
    days.
-   Click **Cancel** to keep the existing dates. If you cancel, none of
    the changes in that save are stored, including other fields changed
    in the same save.
-   If a date being removed has played matches, the date change is
    refused and the message names the affected dates. A day with played
    matches cannot be removed.
-   The same warning can appear when publishing or deleting an event.

### What happens to venue days?

**Tournament**

-   Venues follow the event's date range.
-   When dates are added, the new days are added to every venue.
-   When dates are removed, those days are removed from every venue.
-   If a venue is left with no days, it receives all the new event days.

**League**

-   Each venue keeps its own agreed days.
-   Extending the event does not automatically add days to venues.
-   Venue days outside the new event date range are removed.

After a confirmed date reset, the system removes affected planning and
schedule data: matches are unscheduled, Day Planner plans and breaks are
deleted, club venue registrations are cancelled, and umpire and referee
registrations are withdrawn. If the Start Date moves, officials' day
numbering is renumbered.

If a day already has played matches, keep that day within the event date
range. The error may appear as `EVENT_DATES_HAVE_STARTED_MATCHES`
followed by the dates.

If the dates have not changed, saving the event does not modify venue
days.

## Common errors and how to fix them

### "Event Already Exists"

**What it means:** An event with the same name and the same Event Type
(Tournament or League) already exists.

**What to do:** Choose a different event name. The same name can be
reused after the original event is deleted. This check also runs when
renaming an event.

### "Event name must not be purely numeric"

**What it means:** The name contains only a number, such as `2026`,
`0999`, `-3` or `3.5`.

**What to do:** Add descriptive words, such as `Open 2026`. Names that
contain both letters and digits are allowed.

An existing event with a numeric name may still be edited if its name is
not changed.

### "You can't skip mandatory fields"

**What it means:** A required field, banner or thumbnail is missing.

**What to do:** Look for red-bordered fields and complete the required
information before clicking Create or Update.

### "Please upload a thumbnail"

**What it means:** The thumbnail is missing.

**What to do:** Upload a PNG, JPG or JPEG that is exactly 379 × 200 px
and smaller than 1 MB.

### "Invalid email format"

**What it means:** An email field contains an address that does not
match the expected email format.

**What to do:** Check for typing mistakes, spaces or a missing part of
the email address.

### "You are typing an invalid key"

**What it means:** A number field has received a character other than a
digit.

**What to do:** Enter digits only in that field.

### "Sport default configs are required"

**What it means:** No sport is configured for the organisation, so the
event cannot be created.

**What to do:** Contact the organisation's administrator or support.
This is not something the organiser can fix by changing ordinary event
fields.

### "No Event Found"

**What it means:** The event may have been deleted, or the page URL
contains an incorrect event ID.

**What to do:** Return to the event list and open the event again. If it
is missing, ask an administrator to check it.

### "Unauthorized Access"

**What it means:** The session may have expired, or the user is trying
to delete an event they did not create.

**What to do:** Sign in again and retry. If the issue occurs while
deleting, confirm that the current user created the event.

### "Access Denied"

**What it means:** The user's role is not allowed to work on the event.

**What to do:** Ask an administrator to review the user's permissions.

### "File upload failed"

**What it means:** The server rejected the file or did not receive it
successfully.

**What to do:** Check the allowed file type, the field-specific size
limit, the image dimensions where required, and whether the file's
actual content matches its extension. Confirm the user is signed in.
WEBP is not accepted by the server.

### "Generation failed. The model may be loading. Try again in a minute."

**What it means:** The AI banner generator may not be ready.

**What to do:** Wait about a minute and try Generate again.

### "AI Image API Not Configured"

**What it means:** The AI banner feature is not configured for this
installation.

**What to do:** Contact support.

### "Please select Participant Type"

**What it means:** No participant type was selected while adding a
category.

**What to do:** Select Singles, Teams, Doubles or Mix-Doubles. For a
League, select Teams.

### "Please select Category"

**What it means:** No Class was selected.

**What to do:** Choose a Class after selecting Category Levels and
Participant Type.

### "Please select Category Levels"

**What it means:** The category level was not selected.

**What to do:** Select Category Levels first.

### "Category Already Added In List" or "Category Already Exists"

**What it means:** The class is already in the event or appears more
than once in the list being saved.

**What to do:** Remove the duplicate and save the category list again.

### "Cannot Delete Category, Fixtures Already Generated"

**What it means:** Fixtures have already been generated for the
category.

**What to do:** Open the Fixtures screen and delete the category's
stages first. A category with only draft stages may be deleted.
Published ranking points may also block deletion.

### "No Venue Found"

**What it means:** The venue linked to the event was deleted.

**What to do:** Select a different venue in Venue Detail.

### "Cannot remove dates with scheduled matches"

**What it means:** Matches are scheduled on a venue date that is being
removed.

**What to do:** Unschedule the affected matches before removing the
date.

### "Please complete all sections before sending for verification"

**What it means:** At least one required section is incomplete.

**What to do:** Check the section status icons and fill the missing
mandatory information. Every section must show a blue tick before
sending for verification.

### "This action is not permitted. Points for this event have been published to OTT..."

**What it means:** The requested change affects event or category
information locked after ranking points have been published to OTT.

**What to do:** Review [Editing or deleting after points are
published](#editing-or-deleting-after-points-are-published). If the
requested change is blocked, contact the administrator for guidance.

## Editing or deleting after points are published

Once ranking points for an event have been published to OTT, changes
that affect those points are restricted.

### Changes blocked on the Details page

-   Event Name
-   Start Date
-   End Date
-   Event Type
-   Event Levels
-   Season
-   Event Status
-   Publish toggle
-   Primary Display Selection

Deleting the event is also blocked.

The system may show a message explaining that event, category or stage
changes are not allowed after points have been published. Match-level
changes, such as editing results or adding/deleting matches, may still
be permitted and can require recalculation.

### Changes that may still be allowed

-   Banner
-   Thumbnail
-   Logo
-   Description
-   Extra information sections
-   Settings on other steps, such as umpire, referee, accommodation and
    travel

Saving without changing a locked field is not blocked.

For a category with published points, deleting it or changing its
Abbreviation, Color or Category Level is blocked. Reordering it or
saving it unchanged is allowed.

## What happens automatically when an event is created?

After Create succeeds, the system:

-   Copies default rule settings for the sport and event type into the
    event.
-   Copies the organisation's default print alert settings. Later
    changes to the organisation defaults do not change this event's
    copied settings.
-   Creates payment settings for the event.
-   Gives the creator access to the event.
-   Does not add a venue automatically; add one in Venue Detail.
-   Starts the event as INCOMPLETE if Auto status mode is selected.
-   Automatically verifies an event created by the main administrator
    account.

## External events

The same form is used for **External Events**, which are events held
outside the system but registered for ranking calculations.

Differences from regular events:

-   Event Type is fixed to Tournament.
-   Only Event Details and Add Class/Category panels are shown.
-   There is no verification step.
-   There is no Delete button.
-   The Publish toggle is available as soon as the event is saved.

## Natural-language question patterns

Users may ask about a feature without using the exact UI wording. The
examples below are alternate ways of asking about documented behaviour,
not additional product features.

### Intent: create an event

Possible questions: - "How do I create a tournament?" - "I want to add a
new event." - "Tournament kaise banau?" - "Naya event create karna hai,
where do I start?" - "What details do I need before creating an event?"

### Intent: event not visible or not live

Possible questions: - "My tournament is not live." - "Players cannot see
my event." - "Event publish nahi ho raha." - "How do I make the
tournament public?" - "The Publish button is missing." - "Event create
ho gaya but live nahi hai."

### Intent: event stuck on INCOMPLETE

Possible questions: - "Why is my event still incomplete?" - "Sab details
bhar di, phir bhi incomplete aa raha hai." - "Tournament ready kyun nahi
ho raha?" - "Why has my event status not changed?" - "I added the
details but status is not updating."

### Intent: category missing or not saved

Possible questions: - "I added a category but it disappeared." -
"Category add ki thi, save nahi hui." - "Why can't I find my class?" -
"Where do I add Singles or Doubles?" - "Class dropdown empty hai." -
"Players cannot register for the category I added."

### Intent: image or poster upload failure

Possible questions: - "My tournament poster is not uploading." - "Banner
upload nahi ho raha." - "Thumbnail error aa raha hai." - "Can I upload
WebP?" - "What size should my event image be?" - "Logo upload failed."

### Intent: cannot edit or delete an event

Possible questions: - "Edit button is not showing." - "Event ke fields
grey hain." - "I cannot change the tournament name." - "Why is my event
locked?" - "Delete option nahi aa raha." - "Why can't I delete this
tournament?"

### Intent: date changes or schedule reset

Possible questions: - "I changed the dates and my schedule
disappeared." - "Date change karne par matches delete honge?" - "Why is
it asking to reset the schedule?" - "Can I move the tournament after
matches have started?" - "My venue dates changed automatically."

### Intent: verification pending or rejected

Possible questions: - "How long until my event is approved?" - "My event
is pending." - "Event reject ho gaya, what now?" - "Where can I see
reviewer comments?" - "I cannot send it for verification."

### Intent: duplicate name or invalid event name

Possible questions: - "Why can't I use this tournament name?" - "Event
Already Exists aa raha hai." - "Can two tournaments have the same
name?" - "Why is 2026 not accepted as the event name?"

## Frequently asked questions

### How do I create an event?

Open Details for a new event, fill all mandatory fields, upload the
banner, thumbnail and logo, then click Create. Add categories and
complete other required sections afterward.

### Why are all fields greyed out?

An existing event opens in view mode. Click Edit at the top right. If
Edit is missing, ask an administrator to check permissions.

### Why can't I pick an End Date?

Choose the Start Date first. If you change the Start Date, the End Date
is cleared and must be selected again.

### Why can't I change Event Type or Event Levels?

Both are locked after the event has been created.

### Why is the License list empty?

Choose a Season first. Licences are loaded for the selected season. This
field is only available for organisations that use licences.

### What size should the banner be?

The recommended banner size is 1200 × 360 px, with a maximum file size
of 15 MB.

### What size should the thumbnail be?

Exactly 379 × 200 px, smaller than 1 MB, in PNG, JPG or JPEG format.
WEBP is rejected by the server.

### Why does my logo upload fail?

Use PNG, JPEG or JPG and keep the file within the 1 MB limit.

### I added categories, but they disappeared after reloading. Why?

Click Create or Update at the bottom of Add Class/Category after using
the plus button. The plus button alone does not save categories.

### Why is the Class dropdown empty?

Select Category Levels and Participant Type first.

### Why is there no pencil icon on a category?

The category must already have been saved using Create or Update before
it can be edited.

### Why is Send Verification disabled?

Make sure you are in Edit mode, the event is saved, every section has a
blue tick, and the event has not already been accepted.

### Why can't I see the Publish toggle?

The event must be saved and its verification status must be Accepted.
Check the bottom action bar while in Edit mode.

### Why can't I publish my event? (event not live)

Publishing the event is done on this Details step with the **Publish**
toggle in the bottom action bar. It does not depend on standings,
results or awards. If you cannot publish, check:

1.  The event has been created and saved.
2.  If the Event Level requires verification, the event has been
    sent for verification and is **Event Accepted**. A rejected event
    must be fixed and sent again.
3.  You are in Edit mode.
4.  You are looking at the bottom action bar of the Details step.

Turn the **Publish** toggle on to publish the event; the change is
saved immediately.

### Why is my event not visible to players?

Players see an event only after it is published. Publish it on this
Details step with the **Publish** toggle in the bottom action bar. The
toggle shows only when the event is saved, its verification is
**Event Accepted** (when the Event Level requires verification) and you
are in Edit mode. If players can see the event but cannot register,
check the Registration step instead.

### What happens if I change event dates?

After confirmation, planning and match schedules on removed days are
cleared, along with other affected registrations and plans. Days with
played matches cannot be removed.

### Why can't I edit after publishing points?

Event Name, dates, type, level, season, status and publish state are
locked after ranking points are published to OTT. Some other fields
remain editable.

### What happens to players if I delete a category?

All participants entered in that category are removed when you click
Update. This cannot be undone from this screen.

### Why can't I delete a category?

Fixtures may already have been generated, or ranking points may have
been published. Delete the relevant stages first when fixtures are the
blocker. Published points can prevent deletion.

### How do I create a tournament?

Open **Event** from the sidebar; a new event opens on the **Details** step. Fill in the mandatory fields, upload the banner, thumbnail and logo, then click **Create**. Add the categories and complete the other setup steps afterwards.

### How do I add categories to this event?

On the **Details** step, in Edit mode, open **Add Class/Category**: choose **Category Levels**, **Participant Type** and **Class**, optionally an abbreviation and a colour, and click **+**. Then click **Create** (or **Update**) at the bottom of the panel; **+** alone does not save the category.

### Why do I get "Event Already Exists"?

An event with the same name and the same Event Type (Tournament or League) already exists. Choose a different event name; the name can be reused after the original event is deleted.

### Why is the status stuck on INCOMPLETE?

In Auto mode the status is INCOMPLETE while the event has no active category, or while verification is pending and the event is missing dates, a category, an organiser or a venue. Add what is missing; the status is recalculated after changes and about once an hour.

### Why can't I edit or delete my event?

If **Edit** or **Delete** is missing, your role may not have Edit permission for Event Details; ask an administrator. Only the user who created an event can delete it, and an event whose ranking points were published to OTT cannot be deleted.

### Why did changing the event dates remove schedules?

Removing days from the event clears the planning and match schedules on those days. The warning "Changing these dates will reset the schedule" lists what will be cleared; click **Cancel** to keep the old dates. Days with played matches cannot be removed.

### Why is my image upload failing?

Check the file type and size for that field: the logo must be PNG, JPEG or JPG within 1 MB, and the thumbnail exactly 379 × 200 px. WEBP is not accepted, and renaming a file does not change its type. An expired sign-in can also make uploads fail.

## Source-of-truth and escalation rules

-   This guide documents the Event Details page. It does not prove the
    current state of a specific event.
-   Do not infer an event's actual status, visibility, verification
    result, category list, venue, permissions or upload result without
    access to live application data.
-   If the user reports a current event-specific problem, provide
    documented checks first. If the answer depends on data not available
    to the assistant, say what needs to be checked in TMS or by an
    administrator.
-   Organisation-specific fields, statuses, event levels, sport
    configurations and extra sections may vary.
-   Do not invent review timelines, upload retry limits, event
    visibility rules beyond those documented here, or undocumented
    backend behaviour.
-   If a server-side configuration issue is indicated, such as "Sport
    default configs are required" or "AI Image API Not Configured,"
    direct the user to the organisation's administrator or support.
