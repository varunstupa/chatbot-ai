---
doc_id: tms.export-share-results.sync
title: Sync tab (Rating Central) – sync history, Sync to Rating Central steps (missing IDs, check IDs, select matches, review), the director details and the provider not set state
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
  - What happens after I click Sync Data?
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
  - src/app/modules/tms/rating-central-tms/rc-sync-flow/rc-sync-flow.component.html
  - src/app/modules/tms/rating-central-tms/rc-sync-flow/services/rc-sync-flow.service.ts
  - src/app/modules/tms/rating-central-tms/rc-sync-flow/components
  - src/app/modules/tms/rating-central-tms/rc-sync-flow/utils/rc-review-form.util.ts
  - src/app/core/constants/rating-central-sync.constants.ts
  - src/app/core/constants/api-constant.ts
  - src/app/modules/admin/rating-external-points/no-provider/no-provider.component.html
  - src/app/modules/admin/admin-dashboard/admin-download/admin-download.component.html
---
# Sync tab (Rating Central)

The **Sync** tab on the Export/Share Results screen sends the event's results to the external rating platform (Rating Central). It is shown on the TMS route only, next to the **Download** tab. The tab is built from three parts: the header, the sync history table, and the dialogs that guide the sync.

The tab only works when a rating provider is set up for the tenant. When none is set, the tab shows "No Provider Connected Yet" with "You don't have any providers connected to your account yet. Please email support@stupaanalytics.com".

When the NBTF results sync is switched on for the organisation, the Sync tab shows the NBTF sync instead of Rating Central (see the NBTF sync guide).

## Sync tab (Rating Central) header
- The heading is **Sync History (Rating Central)**.
- **Last Sync** shows the date and time of the last automatic sync, if the automatic sync has run.
- The **Sync to Rating Central** button opens the sync steps for the event, in place of the history.
- The note reads: "Important Note: Provide accurate information, as data syncs when you press the "Sync" button. If any issues occur, the external platform will contact you via email."

## Sync tab (Rating Central) sync history table
- Lists the Rating Central export jobs of this event only, ten rows per page by default (page sizes 10, 20 or 30).
- Columns: **S.No**, **File Name** (always shown as "Result"), **Format** (CSV when none is given), **Initiated by**, **Date/Time** (day/month/year hours:minutes), **Status** and **Action**.
- **Status** values: **Successfully Synced** (the job finished) and **Error Occurred** (the job failed), each with its own colour.
- While a job is queued or running, and after it expired, the Status cell is empty: the server sends a status the screen has no label for, so **Pending** never appears.
- A download icon appears in the Action column. For safety only the newest row on the first page has an active download link; the other rows show the icon disabled.
- When there are no rows, the table shows "No sync history found".

## Sync to Rating Central steps
- The steps are **Add Missing IDs**, **Check IDs**, **Select Matches** and **Review & Sync**, shown as tabs. You can click back to a step already reached, but not ahead.
- While data loads, "Processing Data…" ("Please wait while we process the records.") is shown; cancelling the first load returns to the history.
- If every player already has a Rating Central ID, the first two steps are skipped and the flow opens on **Select Matches**.
- Each step ends with a confirmation: "Data Fetched Successfully" (players or matches) with **Review**, and "Data Processed Successfully" with **Review & Sync Data** before the last step.
- **Cancel** on any step leaves the flow without sending anything. A failed call shows the server's message, or "Something went wrong. Please try again."
- The server checks the event too: a request for an event other than the one open in the app is refused with "Access Denied".

## Sync to Rating Central: Add Missing IDs
- Lists "Players missing a Rating Central ID" ("{total} players · {temporary} with a temporary ID") with **Sr. No.**, **TTA ID**, **Player**, **Gender**, **Date of Birth**, **Email**, **Rating Central ID** and **Status** (**Added** or **Temporary ID**).
- Players left without an ID are sent with a temporary ID. Type the ID with the pencil, or use **Edit All IDs** / **Done Editing**.
- An ID must be a number between 5000 and 9999999 ("Enter a number between 5000 and 9999999") and not used by another player ("This ID is already used for another player").
- **Download Rating Central player list** opens the latest list to look IDs up. If the browser blocks it: "The player list is ready. Click the button again to open it."
- **Reset IDs** clears the IDs typed but not saved. **Save** (greyed out while an ID is wrong) saves and goes to **Check IDs**. **Skip** goes on without saving and is greyed out while there are unsaved changes.
- The server also refuses an ID outside 5000 to 9999999, or the same player sent twice.

## Sync to Rating Central: Check IDs and Select Matches
- **Check IDs** is read only: "Read only. {added} added · {temporary} temporary. Go back to change an ID." **Reset IDs** (greyed out when none were added) puts every added ID back to its temporary ID and saves at once. **Fetch Matches** loads the completed matches.
- **Select Matches** lists the completed matches in a **Match view** or **Player view**, with **Group by Category**, a search ("Search by player name…"), a **Category** filter and status tabs **All**, **Unsynced**, **Modified** and **Synced**.
- Unsynced: never sent. Modified: sent, but the result changed since (for example a score edited or a walkover applied). Synced: sent with no change.
- Unsynced and Modified matches are ticked when the step opens. "Walkovers and matches without a winner are not sent to Rating Central" and cannot be ticked.
- "{selected} of {total} matches selected", **Select All {count}** and **Clear selection** help to choose. Synced matches you tick are sent again. **Continue** is greyed out until one match is ticked.

## Sync to Rating Central: Review & Sync
- Three tabs: **Event data**, **Player data** and **Match data**.
- **Event data**, **Rating Central sign-in**: **Director ID** (numbers only, "Enter a numeric ID"), **Email** ("Enter a valid email") and **Password** (with show or hide). All are required ("Required").
- **Event details** ("Sent with every match in this report."): **Event Name**, **Club ID**, **State**, **Country** and **Sport ID** are read only ("From the event setup"). **Event Date** and **Province** (NSW, VIC, WA, SA, TAS, QLD, ACT or NT) are required. **Unrated Mean** (1600, 1500, 1300, 1200 or 1100) and **Unrated Standard Deviation** (300 or 250) can be chosen.
- **Player data**: Rating Central ID, Player, **Unrated Mean** (2600 down to 800), **Unrated St. Dev.** (200 or 150) and **Primary Club ID**, which can all be edited.
- **Match data**: **Match ID**, **Player 1 · Rating Central ID**, **Player 2 · Rating Central ID** and **Score**.
- **Sync Data** with a missing or wrong field marks it and opens the **Event data** tab. On success: "Report Synced Successfully" ("... Results are ready to download from the Sync History table."); **Done** returns to the history and reloads it.

## Direct-sync dialog (not opened on this screen)
- The code has a separate **Information Required!** dialog with ID, Email and Password fields (password up to 30 characters). It would send a sync without the review step.
- No control on this screen opens it, so the director details are entered in the review dialog only.
- The event-not-ready answer ("RATING_CENTRAL_EVENT_NOT_READY_FOR_EXPORT") opens an **Event in progress** dialog, and this is only reached by the direct-sync path.

## Messages
- "Required", "Enter a numeric ID" and "Enter a valid email" – sign-in and event fields on Review & Sync.
- "Enter a number between 5000 and 9999999" and "This ID is already used for another player" – Add Missing IDs.
- "Something went wrong. Please try again." – the request failed with no message from the server.
- The server's own error message is shown as a toast when it has one.

## Permissions
- The tab needs the login. The header and the history need nothing more.
- Loading the players, the matches and the Rating Central player list needs the **Rating** permission (Read). Saving IDs, preparing and sending the report need **Rating** (Edit). Administrators always have it. Without it the server answers "Access Denied", shown as a toast.

## Frequently asked questions: Sync tab (Rating Central)
**What is the Sync tab?** It sends the event's results to Rating Central and shows the history.

**How do I sync the event results?** Click **Sync to Rating Central**. Add any missing Rating Central IDs (or skip), check the IDs, fetch and tick the matches, click **Continue**, then **Review & Sync Data**. Enter the Director ID, Email and Password on **Event data** and click **Sync Data**.

**What are the Director ID, Email and Password for?** They identify the director and the organizer who submit the results to the external platform. All three are required.

**What happens after I click Sync Data?** "Report Synced Successfully" appears. Click **Done** to go back to the history. The new row's Status stays empty while the job is queued or running, then shows Successfully Synced or Error Occurred.

**Why does the Sync tab say no provider?** No rating provider is set up for the tenant, so there is nothing to sync to.

**What do the statuses mean?** Successfully Synced: the job finished. Error Occurred: it failed; check the event and try again. An empty Status means the job is still queued or running (or expired).

**Why does the sync say the event is not ready?** The event is still in progress, so its results cannot be sent yet.

**Can I download the file that was synced?** Only the newest row on the first page has an active download link, and only when it has a file.

## Frequently asked questions: Sync tab (Rating Central) (part 2)
**What do I need to enter before I press Sync Data?** On **Event data**, the Director ID, Email and Password, plus Event Date and Province. All are required.

**Why can I not tick a match?** Walkovers and matches without a winner are not sent to Rating Central.

**What is a temporary ID?** A player without a Rating Central ID is sent with a temporary ID. Add the real ID (5000 to 9999999) on **Add Missing IDs** to avoid it.

**Why is a synced match shown as Modified?** Its result changed after it was sent. Modified matches are ticked so they are sent again.
