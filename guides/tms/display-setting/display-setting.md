---
doc_id: tms.display-setting
title: Display Setting screen – live matches, all matches, tables, view links, hide or unhide, exports and the LED settings
routes:
  - tms/display-setting/:event_id/:participant_id/:category_id
aliases:
  - display setting
  - display settings
  - display setting screen
  - display configuration
  - led settings
  - led output
  - led display
  - score card layout
  - live matches display
  - hide unhide match
  - show on table
  - view links
  - rtmp url
  - broadcast link
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Display Setting screen for?
  - How do I hide a match from the table display?
  - How do I copy the Rtmp URL?
  - What are the LED layouts and how do I save one?
  - What does LED Output open?
  - How do I export the match list to Excel?
  - Why does the Hide/Unhide toggle not change?
  - Where do I get the team link and the match link?
  - What is the Tables tab?
  - What does the All matches tab show?
backend_sources:
  - gateway/src/routers/match_router.py (match status, LED settings)
  - gateway/src/routers/ott_router.py (LED settings read)
  - tms repository, branch staging: src/router/match_router.py (LED settings routes)
  - tms repository, branch staging: src/service/match_service.py (update_led_settings, get_led_settings)
source_files:
  - src/app/modules/tms/display-setting/display-setting.component.html
  - src/app/modules/tms/display-setting/display-setting.component.ts
  - src/app/modules/tms/venue-led/venue-led-link-button/venue-led-link-button.component.ts
  - src/app/core/services/common-service/common-service.service.ts
  - src/app/core/services/day-planner/day-planner.service.ts
---
# Display Setting screen

The **Display Setting** screen (route `tms/display-setting/:event_id/:participant_id/:category_id`) is the admin page for the table and LED displays. It lists the event's matches in three tabs, lets you show or hide a match on the table display, copies the links for each match, exports the lists, opens the live LED card, and saves the LED layout.

The screen needs a valid event id. The event id is the **last segment** of the address, so `/tms/display-setting/0/0/1358` shows event 1358. With no valid event the page shows the "no event selected" state and makes no event calls.

The screen opens on **Live Matches**. The tabs are **Live Matches**, **All matches** and **Tables**.

## Where to find it

Open **Display Settings** from the sidebar.

## Header and toolbars

- Title: **Display Configuration**, with the breadcrumb bar.
- The Live Matches and All matches toolbars have a search box and the buttons **LED Output**, the venue LED link (when that feature is on), **Export** and **LED Settings**.
- The Tables toolbar has **LED Output**, the venue LED link, **Export** and **LED Settings**, but no search box.

## Filters and date strip

- **Venue**, **Month** and **Year** are drop-downs above the lists. The venues come from the event's venues, and the first venue is selected by default.
- Changing the venue reloads the event days of that venue. Changing the month or year reloads the days of that month.
- The **date strip** shows the event days. Click a day to load the matches of that day. The arrow buttons scroll the strip and appear only when it overflows.
- With no date selected nothing is loaded.

## Live Matches tab

- Shows matches that are in progress for the event, with their sub matches for team events.
- Columns: **Match ID** (with a red live dot), **Date/Time** (time, then date), **Table No.** (table numbers joined by commas), **Category**, **Round**, **Team** (team names, only for team matches), **Match** (the players or sides, joined by **VS**), **Member Association** or **Club** (only when the event's parent role is one of them), **Broadcast link** and **Hide/Unhide**.
- The search box filters the rows by match id, category, round, table, team name, player name or club.
- Paging offers 10, 20, 30, 40, 50 or 100 rows per page.
- An empty list shows the sport's no-data image and text.

## All matches tab

- Lists all matches of the chosen day and venue, not only the live ones.
- Columns: **Match ID**, **Date/Time**, **Table No.**, **Category**, **Round**, **Team**, **Match**, **Member Association** or **Club** (as above) and **Rtmp URL**.
- There is no Broadcast link and no Hide/Unhide toggle on this tab.
- In the **Rtmp URL** column, a match with one streaming link copies the URL when clicked. A match with several streaming links shows **View Links**, which opens the list of streaming links.

## Tables tab

- Lists the venue tables for the chosen day, one row per table: **Sr.No**, **Table No.** (the word "Table" and the number) and **Broadcast link**.
- Clicking the broadcast link opens the table view in a new tab (the umpire view for sport id 2).
- **Export** on this tab downloads the table list (see Exports).
- The list is paged with the same page sizes.

## View Links (Live Matches)

- When a match has **more than one live sub match**, its Broadcast link cell reads **View Links**. Clicking it opens an overlay with two rows: **Team Link** (the team view of the match) and **Match Link** (the current sub match). Clicking a row opens it in a new tab.
- With one live sub match, or a single match, the cell reads **Link.match..** and opens the match view in a new tab.
- The full address is shown in each row. The copy icons are not shown on this screen; copy the address from the row.
- For sport id 2 (Padel) the links use the umpire view; for other sports they use the match view.

## Rtmp URL and streaming links

- A single streaming link is copied when its URL is clicked. The snackbar says "URL copied to clipboard", or "Failed to copy URL" when the copy fails.
- Several streaming links open a small list. Each entry shows its label (or "Table" and the venue table number when there is no label) and its Rtmp URL. Clicking the URL or the copy button copies that link.

## Hide/Unhide (show on table)

- The **Hide/Unhide** toggle on a Live Matches row decides whether the match is shown on the table display.
- The new state is sent to the server at once. There is no confirmation and no success message.
- If the save fails the screen shows no message and does not reload the list, so the toggle can show a state the server did not keep. Reload the screen to see the saved state.

## Exports

- **Export** on Live Matches and All matches downloads the full match list as "matches.xlsx".
- The live export on Live Matches downloads only the matches in progress.
- **Export** on the Tables tab downloads the table list.
- A loader shows while the file is prepared. If the download fails, the loader stops and no message is shown.

## LED Settings sidebar

- **LED Settings** opens the sidebar titled **Settings**, with the heading **Select what to display**.
- Two cards sit at the top: **Live scores** (selectable) and **Live streaming** (greyed out and disabled).
- **Layouts** – "Pick a score card layout based on your pixels". Five layouts are shown as grids: 3 by 3, 1 by 3, 2 by 3, 2 by 2 and 3 by 4. Click a layout to select it.
- **Card details** – "Select what to display". The options **Parent logo**, **Serve icon**, **T-shirt color**, **Back No.**, **Player Name**, **Specify the live game**, **Overall results** and **Previous results** are shown as togglees. All of them are disabled on this screen.
- **Generate Preview** opens the **LED Preview** dialog. It shows a picture for layouts 1, 2 and 3; layouts 4 and 5 show no picture.
- **Save** stores the selected layout for the event (see the API guide). On success the server message shows in a snackbar; on failure the server message shows in the error style. The saved settings are then read again.

## LED Output

- **LED Output** opens the live LED card of the event in a new tab: `/tms/display-live-card/:event_id`, or `/tms/stupa-live-card/:event_id` when the sport id is 2 (Padel).
- The live card draws the layout saved here (see the LED live card guide).

## Venue LED link

- The venue LED link button appears on the toolbars only when the venue LED feature is switched on.
- It opens a small panel with the public URL of the venue LED board for the event, and a copy button. The board is a separate feature.

## Messages

- Snackbars: "URL copied to clipboard" and "Failed to copy URL"; the server message after **Save**, or its error message when the save fails.
- An empty list shows "No data found" or the sport's no-data text.
- Hide/Unhide and Export show no message.

## Permissions

- Reading the screen needs the login.
- Changing the Hide/Unhide toggle, saving the LED layout and the live status change need the **Display Settings** feature in edit mode. The gateway refuses the change without it.

## Frequently asked questions

**What is the Display Setting screen for?** Choosing which matches appear on the table and streaming displays, copying links, exporting lists and saving the LED layout.

**What does the Tables tab show?** One row per table, with its broadcast link. Export on this tab downloads the table list.

**What does the All matches tab show?** Every match of the chosen day and venue, with its Rtmp URL. It has no Hide/Unhide toggle.

**How do I hide a match from the table display?** On the Live Matches tab, toggle **Hide/Unhide** off for the match. Toggle it on again to show it.

**How do I copy the Rtmp URL?** Click the URL in the Rtmp URL column. With several streaming links, click **View Links** and then the link you need.

**Where do I get the team link and the match link?** On the Live Matches tab, click **View Links** (or **Link.match..** for a single match) and copy the address in the row.

**What are the LED layouts and how do I save one?** Open **LED Settings**, click a layout, then click **Save**. The snackbar shows the server message.

**How do I export the match list?** Click **Export** on the Live Matches or All matches tab. The file is matches.xlsx.

**Why does the Hide/Unhide toggle not change?** Check that the event is valid and that you have the Display Settings edit permission. If the server refused the change, no message is shown; reload the screen to see the saved state.

**What does LED Output open?** It opens the live LED card of the event in a new tab, which draws the layout saved on this page.
