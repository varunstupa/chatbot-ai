---
doc_id: tms.fixture
title: Fixtures and Results page
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - fixture page
  - fixtures and results
  - fixtures page
  - fixture settings
  - results page
  - stage fixtures
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What can I do on the Fixtures and Results page?
  - Why can I not see the Notify Users button?
  - What does Publish All do?
  - How do I notify users about published fixtures?
  - What does Ready for Print count?
  - How do I export the fixtures?
backend_sources:
  - gateway/src/routers/events_router.py (update_event, feature EVENT_ACCESS, Edit)
  - gateway/src/routers/worker_router.py (export/fixtures, feature FIXTURE_ACCESS, Edit)
  - tms/src/router/events_router.py (update_event)
  - tms/src/service/events_service.py (update_event: publish all / unpublish all, umpire and delegation checks)
source_files:
  - src/app/modules/tms/tms-fixture/tms-fixture.component.ts
  - src/app/modules/tms/tms-fixture/tms-fixture.component.html
  - src/app/modules/tms/tms-fixture/tms-fixture-update-event-message.util.ts
---
# Fixtures and Results page – overview

This guide describes the **Fixtures and Results** page of an event in the Stupa Event Management System (admin panel). Here the organiser creates, publishes, prints and exports the draws (fixtures) of each category and stage. The page is the most important module of the admin app: it holds the group stage, the knockout stage, scoring, scheduling and printing.

The page is split into guides:
- this guide: the page itself, its header buttons, publishing, notifying users, printing queue and export;
- stages, templates and fixture generation (coming in later guides);
- group stage and knockout stage (creation wizards, drafts, participants);
- results, standings and scoring;
- scheduling, match access and printing sheets.

## Where to find it

Open **Fixtures/Results** from the sidebar.

## Fixtures and Results page: where it is and what it is for

- Page address: `/tms/fixture/<participant id>/<category id>/<event id>/<event category id>/<stage id>`, for example `/tms/fixture/0/169/1358/4869/0`.
- The page title is **Fixture Settings**.
- Open it from the event's **Fixtures** step. Use the category and sub category tabs to choose what to work on.
- Until a category is chosen the page shows **Select options to browse through fixtures**.
- If no event is selected, the page shows the empty state **No record found** with a button **Go to Event**. Open the event first.

## Header buttons: Notify Users, Publish All, Ready for Print, Export

The header row shows these buttons when a category is loaded:
- **Notify Users** – sends notifications about published fixtures (see below).
- **Publish All** – a toggle that publishes or unpublishes every fixture of the event.
- **Ready for Print** – opens the print queue; the number on it is the matches waiting to be printed.
- **Export** – opens the export sidebar.

The buttons are hidden while the page is loading.

## Notify Users: when the button shows and what it does

- **Notify Users** appears only when two things are true: the organisation has the notify-users feature switched on, and the event has a notification set up for **fixtures published** (for the event or for the category).
- Click it: the dialog **Notify Users** asks "Do you want to proceed with sending notifications for the created and published fixtures?". Click **Yes, Send** to send, or cancel.
- While sending, the button of the dialog shows a loader and the dialog cannot be closed by clicking outside it.
- The result dialog shows success, or the error message the server returned. **Retry** sends again.
- If the number of notifications allowed by the quota is used up, the notification quota dialog opens with the sent and maximum counts instead.

The details of the notification service are documented in the notification guides.

## Publish All: publishing every fixture of the event

- The **Publish All** toggle is saved as soon as you change it. It is stored on the event as "auto publish fixtures": when it is on, fixtures are published as they are created.
- Turning it on publishes all genuine and sample fixtures of the event. Turning it off unpublishes them.
- Success messages from the server:
  - "All genuine and sample fixtures published successfully" (toggle turned on);
  - "All genuine and sample fixtures unpublished successfully" (toggle turned off);
  - "Event Update" when only the event was saved.
- The page then reloads the stages so the **Publish** toggles of each stage show the new state.
- Error messages shown in a snackbar:
  - the message returned by the server, for example "Event Already Exists", "Unauthorized Access", or the umpire and delegation checks ("Delegation Show Users Required");
  - "Something went wrong" when the server gives no message.
- When points were already published to OTT, the server blocks edits to events, categories and stages. The text of that message is not in the English translation file yet, so the screen may show an empty or raw message. Report it to the administrator.

Saving needs **Edit** permission on the feature **Event Access** (the gateway returns "Access Denied" without it).

## Status messages on the page

- "All matches in this stage are completed, please proceed to the next stage." – every match of the stage has a result; continue with the next stage.
- "Final Fixture cannot be created for this stage as all matches of the previous stage are not scored." – score the previous stage first.

## Print queue and Ready for Print

- **Ready for Print** shows the number of matches waiting to be printed.
- Click it to open the **print queue** side panel (closed with its close button).
- In the queue choose **Print All** or **Print Selected**; the printing layout is documented in the printing guide.
- For Badminton the page uses the Badminton day sheet; other sports use the standard day sheet.
- The button is hidden when print alerts are turned off for the event.

## Export: the Export sidebar

- Click **Export** to open the export side panel.
- Choose the export **Format** and, optionally, the categories, a date range and the scoring type; click export.
- The export is prepared in the background. The server confirms with its message; if the server returns an error, the message is shown, otherwise "Unknown error" or "Something went wrong" appears.
- The export format list comes from the organisation's published formats. Only a format that is published appears.

Export needs **Edit** permission on the fixture feature.

## Category and sub category tabs

- The first row lists the categories (or divisions in leagues). Click a category to show its stages. A category that has sub categories shows the number in brackets, for example "Men's Singles ( 3 )".
- Choosing a category with sub categories selects its first sub category. The second row then shows the sub categories (**Sub Division** in leagues, **Sub Category** otherwise); click one to toggle to it.
- The dropdown before the tabs filters by participant type. Choosing a type shows that type's categories and selects the first one.
- If the filter leaves no category, the page shows the empty message and clears the selection.
- Each choice updates the page address with the participant, category, event and stage ids, so a reload or a shared link opens the same selection.

## Export sidebar: the options

- **Format** (required): a published export format. "Please select a format" when missing.
- **Category** (required) with **Select Categories**: "Please select a category" when missing.
- **Date Range**: start and end dates sent as `YYYY-MM-DD`.
- **Team Case** (shown only for some categories): **Single Match** and **Doubles**; with doubles, **Choose Selection Type** appears. **Optional**: **Horizontal** or **Vertical** layout of player positions (one of them can be ticked at a time).
- **Scoring Type** (when shown):
  - **All** – "Export both scored and un-scored matches together";
  - **Only Scored** – "Export scored matches.";
  - **Only Un-scored** – "Export un-scored matches.".
- **Export** sends the choices. While it is sending, the button shows "Exporting..." and cannot be pressed again.
- **Horizontal / Vertical** – "Choose if you want to export player's position data horizontally or vertically".

## Notify Users: the result dialogs

- Success: **Notification Sent** – "Notification Sent Successfully" – with **Okay**.
- Failure: **Notification Failed** – shows the server's message, or "Notification Failed" when the server gives none – with **Retry** (sends again) and **Cancel**.
- Quota reached: the dialog **NOTIFICATION LIMIT REACHED** opens instead. Its headline is "Email quota has been exceeded" (or the SMS equivalent). It shows the blocked channel (**Email** or **SMS**), "sent / maximum sent" and the time left ("Quota resets … remaining", with "your quota automatically renews … "). Under **What you can do**: "Wait for reset", or "Please contact your admin" – the support address shown is the organisation's, with support@stupaanalytics.com as the default. **Dismiss** closes it.

## Print queue sidebar

- Opened from **Ready for Print**. Title **Print Queue**.
- Search by player, match or category ("Search by player, match or category..."). Filter by **Category** with the category menu; remove a category with its remove button.
- Columns: **Category/Round/Match**, **Players**, **Time Added**; tick matches one by one or tick the header box to select all.
- **Print All** prints every queued match (disabled when the queue is empty); **Print Selected** prints only the ticked matches (disabled when none is ticked).
- "No queued matches found." when the queue is empty; "Loading..." while it loads.

## Fixtures and Results page: what the server does

- **Publish All**: one request saves the toggle on the event. The server publishes or unpublishes all fixtures of the event, then answers with the message in the Publish All section.
- **Notify Users** and **Export** send their requests to separate services (notifications and export worker) that are documented in their own guides.
- **Ready for Print** count and queue: read-only requests; they show no message, so errors appear only as a count of 0.
- Print alert settings: when the event turns print alerts off, Ready for Print is hidden.

## What this guide does not cover yet

- The stage list, creating and deleting stages, and generating fixtures (next guide: stages and templates).
- The group and knockout wizards and their participants.
- Results, standings and scoring.
- The schedule popup, match access and the printing sheets.
- The notifications service and the export worker: their rules and messages are not in the code this knowledge base was built from, so their error messages are described from the screen only.

## Fixtures and Results page: permissions

- Changing the event's publish settings needs **Edit** on **Event Access**.
- Exporting needs **Edit** on **Fixture Access**.
- An expired sign-in gives "Unauthorized Access". Sign in again.

## Frequently asked questions about the Fixtures and Results page

**What can I do on the Fixtures and Results page?** Choose a category, create and publish its fixtures, notify users, print match sheets, and export the results. The stage-level actions are in the next guides.

**Why can I not see the Notify Users button?** The notify-users feature is not switched on for your organisation, or the event has no notification set up for published fixtures.

**What does Publish All do?** It publishes every genuine and sample fixture of the event when switched on, and unpublishes them when switched off.

**Why does Publish All say "Something went wrong"?** The server sent no message. Reload and try again; if it repeats, check the event's umpire and delegation settings.

**What does Ready for Print count?** The matches waiting in the print queue.

**Why is Ready for Print not visible?** Print alerts are turned off for this event.

**How do I export the fixtures?** Click **Export**, choose the format and the categories or dates, then click export. Download it when it is ready.

**What is "All matches in this stage are completed"?** Every match of this stage has a result. Move on to the next stage.

**How do I notify users about published fixtures?** Click **Notify Users** and confirm with **Yes, Send**. The button appears only when your organisation has the notify-users feature on and the event has a notification set up for published fixtures.
