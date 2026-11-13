---
doc_id: tms.export-share-results.api
title: Backend logic of the Export/Share Results APIs – the download list, the download records, the Rating Central sync routes and the gateway rules
routes:
  - tms/format-download/:event_id
aliases:
  - export share results api
  - download api
  - downloads api
  - get downloads
  - create download
  - download records
  - download status values
  - rating central api
  - sync history api
  - export payload
  - download permissions
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - Which API loads the download list?
  - Which users see which download records?
  - Which statuses can a download record have and who sets them?
  - Which API starts a Rating Central sync?
  - What does the sync prepare step return?
  - Does the download search look at the file path?
  - Which permission do these routes check?
backend_sources:
  - gateway/src/routers/download_router.py (get_downloads, create_download)
  - gateway/src/routers/user_management_import_export_router.py (creates download records, sets failed and expired)
  - gateway/src/routers/worker_router.py (rating-central settings, sync-history, export prepare and submit)
  - gateway/src/common/download_status.py (status values)
  - tms repository, branch staging: src/router/download_router.py
  - tms repository, branch staging: src/service/download_service.py
  - tms repository, branch staging: src/crud/download_crud.py
  - tms repository, branch staging: src/common/enums.py (DownloadStatus)
  - tms repository, branch staging: src/workers/tasks/dashboard_download_tasks.py
source_files:
  - src/app/modules/admin/admin-dashboard/admin-download/admin-download.component.ts
  - src/app/modules/tms/rating-central-tms/rating-central-tms.component.ts
  - src/app/core/services/dashboard-service/dashboard.service.ts
  - src/app/core/services/external-point/external-point.service.ts
  - src/app/core/constants/api-constant.ts
  - src/app/core/services/rating-central-sync/rc-sync-api.service.ts
  - src/app/modules/tms/rating-central-tms/rc-sync-flow/services/rc-sync-flow.service.ts
---
# Backend logic of the Export/Share Results APIs

The screen uses two groups of routes. The **download list** is served by the gateway download router, which forwards to the TMS download service. The **Sync tab** is served by the gateway worker router, which forwards to the worker service. The gateway checks are described here; the worker service is not in these repositories, so its own rules are not.

## Calls the screen makes

| Screen action | Method and path | Gateway rule |
|---|---|---|
| Download list, paging and search | GET `download/v1/get_downloads` | Login checked in the gateway. No feature permission. |
| Sync settings (header and Last Sync) | GET `worker/rating-central/settings` | Login. |
| Sync history table | GET `worker/rating-central/sync-history` | Login. |
| Sync: players missing a Rating Central ID | GET `worker/rating-central/export/new-players` | Login and Rating (Read). |
| Sync: save or reset player IDs | PUT `worker/rating-central/export/new-players` | Login, event check and Rating (Edit). |
| Sync: completed matches to choose from | GET `worker/rating-central/export/matches` | Login and Rating (Read). |
| Sync: Rating Central player list download | GET `worker/rating-central/players-record` | Login and Rating (Read). |
| Sync: prepare (selected matches) | POST `worker/rating-central/export?action=prepare` | Login, event check and Rating (Edit). |
| Sync: submit after review | POST `worker/rating-central/export?action=submit` | Login, event check and Rating (Edit). |

The event check refuses a request whose event is not the event open in the app (403 "Access Denied"). Administrators pass the Rating permission check.

The direct-sync path (POST `worker/rating-central/export` with no action) exists in the code but is not reached from this screen.

## Download list (GET download/v1/get_downloads)

- The gateway checks the login first. Without a valid login it returns 401 with the unauthorised message.
- It forwards the paging, the search text, the creator filter and the section filter to the TMS service. The gateway does not forward a status filter, although the TMS service accepts one.
- The TMS service never returns deleted records. Its other filters are: the download id, the source name (contains), the status (contains), the creator and the sections (one of a list).
- **Creator rule (gateway)**: the gateway replaces the creator with the caller's own user role id unless the caller has the Admin role, or is a tournament director (role name contains "director") and an event id is sent. Only then is the creator sent by the screen used (none means all records). So other users see only their own records, whatever the screen sends.
- The TMS applies the creator filter only when a creator is given; no user is treated specially there.

## Download list filters sent by the screen

- The screen also sends the event id on the TMS route. The gateway forwards it and the TMS keeps only records saved with that event id, so records without an event (for example dashboard reports) are not listed there.
- **Search** matches the source name only. The gateway description says the URL path is searched too, but the TMS query does not do that.
- Records are ordered newest first (highest id first). The total is counted before paging. Paging applies only when both the page number and the page size are given.
- The gateway then adds **created_by_name** to each record, by looking up the creators' names. If that lookup fails, the list is still returned without names.
- The reply is "Downloads retrieved successfully" with the records, the total, the page and the page size.

## Download records

- A record has a source name, a section, a status, a type name, a format description, a start date, a downloaded path (the file link), the creator and the deleted flag.
- **Create** (POST `download/v1/create_download`): the gateway checks the login, sets the creator to the caller (an administrator may name another creator) and forwards the record. The reply is 201 "Download Created Successfully" with the record, or 400 "Download Creation Failed".
- **Read one**, **update** and **delete**: a user who is not an administrator may only touch their own records, except a tournament director for records that belong to an event. Otherwise 403 "Forbidden". A missing record gives 404 "Download Not Found".
- Delete only sets the deleted flag, so the record disappears from the list ("Download Deleted Successfully").

## Status values

| Value | Shown on the screen as | Set by |
|---|---|---|
| Initiated | Initiated | Not traced in these repositories; the value exists in the TMS and gateway enums. |
| in_progress | In Progress | Not traced in these repositories; the value exists in the TMS and gateway enums. |
| ready to download | Ready to Download | The dashboard report task, when the file is saved. |
| failed | failed (no label) | The user import and export flow, when the export or the record fails. |
| expired | Expired | The user import and export flow, when the file has expired on the external side. A download that already has a file is not marked expired. |

- The dashboard report task creates a record already in the ready state, with the report type, the file link and the section "dashboard".
- The user import and export flow creates the record through the gateway, then starts the export task. It marks the record failed when the start fails.

## Sections

- The download list asks for these sections on the TMS route: fixtures, accommodation and travel (both spellings are sent), and participants.
- The admin route asks for the dashboard section.
- No code in the local gateway or TMS repositories writes records with the fixture, travel or participant sections. Those records are probably written elsewhere, which this guide has not checked.

## Rating Central sync routes

- **Settings** (GET) return the sync automation settings, including the last run. The screen shows the no-provider state when the response has no data.
- **Sync history** (GET) takes the page number (from 1), the page size (1 to 100, default 10), the task type (the screen sends export) and the event id. The gateway picks the task name from the task type.
- **Prepare** (POST with action prepare) is sent with the event and the IDs of the matches ticked on Select Matches. It returns the export payload for the review step: the event, the players, the match results and counts.

## Rating Central sync step routes

- **New players** (GET) lists the players of the event without a Rating Central ID. **PUT** saves the IDs typed, or an empty ID to put a player back on the temporary ID. The gateway checks the body first: at least one player, no player twice, and each ID between 5000 and 9999999; otherwise the request is refused with a validation message.
- **Matches** (GET) returns the completed Singles and singles-in-team matches with their sync status (unsynced, modified, synced). **Players record** (GET) returns the download link of the latest Rating Central player list.
- **Prepare** and **submit** refuse an empty list of match IDs. **Submit** needs the export payload with a submission block (director id, director password and organizer email). Missing parts give 400 with the field and the reason, or "export_payload is required when action=submit". The reply is the queued job, which can be polled until it finishes.
- The rules inside the worker service (what it does with the IDs and the matches) are not in these repositories.
- The direct path (POST without an action) sends the director fields at the top level. Its dialog is not opened on this screen.

## Rating Central sync history statuses

- The gateway turns the job status into: completed "Successfully Synced", failed "Error Occurred", running "In Progress", queued "Queued", expired "Expired". The value is sent as a message key.
- The screen only labels Successfully Synced, Pending and Error Occurred. The gateway never sends Pending, so a queued, running or expired job shows an empty Status cell.
- Only export jobs of the event are listed (the screen sends the task type export and the event id). The file link is the job's report or CSV link.

## Permissions and errors

- All routes need the login. The download list, the Sync settings and the sync history check no feature permission. The Rating Central sync step routes check the Rating feature (Read to load, Edit to save or send); without it the reply is 403 "Access Denied".
- Unauthorised requests return 401.
- A failed list call shows "Something went wrong." as a toast.
- A failed sync call shows the server's message as a toast, or the validation messages when the server returns them.
- When the NBTF results sync is switched on for the organisation, the Sync tab uses the NBTF flow instead of these Rating Central routes (see the NBTF sync guide).

## Things to know

- The gateway description of the search mentions the URL path, but the search only matches the source name.
- The status filter is supported by the TMS service but not forwarded by the gateway, so the screen cannot filter by status.
- The Sync tab's "Sync" label is written as plain text, so it is not translated.

## Frequently asked questions

**Which API loads the download list?** GET download/v1/get_downloads through the gateway.

**Which users see which records?** Users with the Admin role see all records (or one user's, with the filter). A tournament director sees all records of the event on the TMS route. Everyone else sees only their own records; the gateway enforces this.

**What do the statuses mean and who sets them?** See the status table: the dashboard task sets Ready to Download, the user import and export flow sets failed and expired, and the export sets Initiated and in_progress.

**Which API starts a Rating Central sync?** The submit call after the review step: POST worker/rating-central/export with action submit, with the ticked match IDs.

**What does the prepare step return?** The export payload: the event, the players, the match results and the counts.

**Does the download search look at the file path?** No, only the source name.

**Which permission do these routes check?** The download list and the sync history need only the login. The Rating Central sync steps need the Rating permission (Read to load, Edit to save IDs or send).
