---
doc_id: tms.event-settings.create-event
title: Event Details page
routes:
  - tms/event-settings/create-event/:event_id
aliases:
  - event details
  - details step
  - create event
  - edit event
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I add categories to this event?
  - Why do I get "Event Already Exists"?
  - Why is the status stuck on INCOMPLETE?
  - What size should the banner and thumbnail be?
backend_sources:
  - gateway/src/routers/events_router.py
  - gateway/src/main.py (file_upload)
  - tms/src/service/events_service.py
  - tms/src/service/event_status_calculator.py
  - tms/src/service/points_state_guard.py
  - tms/src/utils/event_date_sync.py
source_files:
  - src/app/modules/tms/create-tournament/create-tournament.component.ts
  - src/app/modules/tms/create-tournament/create-tournament.component.html
  - src/app/shared/ai-banner-generator-dialog/ai-banner-generator-dialog.component.html
  - src/app/shared/ai-banner-generator-dialog/ai-banner-generator-dialog.component.ts
  - src/app/modules/admin/venue-management/event-venue/event-venue-section.component.html
  - src/app/shared/components/category-view/category-view.component.html
---
# Event Details page (Create / Edit Event) – user guide

This guide describes the **Details** step of an event in the Stupa Event Management System (admin panel). It is the page where an organiser creates a new event or edits an existing one. Use it to answer questions about fields, buttons, rules, error messages and what to do next on this page.

## Event Details page: where it is and what it is for

- Page address: `/tms/event-settings/create-event/<event id>`. Example: `/tms/event-settings/create-event/1358` opens event 1358. An id of `0` means a new event that has not been saved yet.
- Page heading: **Details**. Breadcrumb: **Tournaments > Event**.
- It is step **1 – Details** in the row of event setup steps at the top. The other steps (for example Registration, Playing Order, Draw Settings, Payment & Invoice, Umpire Settings, Referee Settings, Day Planner, Print Settings, Access-Control, Documents & Sponsors) depend on what is enabled for the organisation. They need the event to be created on the Details step first.
- The left menu (Event, Players, Fixtures/Results, Schedule, Scoring and Streaming, Awards and Standing, Printing, Display Settings, Export/Share Results) belongs to the event as a whole, not to this page.
- What you do on this page: enter the event's basic information, add its categories (classes) or divisions, fill any extra information sections, choose the venue, send the event for verification if required, and publish it.

## Event Details page: sections (accordion panels)

The page is a list of collapsible panels. Click a panel title to open it. Only one panel is open at a time.

1. **Event Details** – name, status, type, dates, level, season, banner, thumbnail, logo, description.
2. **Add Class/Category** (shown as **Add Division** for a League) – the categories players or teams can enter.
3. **Extra sections** – additional information sections set up by the organisation for the chosen event type (for example organiser or contact details). The names and fields differ per organisation.
4. **Venue Detail** – the venue used by the event.

Each panel title has a status icon: a **grey tick** means the section is not complete, a **blue tick** means it is complete.

- Event Details is complete once the event has been created.
- Add Class/Category is complete once at least one category is saved.
- An extra section is complete when all its mandatory fields are filled.
- Venue Detail is complete once a venue is linked to the event.

## Event Details page: view mode, Edit button and Delete button

- A **new event** opens ready to fill in, with a **Create** button at the bottom of the Event Details panel.
- An **existing event** opens in **view mode**: fields are greyed out and cannot be changed. Click **Edit** (top right) to switch to edit mode. In edit mode the panels show **Update** buttons, and category editing, drag-and-drop ordering, the section Publish toggles and the bottom action bar become usable.
- If you cannot see **Edit** or **Delete**, your role does not have Edit permission for "Event Management (Event Details)". Ask an administrator for access.
- There is no "Cancel edit" button. To discard unsaved changes, leave or reload the page without clicking Update.
- **Delete** (top right, existing events only) asks "Are you sure you want to delete this event?". After confirming, the message "The Tournament is deleted successfully" appears and you return to the events list.

## Event Details panel: basic fields

Fields marked with a red `*` are mandatory.

- **Event Name*** – free text, maximum 50 characters.
- **Event Status*** – has an **Auto / Manual** switch above it.
  - **Manual**: you choose the status from the dropdown yourself. The available statuses are set up by the organisation.
  - **Auto**: the dropdown is locked and the system manages the status. A new event in Auto mode starts as INCOMPLETE.
- **Event Type*** – **Tournament** or **League**. Default is Tournament. It cannot be changed after the event is created. Changing it on a new event reloads the extra sections for that type.
- **Start Date*** – pick from the calendar.
- **End Date*** – locked until a Start Date is chosen. It cannot be earlier than the Start Date. Changing the Start Date clears the End Date, so pick the End Date again.
- **Event Levels*** – the level of the event, from a list set up by the organisation. It cannot be changed after the event is created. The level decides whether the event needs verification before it can be published.
- **Link Event (Master)** – optional switch to link this event to a master event (see "Linking a master event"). Not shown for every organisation.
- **Season** – optional. Only active seasons are listed. Choosing a season loads the licences for that season.
- **License** – optional, multiple choice, only shown for organisations that use licences. The list is empty until a Season is chosen.
- **Event Description** – optional free text.
- The organisation may have added further custom fields at the bottom of this panel. A red `*` marks the mandatory ones.

## Event Details panel: banner, thumbnail and logo

- **Event Banner*** – recommended size **1200 x 360 px**, maximum file size **15 MB**. Three ways to set it:
  1. Click the upload area and choose an image. A larger file shows "File Exceed max limit of 15mb."
  2. Click one of the ready-made pictures under **Selected from predefined images**. Use the sport tabs (for example Table Tennis, Padel, Tennis, Badminton) to see the pictures for that sport.
  3. Click **Generate with AI** (see "Generate with AI").
  - To replace a banner, hover over it and use **Reupload**.
  - On a new event, choosing a banner also fills the Thumbnail automatically, unless you already uploaded your own thumbnail. On an existing event, changing the banner does not change the thumbnail.
- **Thumbnail*** – use PNG, JPG or JPEG (the field also lists WEBP, but the server rejects WEBP files). Must be smaller than **1 MB** and exactly **379 x 200 px**. Use **Change** to replace it. Error messages:
  - "Only PNG, JPG, JPEG, and WEBP files are allowed" – shown when the file is some other type, such as GIF or PDF. A WEBP file passes this first check but is then rejected by the server with "File upload failed", so do not use WEBP.
  - "Thumbnail size should be less than 1MB"
  - "Thumbnail dimensions must be exact 379x200px"
- **Logo*** – allowed formats PNG, JPEG, JPG. Maximum **1 MB**. Use **Change** to replace it. Error messages:
  - "Only PNG, JPEG, and JPG files are allowed"
  - "Logo size should be less than 1MB"
- "File upload failed" means the server rejected or did not receive the file. See "File uploads: what the server accepts".

## Event Details panel: Generate with AI (AI banner)

The **Generate with AI** button next to the Event Banner label opens the **Generate Banner with AI** window.

1. Type a description under **Describe your event banner**, or click one of the **Quick suggestions**.
2. Click **Generate**. A preview is drawn while the message "Painting pixels..." shows.
3. If you like the result, click **Use as Event Banner**. The image is uploaded and becomes the event banner. Click **Cancel** to close without using it.
4. To try again, change the description and click **Generate** again.

Notes:
- The generator is tuned for table tennis images.
- "Generation failed. The model may be loading. Try again in a minute." – wait a minute and click Generate again.
- "AI Image API Not Configured" – the feature is not set up for this installation; contact support.
- The banner is only stored with the event after you click **Create** or **Update**.

## Event Details panel: creating and updating the event

- New event: fill all mandatory fields and click **Create**. On success the event is saved, the page address changes to the new event id, and the next panel (Add Class/Category) opens.
- Existing event: click **Edit**, change the fields, then click **Update** in the Event Details panel.
- Mandatory for Create: Event Name, Event Status, Event Type, Start Date, End Date, Event Levels, Event Banner, Thumbnail and Logo, plus any mandatory custom field. Missing fields get a red border.
- Error messages:
  - "You can't skip mandatory fields" – a mandatory field, the banner or the thumbnail is missing.
  - "Please upload a thumbnail" – the thumbnail is missing.
  - "Invalid email format" – a custom email field is not a valid email address.
  - "You are typing an invalid key" – a number field accepts digits only.
- Each panel is saved separately with its own Create/Update button. Clicking Update in one panel does not save unsaved changes in another panel.

## Event Details panel: linking a master event

Use **Link Event** to connect this event to a master event.

1. Turn on the **Master** switch. The **Link Master Tournament** side panel opens.
2. Search for the event (type at least 2 characters) or scroll the list; more events load as you scroll.
3. Click the event you want, then click **Save**.
4. The linked event's name appears as a link under the switch. Click it to change the selection.
5. Click **Create** or **Update** in the Event Details panel to store the link.

Turning the switch off removes the link. Closing the side panel without choosing an event turns the switch back off.

## Changing event dates: schedule reset warning

If you change the dates of an event that already has venue days, planning or schedules on the dates being removed, a confirmation appears: **"Changing these dates will reset the schedule"** – "Event planning and match schedules will be cleared for the affected days."

- It lists each venue and how many days will be removed, and how many official registrations on those dates will be withdrawn.
- Click **Yes, reset** to apply the date change and clear those days, or **Cancel** to keep the current dates.
- If a date being removed already has played matches, the change is refused and the message names those dates. Dates with played matches cannot be removed.
- The same warning can appear when publishing or deleting an event.

## Add Class/Category panel: adding categories

This panel sets which categories (classes) the event offers. For a **League** the panel is called **Add Division** and categories are called divisions. The event must be created first, and the page must be in edit mode.

To add a category:
1. **Category Levels** (League: **Division**) – choose the level.
2. **Participant Type** – Singles, Teams, Doubles or Mix-Doubles. For a League only Teams is available.
3. **Class** – choose the class. The list is filled after Category Levels and Participant Type are chosen, and it has a search box ("No matching data found" when nothing matches).
4. **Abbreviation** – optional short name, maximum 50 characters.
5. **Choose Color** – optional colour for the category.
6. Click the **+** button. The category is added to the list below.
7. Click **Create** (first time) or **Update** at the bottom of the panel. **Categories are only saved when you click Create/Update** – the + button alone does not save them.

Error messages when clicking +:
- "Please select Participant Type"
- "Please select Category" – no Class chosen.
- "Please select Category Levels"
- "Category Already Added In List" – that class is already in the event.

**Primary Display Selection** (top of the panel): choose **Class** or **Abbreviation**. This decides which label is shown for categories across all screens of the event. It is saved with Create/Update.

## Add Class/Category panel: reorder, edit and delete categories

The list shows Category Level, Participant Type, Class, Abbreviation, Color and (in edit mode) Action.

- **Reorder**: in edit mode, drag a row by the dotted handle on the left to a new position, then click **Update**. The order is used wherever the event's categories are listed.
- **Delete**: click the red bin icon and confirm "Are you sure you want to delete this category?". The row disappears; click **Update** to make the deletion permanent.
- **Edit**: click the pencil icon. It is only available for categories that have already been saved. A side panel **Edit category** (League: **Edit Division**) opens with: Name*, Participant Type*, Gender Selection*, Abbreviation*, Born After, Born Before, Minimum Points, Maximum Points, Color and Category Level*. Click **Save** to store the changes. "Please fill all required fields" means a field marked `*` is empty. The side panel also has a **Delete** option.
- A category with participant type Teams makes the team leaderboard available for the event.

## Extra information sections

Below the category panel there may be extra sections defined by the organisation for the event type. They only become editable after the event is created and the page is in edit mode.

- Field types can be text, email, number, date, dropdown or image upload. Text fields allow up to 50 characters. Number fields accept digits only.
- Click **Create** (first save) or **Update** at the bottom of the section to save it. Each section is saved on its own.
- If a mandatory field is empty the message is "<field name> Is Required ." An invalid email shows "Invalid email format".
- Sections that contain an **Organiser** field have a **Publish** switch. Turn it on and click Create/Update to publish that section's information; turn it off and save to unpublish it.

## Venue Detail panel

- The panel text reads: "Select a venue created in Venue Management to view its form or create your own".
- Choose a venue from the **Select Venue** dropdown (it has a search; "No venues found" appears if nothing matches). The venue's details are shown read-only.
- Click **Update** to link the chosen venue to the event. The panel's tick turns blue once a venue is linked.
- Click **Add new venue** to create a venue without leaving the page.

## Verification: Send Verification button and status banner

Some event levels require the event to be verified (approved) before it can be published. Whether verification is needed depends on the chosen **Event Level**.

- If verification is required, a **Send Verification** button appears in the bar at the bottom of the page.
- The button is enabled only when: the page is in edit mode, the event has been created, all sections show a blue tick, and the event is not already accepted.
- Messages: "Please save the event first before sending for verification", "Please complete all sections before sending for verification", "Event sent for verification successfully".
- After sending, a status banner appears at the top of the page:
  - **Event Pending** – waiting for review.
  - **Event Accepted** – approved. **View Details** shows "Verification Successful".
  - **Event Rejected** – not approved. **View Feedback** shows "Verification Failed" with the reviewer's feedback. Fix the points raised and send for verification again.
- Events whose level does not require verification are accepted automatically when created.

## Publishing the event

- The **Publish** switch is in the bar at the bottom of the page.
- It only appears when the event has been created **and** its verification status is Accepted (automatically for levels that do not need verification, otherwise after the event is approved).
- The page must be in edit mode (click **Edit**) to use the switch.
- Turn the switch on to publish the event, off to unpublish it. The change is saved immediately; a confirmation message appears.
- If Publish is missing: check that the event is saved, that verification (if required) has been sent and accepted, and that you are looking at the bottom bar of the Details step.

## Saving the event: messages from the server and what they mean

When you click **Create** or **Update**, the server checks the event again. Its reply appears as a message at the bottom of the screen.

- **"Event Create"** / **"Event Update"** – the save worked.
- **"Event Already Exists"** – another event with the same name and the same Event Type (Tournament or League) already exists. Choose a different name. A deleted event's name can be reused. The same check runs when you rename an event.
- **"Event name must not be purely numeric"** – the name is only a number, for example `2026`, `0999`, `-3` or `3.5`. Add words, for example `Open 2026`. Names that mix letters and digits are fine.
- **"Sport default configs are required"** – no sport is configured for your organisation, so the event cannot be created. Contact support.
- **"No Event Found"** – the event no longer exists (it was deleted) or the address has a wrong event id.
- **"Unauthorized Access"** – your session expired, or you are trying to delete an event you did not create. Sign in again and retry.
- **"Access Denied"** – your role is not allowed to work on this event. Ask an administrator for access.

An existing event is only re-checked for the values you changed. An old event with a numeric name can still be edited without renaming it.

## Custom field rules checked when saving

Extra fields set up by your organisation (in the Event Details panel and in the extra sections) are checked by type when you save:

- **Text field**: "Field '<field name>' must not be purely numeric". A text field cannot hold only a number. `Hall 3` and `Main Street 42` are fine; `42` is not.
- **Number field**: "Field '<field name>' must contain a valid number". Accepted forms: `12`, `3.5`, `3,5`, `1,000`, `1.234,56`, `1 000`, with an optional `+` or `-`.
- **Letters-and-numbers field**: "Field '<field name>' must contain only letters, numbers and spaces". Punctuation and symbols such as `@` or `-` are rejected. Accented letters are accepted.
- Dropdown, email, date and file fields are not checked by these rules (email format is checked on the screen).
- Only values you changed are checked. A field left as it was never blocks a save.
- These rules are skipped when you delete the event.

## What happens automatically when an event is created

After **Create** succeeds, the system sets up the event for you:

- Default rule settings for the sport and event type are copied into the event.
- Print alert settings are copied from your organisation's defaults. Later changes to the defaults do not change this event.
- Payment settings are created for the event.
- You are given access to the event as its creator.
- No venue is added automatically. Add one in the **Venue Detail** panel.
- If the event is in **Auto** status mode it starts as INCOMPLETE.
- An event created by the main administrator account is verified automatically.

## Event Status in Auto mode: how the status is decided

In **Auto** mode the system sets Event Status itself. It recalculates when the event, its categories or its verification change, and about once an hour. Times use the venue's time zone.

Checked first, in this order:
1. Verification rejected → **REJECTED**.
2. No active category on the event → **INCOMPLETE**.
3. Verification pending → **UNVERIFIED** if the event has dates, at least one category, an organiser and a venue; otherwise **INCOMPLETE**.

Otherwise the highest of these that applies:
1. **RECENT** – today is after the End Date.
2. **ONGOING** – today is between Start Date and End Date and registration is not open.
3. **UPCOMING** – the day before the Start Date, if registration is not open and no draw exists.
4. **REGISTRATION OPEN** – registration is open for at least one category. This wins even after the Start Date.
5. **DRAWS OUT** – a draw (fixtures) exists and the event has not started.
6. **REGISTRATION CLOSED** – the last registration end time has passed and the event has not started.
7. **VERIFIED** – verification is accepted, or the event level needs none.

## Event Status: Manual mode and switching modes

- In **Manual** mode the system never changes the status. It stays as you set it, including after dates pass.
- Switching from Manual to **Auto** and saving recalculates the status immediately.
- Switching from Auto to **Manual** keeps the current status until you change it.
- If an Auto event stays INCOMPLETE, add at least one category. If it stays INCOMPLETE while waiting for verification, also link a venue.
- If an Auto event does not show REGISTRATION OPEN, check the registration start and end times on the Registration step.

## Editing or deleting after points are published

Once ranking points for the event have been published to OTT, the event is locked against changes that affect those points.

- Blocked edits: Event Name, Start Date, End Date, Event Type, Event Levels, Season, Event Status, the Publish switch and Primary Display Selection.
- Message: "This action is not permitted. Points for this event have been published to OTT. Editing events, categories, or stages is not allowed after publication. Match-level changes (edit results, add matches, delete matches) are still permitted and will require recalculation. If you need further assistance, please contact the administrator…"
- Still allowed: banner, thumbnail, logo, description, extra sections, and settings on other steps (umpire, referee, accommodation, travel).
- Deleting the event is blocked: "Deletion is not permitted. Points for this event have been published to OTT. Deleting events, categories, or stages is not allowed after publication."
- Saving without changing a locked field is not blocked.

## Deleting an event: rules

- Only the user who created the event can delete it. Anyone else gets "Unauthorized Access".
- An event whose points are published to OTT cannot be deleted.
- A deleted event disappears from the event lists and its name can be used again.
- Ranking lists that were calculated but not yet published for the event are removed.
- Deleting does not ask for the schedule-reset confirmation.

## Changing event dates: what happens to venues, schedule and officials

When Start Date or End Date changes, the venues' days are adjusted to match.

- **Tournament**: venues follow the event. Added days are added to every venue. Removed days are taken off every venue. A venue left with no days takes all the new event days.
- **League**: each venue keeps its own agreed days. Extending the event does not add days to venues. Days outside the new range are removed.
- Days are only removed after you confirm with **Yes, reset**. If you click **Cancel**, nothing from that save is stored, including other fields changed in the same save.
- After confirming, for the removed days: matches are unscheduled, Day Planner plans and breaks are deleted, club venue registrations are cancelled, and umpire and referee registrations are withdrawn.
- If the Start Date moves, the officials' day numbering is renumbered.
- **A day that already has played matches cannot be removed.** The save is refused with a message naming the dates (it may appear as `EVENT_DATES_HAVE_STARTED_MATCHES` followed by the dates). Keep those dates inside the event range.
- A save that does not change the dates never touches the venues.

## Saving categories: messages from the server and what they mean

After **Create/Update** in the Add Class/Category panel:

- **"Category Update"** – the categories were saved.
- **"Category Already Exists"** – the class is already in this event, or it appears twice in the list you are saving.
- **"Cannot Delete Category, Fixtures Already Generated"** – fixtures exist for that category. Delete its stages on the Fixtures screen first. A category with only draft stages can be deleted.
- **"No Event Found"** – create the event first.
- **"Category changes saved. N category change(s) were skipped because points for those categories are already published on OTT."** – the other changes were saved; the listed categories were left as they were.
- The points-published messages (see "Editing or deleting after points are published") appear when every change you made touches a published category.

For a category with published points: deleting it is blocked, and changing its Abbreviation, Color or Category Level is blocked. Reordering it, or saving it unchanged, is allowed.

## Deleting a category: what is removed

- **Deleting a category removes all participants entered in it.** This cannot be undone from this screen.
- The deletion only happens when you click **Update**. Until then, reload the page to get the category back.
- A new category takes its minimum and maximum points, born-after and born-before dates and gender from the class you chose.
- New categories are added at the end of the list unless you drag them.
- In Auto status mode, saving the first category moves the event out of INCOMPLETE.

## Venue Detail panel: rules when linking a venue

- The first venue linked to an event becomes its primary (default) venue.
- For a Tournament, a newly linked venue takes all the event's dates.
- **"No Venue Found"** – the venue was deleted. Choose another one.
- **"Cannot remove dates with scheduled matches"** – a date cannot be taken off a venue while matches are scheduled there. Unschedule those matches first.
- A venue is needed before an event waiting for verification can move from INCOMPLETE to UNVERIFIED in Auto mode.

## File uploads: what the server accepts

Banner, thumbnail, logo and image fields are uploaded to the server, which applies its own checks:

- Accepted file types: PNG, JPG, JPEG, HEIC, HEIF, AVIF, PDF, DOC, DOCX.
- **WEBP is not accepted by the server**, even though the thumbnail field lists it. A WEBP thumbnail fails with "File upload failed". Use PNG or JPG.
- The file's real content must match its extension. A file that was only renamed (for example a WEBP renamed to .png) is rejected.
- Maximum size on the server is 15 MB. The screen applies stricter limits for thumbnail and logo (1 MB).
- On the screen every server rejection shows as "File upload failed". Check the type, size and that the file is a genuine image, then try again.
- You must be signed in; an expired session also makes uploads fail.

## Chat assistant on the Event Details page

A round chat button sits at the bottom-right corner of the page. Click it to open the **Event assistant**, type a question and press Enter to send (Shift+Enter for a new line). The assistant can also raise a support ticket: describe the problem, add attachments if asked, review the summary and confirm.

## External events

The same form is used for **External Events** (events held outside the system, registered for ranking calculations). Differences: Event Type is fixed to Tournament, only the Event Details and Add Class/Category panels are shown, there is no verification step or Delete button, and the Publish switch is available as soon as the event is saved.

## Frequently asked questions about the Event Details page

**How do I create an event?** Open the Details step with a new event, fill Event Name, Event Status, Event Type, Start Date, End Date, Event Levels, Event Banner, Thumbnail and Logo, then click **Create**.

**Why are all the fields greyed out?** An existing event opens in view mode. Click **Edit** at the top right.

**Why can't I pick an End Date?** Choose the Start Date first. If you change the Start Date, the End Date is cleared and must be picked again.

**Why can't I change Event Type or Event Levels?** Both are locked once the event has been created.

**Why is the License list empty?** Choose a Season first; licences are loaded per season. The field only exists for organisations that use licences.

**Why does my thumbnail upload fail?** It must be PNG, JPG or JPEG, smaller than 1 MB and exactly 379 x 200 px. WEBP files are rejected by the server.

**Why does my logo upload fail?** It must be PNG, JPEG or JPG and no larger than 1 MB.

**What size should the banner be?** 1200 x 360 px, up to 15 MB.

**I added categories but they are gone after reload.** Click **Create/Update** at the bottom of the Add Class/Category panel after using the + button.

**Why is the Class dropdown empty?** Choose Category Levels and Participant Type first.

**Why is there no pencil icon on a category?** Editing is only available after the category has been saved with Create/Update.

**Why is Send Verification disabled?** Click Edit, make sure the event is created and every section has a blue tick. It is also disabled once the event is accepted.

**Why can't I see the Publish switch?** The event must be saved and its verification status must be Accepted.

**How do I delete an event?** Click **Delete** at the top right and confirm. You need Edit permission.

**What happens to the schedule if I change the event dates?** Planning and match schedules on removed days are cleared after you confirm with "Yes, reset". Days with played matches cannot be removed.

**Why do I get "Event Already Exists"?** Another event with the same name and type exists. Use a different name.

**Why is my event name rejected?** A name cannot be only a number. Add words to it.

**Why is the status stuck on INCOMPLETE?** In Auto mode the event needs at least one saved category; if it is waiting for verification it also needs a venue.

**Why can't I edit the event after publishing points?** Name, dates, type, level, season, status and publish state are locked once points are published to OTT.

**Why can't I delete the event?** Only its creator can delete it, and not after points are published to OTT.

**What happens to players if I delete a category?** All participants entered in that category are removed when you click Update.

**Why can't I delete a category?** Fixtures were already generated for it, or its points are published. Delete its stages first.
