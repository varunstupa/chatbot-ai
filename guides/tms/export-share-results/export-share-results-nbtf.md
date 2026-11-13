---
doc_id: tms.export-share-results.nbtf-sync
title: Sync tab (NBTF) – connecting the event to NBTF, choosing categories, Review Sync and the NBTF sync history
routes:
  - tms/format-download/:event_id
aliases:
  - nbtf sync
  - nbtf results sync
  - sync to nbtf
  - nbtf uid
  - norges bordtennisforbund
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I sync the results to NBTF?
  - Why can I not select a category for the NBTF sync?
  - What does "Missing — required" mean on Review Sync?
source_files:
  - src/app/modules/admin/admin-dashboard/admin-download/admin-download.component.html
  - src/app/modules/tms/nbtf-results-sync/nbtf-results-sync.component.html
  - src/app/modules/tms/nbtf-results-sync/nbtf-results-sync.component.ts
  - src/app/modules/tms/nbtf-results-sync/nbtf-results-sync.i18n-keys.ts
  - src/app/modules/tms/nbtf-results-sync/nbtf-results-sync.constants.ts
  - src/app/modules/tms/nbtf-results-sync/category-select-dialog/category-select-dialog.component.html
  - src/app/modules/tms/nbtf-results-sync/category-select-dialog/category-select-dialog.component.ts
  - src/assets/i18n/en.json
---
# Sync tab (NBTF)

## Sync tab (NBTF) overview
- On the **Export/Share Results** screen, the **Sync** tab sends the event's results to NBTF (Norges Bordtennisforbund) instead of Rating Central, when the NBTF results sync is switched on for the organisation. Only one of the two is shown; organisations without it see the Rating Central Sync tab.
- If the NBTF screen cannot be loaded, the tab shows "Could not load the NBTF sync screen. Please refresh the page."
- For a league, the tab shows **Coming Soon**: "NBTF Sync isn't available for Leagues yet" and suggests using the **Download** tab to export a manual file.

## Sync tab (NBTF) connect the event
- An event that is not linked to NBTF yet shows "Connect this event to NBTF" with the text "Create the matching NBTF event once for this tournament to start syncing results — no file download or upload needed."
- Click **Create** (it reads "Creating…" while it runs, and cannot be clicked twice). Once created, the sync history appears.
- "A create request is already running for this event." means a create is still running.

## Sync tab (NBTF) sync history
- The heading is **Sync History (NBTF — Norges Bordtennisforbund)**, with **Last Sync:** (day/month/year hours:minutes, or "--") and the **Sync** button.
- A note says: "Important Note: Provide accurate information — data is submitted the moment you press "Sync Data" on the review screen. Contact NBTF Admin for any issues."
- Columns: **Sr.No**, **File Name** (a "{count} categories" pill opens the list when a sync covered several categories), **Format** (JSON), **Initiated by**, **Type Name** (API), **Date/Time**, **Status** and **Action**.
- Status: **Successfully Sent** (green), **Failed** (red), **In Progress** or **Dry Run** (amber), **Staged** (grey).
- The download icon in **Action** is active only when the sync is not in progress and a file exists; otherwise it is greyed out (hover shows the error, if any).
- With no rows: "No sync history yet for this event."

## Sync tab (NBTF) Select Categories to Sync
- **Sync** opens **Select Categories to Sync**: "Only Singles and Team Singles categories count toward NBTF ranking and are eligible here. Within those, only categories with every match completed can be selected."
- Each category has a pill: **Ready to Sync** (can be ticked), **Match Not Completed**, **Scores Held Back** or **Not Applicable**. Only ready categories can be ticked.
- Under the name, one line joins: the number of players (or teams, for Team Singles); then for a ready category "{count} matches complete" (or "all ties complete" for teams), otherwise the reason ("{count} matches still in progress", "{count} ties still in progress", "Scores are held back until published", "Doubles events aren't used for NBTF ranking"); and "Last synced {date}" for earlier syncs.
- "Select all ready categories ({count})" ticks every ready one. **Continue** stays greyed out until one is ticked; **Cancel** closes.
- When categories were synced before, a banner says each sync replaces the previous NBTF submission and re-includes them even if left unticked.

## Sync tab (NBTF) category rules on the server
- Singles count with all their matches. Team Singles count only the singles games inside each tie, and the category is ready only when every tie is finished. Doubles and mixed doubles are **Not Applicable**.
- A match counts as complete when it is scored or skipped, or ended by walkover. The unplayed games of a tie that already has a winner do not hold the category back.
- Any match with scores not yet published makes the category **Scores Held Back**, even if other matches are unfinished.
- Matches against a BYE are ignored. A category with no match to count (for example no draw yet) is not listed at all.
- "Last synced {date}" shows only when the last sync was sent; a staged run does not count.
- **Sync** needs at least one category; the server refuses an empty choice.

## Sync tab (NBTF) Review Sync
- After **Continue**, "Review in Progress" then "Data Processed Successfully" appear; click **Review & Sync Data**.
- **Review Sync** shows the counts of categories, players and matches (Singles and Team Singles only), the read-only **Event ID**, and **Players & their matches**: **Source ID (Stupa ID)**, **NBTF UID**, **First Name**, **Last Name**, **Birth Year**, **Sex**, **Club ID**, **Club Name**, and each match's **Class**, **Game Level**, **Winner ID**, **Loser ID**, **Set Score** and **Walkover**.
- A player without an NBTF UID shows "Missing — required" and "needs attention", and the banner "Resolve missing NBTF UIDs and unmatched players before syncing." is shown. **Sync Data** is not blocked by this; it is only greyed out while a submission is being sent.
- **Set Score** is shown from the viewed player's side (own points first); a walkover shows "—".
- **Sync Data** sends the data ("Sending to NBTF…"); the row shows **In Progress** in the history until NBTF answers. **Cancel** or **Back to Sync** leaves without sending.

## Sync tab (NBTF) error messages
- "Select at least one ready category before syncing."
- "{names} is no longer ready — refreshing categories."
- "A sync is already in progress for this event."
- "Nothing completed to send for the selected categories."
- "NBTF does not have an open ranking period right now — please retry later."
- "This event is no longer connected to NBTF — reconnect it first."
- "NBTF rejected the submission."
- "Still waiting on NBTF — check Sync History shortly for the result."
- "NBTF sync is not configured on the server yet — this is not something you can fix here. Contact support."
- "This screen only works for the NBTF-connected tenant." / "NBTF sync is not available for this tenant."
- "Something went wrong. Please try again."

## Sync tab (NBTF) server checks and history
- The NBTF calls need only the login; no feature permission is checked.
- The server allows NBTF sync only for the organisations set up for it on the server; for others every NBTF call is refused.
- History status: the result NBTF gave (sent, staged, failed or dry run) when there is one. Otherwise a queued or running job is **In Progress**, and an expired job is **Failed**.
- **Initiated by** is the user's full name, or their user number when the name cannot be found.

## Frequently asked questions: Sync tab (NBTF)
**How do I sync the results to NBTF?** Open the **Sync** tab, connect the event with **Create** if asked, click **Sync**, tick the ready categories, click **Continue**, then **Review & Sync Data**, check the data and click **Sync Data**.

**Why can I not select a category?** Only Singles and Team Singles categories with every match completed and scores published can be selected. Doubles are not used for NBTF ranking.

**What does "Missing — required" mean?** The player has no NBTF UID. A banner asks you to resolve it before syncing; the screen does not stop you from pressing **Sync Data**, so fix the UIDs first.

**Does a new sync add to the earlier one?** No. It replaces the previous NBTF submission for the event, and categories synced before are re-included automatically.
