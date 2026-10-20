---
doc_id: tms.export-share-results.sync
title: Sync tab (Rating Central) – sync history, the Sync button, the prepare and review steps, the director details and the provider not set state
routes:
  - tms/format-download/:event_id
aliases:
  - sync tab
  - rating central sync
  - rating central
  - sync to rating central
  - sync results
  - sync history
  - sync history rating central
  - rating central export
  - director id
  - organizer email sync
  - review and sync
  - sync data
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Sync tab?
  - How do I sync the event results to Rating Central?
  - What are the Director ID, Email and Password for?
  - What happens after I click Sync?
  - Why does the Sync tab say no provider?
  - What do the sync statuses mean?
  - Why does the sync say the event is not ready?
  - Can I download the file that was synced?
backend_sources:
  - gateway/src/routers/worker_router.py (rating-central settings, sync history, export prepare and submit)
  - gateway/src/routers/worker_router.py (export without action, used by the direct sync)
source_files:
  - src/app/modules/tms/rating-central-tms/rating-central-tms.component.ts
  - src/app/modules/tms/rating-central-tms/rating-central-tms.component.html
  - src/app/modules/tms/rating-central-tms/sync-auth-dialog/sync-auth-dialog.component.ts
  - src/app/modules/tms/rating-central-tms/sync-prepare-dialog/sync-prepare-dialog.component.ts
  - src/app/modules/tms/rating-central-tms/review-sync-dialog/review-sync-dialog.component.ts
  - src/app/core/constants/api-constant.ts
---
# Sync tab (Rating Central)

The **Sync** tab on the Export/Share Results screen sends the event's results to the external rating platform (Rating Central). It is shown on the TMS route only, next to the **Download** tab. The tab is built from three parts: the header, the sync history table, and the dialogs that guide the sync.

The tab only works when a rating provider is set up for the tenant. When none is set, the tab shows the no-provider state instead.

## Header

- The heading is **Sync History (Rating Central)**.
- **Last Sync** shows the date and time of the last automatic sync, if the automatic sync has run.
- The **Sync** button starts a sync for the event.
- The note says the data syncs when you press the Sync button, and that the platform contacts you by email if there is a problem.

## Sync history table

- Lists the export jobs of the event, ten rows per page.
- Columns: **S.No**, **File Name**, **Format**, **Date/Time**, **Initiated by**, **Status**, **Result** and **Action**.
- **Status** values: **Successfully Synced**, **Pending** and **Error Occurred**. Each has its own colour.
- A download icon appears in the Action column. For safety only the newest row on the first page has an active download link; the other rows show the icon disabled.
- When there are no rows, the table shows "No sync history found".

## Sync flow

The Sync button starts a three-step flow in the dialogs:

1. **Prepare**: the screen asks the server to build the export of the event. A loading message is shown while it works, then the result: "Data processed successfully" with the buttons **Review and Sync** and **Close**.
2. **Review and Sync**: the review dialog opens with the data to be sent (see below). You can correct the fields, then press **Sync data**.
3. **Submitted**: the screen shows "Report synced successfully" when the sync is accepted. Closing the dialog reloads the history.


## Review dialog

Before you press Sync data, check the event, players and matches on the review dialog, then enter the Director ID, Email and Password. All three are required before the sync can be sent.

- Three tabs: **Event**, **Player** and **Match**.
- **Event** tab: the event name and date, the club and state (greyed out), the province (drop-down of NSW, VIC, WA, SA, TAS, QLD, ACT and NT), the country (AUS), the sport id, and the unrated mean and standard deviation drop-downs (means 1600, 1500, 1300, 1200 and 1100; deviations 300 and 250).
- **Player** tab: the player report id, the player name, the unrated mean (drop-down from 2600 down to 800), the unrated standard deviation (200 or 150), and the primary club (greyed out).
- **Match** tab: the winner id, the loser id and the score of each match.
- **Cancel** closes the dialog without sending anything.
- The director section at the bottom of the Event tab holds the **Director ID**, the **Email** and the **Password**. All three are required. A missing one is marked with "This information is required." and the Event tab is opened.
- The password can be shown or hidden with its eye button.
- **Sync data** sends the event, players, matches and the director details.

## Direct-sync dialog (not opened on this screen)

- The code has a separate **Information Required!** dialog with ID, Email and Password fields (password up to 30 characters). It would send a sync without the review step.
- No control on this screen opens it, so the director details are entered in the review dialog only.
- The event-not-ready answer ("RATING_CENTRAL_EVENT_NOT_READY_FOR_EXPORT") opens an **Event in progress** dialog, and this is only reached by the direct-sync path.

## Messages

- "This information is required." – a required field is empty.
- "Something went wrong. Please try again." – the request failed with no message from the server.
- The server's own error message is shown as a toast when it has one.
- Dialog buttons: **Cancel** and **Sync data** (review), **Review and Sync** and **Close** (prepare).

## Permissions

- The tab needs the login.
- The gateway checks the login on the export route. It does not check a feature permission.

## Frequently asked questions

**What is the Sync tab?** It sends the event's results to Rating Central and shows the history.

**How do I sync the event results?** Click **Sync**, then **Review and Sync**, check the event, players and matches, enter the director ID, email and password, and click **Sync data**.

**What are the Director ID, Email and Password for?** They identify the director and the organizer who submit the results to the external platform. All three are required.

**What happens after I click Sync data?** The results are sent and a new history row appears, Pending until the platform reports back.

**Why does the Sync tab say no provider?** No rating provider is set up for the tenant, so there is nothing to sync to.

**What do the statuses mean?** Successfully Synced: accepted. Pending: still processing. Error Occurred: failed; check the event and try again.

**Why does the sync say the event is not ready?** The event is still in progress, so its results cannot be sent yet.

**Can I download the file that was synced?** Only the newest row on the first page has an active download link.
**What do I need to enter before I press Sync data?** In the review dialog, check the Event, Player and Match tabs. Then enter the Director ID, Email and Password in the director section at the bottom of the Event tab. All three are required. The Event tab also has drop-downs for the province and the unrated mean and standard deviation, which you can change before syncing.
