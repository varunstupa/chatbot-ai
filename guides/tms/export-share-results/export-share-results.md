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

The screen opens with the **Download** tab. On the TMS route there is a second tab, **Sync** (see the Sync guide).

## Where to find it

Open **Export/Share Results** from the sidebar.

## Which screen you are on

- **TMS route** (`tms/format-download/:event_id`): the title is **Export/Share Results**, with the breadcrumb bar and the two tabs **Download** and **Sync**.
- **Admin route** (`download`): the title is **Download** and there is no tab. The list has no Description column, and the type column shows **Excel File**.
- On the TMS route, a missing or invalid event id shows the "no event selected" state with a button to create an event. The list is not loaded.

## Download list

- Columns on the TMS route: **Sr.No**, **File Name**, **Description**, **Initiated by**, **Type Name**, **Date/Time** (the date and the time in two lines), **Status** and **Action**.
- Columns on the admin route: the same, except **Description** is hidden, **Type Name** shows "Excel File", and **Date/Time** is one line.
- The newest files are listed first.
- **File Name** is the source of the export (for example the report it came from). Hovering the name shows the full text.
- **Initiated by** is the name of the user who made the file. A dash is shown when the name is not known.

## Status

- **Initiated** – the export has been asked for.
- **In Progress** – the file is being built.
- **Ready to Download** – the file can be downloaded.
- **Expired** – the file is marked expired on the server, so it is no longer offered.
- **failed** – the export failed. The screen shows the raw word, because no label is set for it.
- A status with no value shows a dash.

## Action

- A file that is ready has a download icon. Clicking it opens the file in a new tab.
- A file with no link shows the same icon with no link to open.

## Search and paging

- The search box filters the list by file name. The list reloads about half a second after the last key press, and goes back to the first page.
- The page sizes are 10, 20, 30, 40, 50 and 100. Changing the page size goes back to the first page.
- The paging appears only when there is at least one row.

## Empty states

- "No data found for this event" appears in the table when there are no files.
- On the TMS route with no event, the no-event state is shown instead of the list.

## Who sees which files

- On both routes the list shows the files created by the signed-in user. The account with user role id 1 sees every file of the tenant.
- Each screen asks for its own section of files: the TMS route asks for fixtures, travel and accommodation, and participants; the admin route asks for the dashboard files.

## Messages

- If the list cannot be loaded, the screen shows "Something went wrong." as a toast.

## Permissions

- The screen needs the login. The gateway checks the login on the list call. It does not check a feature permission.

## Frequently asked questions

**What is the Export/Share Results screen for?** Finding and downloading the files exported for an event, and checking when they are ready.

**Where do I download an exported file?** Click the download icon in the Action column once the status is Ready to Download.

**What do the statuses mean?** Initiated: asked for. In Progress: being built. Ready to Download: can be downloaded. Expired: no longer available.

**Why does a file show Expired or Initiated?** Expired files are marked expired on the server. Initiated files have been asked for but not built yet.

**Why is my export missing from the list?** The list shows only the files created by the signed-in user, unless the account is the tenant administrator (user role id 1).

**How do I search the download list?** Type part of the file name in the search box.

**What is the Sync tab?** It sends the event's results to the external rating platform. See the Sync guide.

**Why does the screen say No data found for this event?** The event has no exported files yet. Files appear in the list once an export has been made.
