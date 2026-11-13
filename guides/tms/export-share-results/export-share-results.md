---
doc_id: tms.export-share-results
title: Export/Share Results screen – the download list of exported files, status and links, search and paging, and the Download and Sync tabs
routes:
  - tms/format-download/:event_id
  - admin/download
aliases:
  - export share results
  - export/share results
  - format download
  - downloads
  - download history
  - export history
  - exported files
  - download list
  - download status
  - ready to download
  - share results
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Export/Share Results screen for?
  - Where do I download an exported file?
  - What do the download statuses mean?
  - Why does a file show Expired or Initiated?
  - Why is my export missing from the list?
  - How do I search the download list?
  - What is the Sync tab?
  - Why does the screen say No data found for this event?
backend_sources:
  - gateway/src/routers/download_router.py (download/v1/get_downloads, create_download)
  - tms repository, branch staging: src/router/download_router.py
  - tms repository, branch staging: src/service/download_service.py
  - tms repository, branch staging: src/crud/download_crud.py
  - tms repository, branch staging: src/workers/tasks/dashboard_download_tasks.py
source_files:
  - src/app/modules/admin/admin-dashboard/admin-download/admin-download.component.ts
  - src/app/modules/admin/admin-dashboard/admin-download/admin-download.component.html
  - src/app/modules/tms/tms.module.ts
  - src/app/modules/admin/admin.module.ts
---
# Export/Share Results screen

The **Export/Share Results** screen (route `tms/format-download/:event_id`, with the same component on the admin route `download`) lists the files that were exported or generated for the event, with their status and a link to download each one. The list is kept by the TMS service, so a file made by a user in one screen can be downloaded here.

The screen opens with the **Download** tab. On the TMS route there is a second tab, **Sync** (see the Sync guide). The Sync tab shows Rating Central, or NBTF when the NBTF results sync is switched on for the organisation.

## Where to find it
Open **Export/Share Results** from the sidebar.

## Which screen you are on
- **TMS route** (`tms/format-download/:event_id`): the title is **Export/Share Results**, with the breadcrumb bar and the two tabs **Download** and **Sync**.
- **Admin route** (`download`): the title is **Download** and there is no tab. The list has no Description column, and the type column shows **Excel File**.
- On the TMS route, a missing or invalid event id (the last number of the address is 0) shows "No record found" and "Create Event to begin with Export/Share Results." with a **Go to Event** button. The list is not loaded and the tabs are hidden.

## Download list
- Columns on the TMS route: **Sr.No**, **File Name**, **Description**, **Initiated by**, **Type Name**, **Date/Time** (the date and the time in two lines), **Status** and **Action**.
- Columns on the admin route: the same, except **Description** is hidden, **Type Name** shows "Excel File", and **Date/Time** is one line.
- The newest files are listed first.
- **File Name** is the source of the export (for example the report it came from). Hovering the name shows the full text.
- **Initiated by** is the name of the user who made the file ("--" when the name is not known). The column is shown only to administrators and tournament directors on the TMS route, and only to administrators on the admin route.

## Download screen Initiated by filter (admin route)
- On the admin route, an administrator sees an **Initiated by:** drop-down above the list. It starts on **All Users**; pick a user (the list has a search) to see only that user's files.
- Changing the user reloads the list from the first page.
- If the user list cannot be loaded: "Something went wrong".

## Status
- **Initiated** – the export has been asked for.
- **In Progress** – the file is being built.
- **Ready to Download** – the file can be downloaded.
- **Expired** – the file is marked expired on the server, so it is no longer offered.
- **failed** – the export failed. The screen shows the raw word, because no label is set for it. Any other unknown value is also shown as it is.
- A status with no value shows "--".
- **Ready to Download**, **Initiated**, **In Progress** and **Expired** each have their own colour.

## Action
- A row that has a file link has a download icon. Clicking it opens the file in a new tab.
- Who can download: an administrator can download every file; on the TMS route a tournament director can too. Other users can download only the files they made.
- A row with no file link, or a file you may not download, shows the icon faded with nothing to open.

## Search and paging
- The search box filters the list by file name. The list reloads about half a second after the last key press, and goes back to the first page.
- The page sizes are 10, 20, 30, 40, 50 and 100. Changing the page size goes back to the first page.
- The paging appears only when there is at least one row.

## Empty states
- TMS route, administrator or tournament director: "No data found for this event" when there are no files.
- TMS route, other users: "No exports initiated yet" with "Exports you request for Fixtures, Players, Schedule, or Awards within this event will appear here for download."
- Admin route: "No data found".
- On the TMS route with no event, the no-event state is shown instead of the list.

## Who sees which files
- TMS route: administrators and tournament directors see all the downloads; other users see only the files they made.
- Admin route: administrators see all files, or one user's files with the **Initiated by** filter; other users see only their own files.
- Administrator here means the main administrator account or a user whose role is Admin; tournament director means a role whose name contains "director".
- Each screen asks for its own section of files: the TMS route asks for fixtures, travel and accommodation, and participants; the admin route asks for the dashboard files.
- The TMS route lists only files recorded for the open event. Files saved without an event (such as dashboard reports) never appear there.

## Download list: what the server enforces
- The server limits the list to the user's own files unless the user has the Admin role, or is a tournament director on the TMS route (where the event is sent). This holds even if the screen asks for more.
- On the admin route a tournament director therefore sees only their own files.
- A file record made by a user is always saved under that user's name, unless an administrator makes it.

## Messages
- If the list cannot be loaded, the screen shows "Something went wrong." as a toast.

## Permissions
- The screen needs the login. The gateway checks the login on the list call ("Unauthorized Access" without it). It does not check a feature permission; the role rules above decide which files are listed.

## Frequently asked questions: Export/Share Results
**What is the Export/Share Results screen for?** Finding and downloading the files exported for an event, and checking when they are ready.

**Where do I download an exported file?** Click the download icon in the Action column once the status is Ready to Download.

**What do the statuses mean?** Initiated: asked for. In Progress: being built. Ready to Download: can be downloaded. Expired: no longer available.

**Why does a file show Expired or Initiated?** Expired files are marked expired on the server. Initiated files have been asked for but not built yet.

**Why is my export missing from the list?** Users who are not administrators (or, on the TMS route, tournament directors) see only the files they made. On the admin route, check that the **Initiated by** filter is on **All Users** or on your name.

**Why is the download icon faded?** The file has no link yet, or it was made by another user and you are not an administrator or tournament director.

**How do I search the download list?** Type part of the file name in the search box.

**What is the Sync tab?** It sends the event's results to the external rating platform (Rating Central, or NBTF where the NBTF sync is switched on). See the Sync guides.

## Frequently asked questions: Export/Share Results (part 2)
**Why does the screen say "No record found" with a Go to Event button?** No event is selected in the address. Open the event first, or click **Go to Event**.

**Why does the screen say No data found for this event?** The event has no exported files yet. Files appear in the list once an export has been made. Users who are not administrators see "No exports initiated yet" instead.
