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
  - led overlay link
  - generate led link
  - generate overlay link
  - big led
  - umpire screen
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Display Setting screen for?
  - How do I hide a match from the table display?
  - How do I copy the Rtmp URL?
  - How do I generate the LED or overlay link?
  - Which display should I use, big LED, overlay or umpire screen?
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
  - src/app/modules/tms/venue-led/venue-led-link-button/venue-led-link-button.component.html
  - src/app/modules/tms/venue-led/venue-led.constants.ts
  - src/app/shared/no-event-selected/no-event-selected.component.html
  - src/app/modules/tms/award-standings/utils/is-valid-tms-event-id.util.ts
---
# Display Setting screen

The **Display Setting** screen (route `tms/display-setting/:event_id/:participant_id/:category_id`) is the admin page for the table and LED displays. It lists the event's matches in three tabs, lets you show or hide a match on the table display, copies the links for each match, exports the lists, opens the live LED card, and saves the LED layout.

The screen needs a valid event id. The event id is the **last segment** of the address, so `/tms/display-setting/0/0/1358` shows event 1358. With no valid event the page shows the "no event selected" state and makes no event calls.

The screen opens on **Live Matches**. The tabs are **Live Matches**, **All matches** and **Tables**.

## Where to find it
Open **Display Settings** from the sidebar.

## Display Setting screen with no event or no categories
- With no valid event in the address, the screen shows "No record found" and "Create Event to begin with Display Settings.", with a **Go to Event** button.
- When the event has no categories yet, it shows "No record found" and "Add Categories in this event to begin with Display Settings.", with the same **Go to Event** button.
- **Go to Event** opens the event's settings page (Create Event), where you can finish the event and add categories.

## Choose the display first: big LED, overlay or umpire screen
There are three kinds of display, and each has its own link. Decide which one you need before you look for a link.

| Display | What it is | How you get the link |
|---|---|---|
| **Big LED** | The LED board in the hall. It shows several live matches at once as score cards. | Pick and **Save** a layout in **LED Settings**, then click **LED Output**. It opens `/tms/display-live-card/:event_id` (see the LED live card guide). |
| **Overlay** | The score graphic placed over a live video stream, for one match, one sub match or one table. | Click **Export** and open the Excel file. The **match_link**, **table_link** and **sub_match_link** columns hold the overlay links (`/stream/match/...` and `/stream/table/...`). The overlay links are only in this Excel file. The **Broadcast link** on the Live Matches and Tables tabs opens the score card view, not the overlay. |
| **Umpire screen** | The overlay page used for Padel (sport id 2), at `/umpire-view/table/...` or `/umpire-view/match/...`. | For Padel, the **Broadcast link** opens the umpire view instead of the score card view. |

- The **layouts** in LED Settings (3 by 3, 1 by 3 and so on) apply **only to the big LED**. They do not change the overlay or the umpire screen.
- The overlay and the umpire screen show data only while the match is **live**, that is while it is being scored on the mobile scoring app. Each point scored there updates the overlay. With no live match the overlay is empty or shows a blank placeholder.

## Header and toolbars
- Title: **Display Configuration**, with the breadcrumb bar.
- The Live Matches and All matches toolbars have a search box and the buttons **LED Output**, the venue LED link (when that feature is on), **Export** and **LED Settings**.
- The Tables toolbar has **LED Output**, the venue LED link, **Export** and **LED Settings**, but no search box.

## Filters and date strip
- The filters and the date strip are on the **All matches** and **Tables** tabs only. The **Live Matches** tab has no venue, month or date filter; it always lists what is in progress for the event.
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
- When a match has **more than one live sub match**, its Broadcast link cell reads **View Links**. Clicking it opens a small panel with two rows: **Team Link** (the team view of the match) and **Match Link** (the current sub match). Clicking the address in a row opens it in a new tab.
- With one live sub match, or a single match, the cell reads **Link.match..** and opens the match view in a new tab. Hover over it to see the address.
- Each row shows the full address and a blue **copy** icon. The copy icon copies the address and shows "Team link copied to clipboard!" or "Match link copied to clipboard!".
- The addresses shown and copied in the panel are the match view addresses (`/match/...`).
- For sport id 2 (Padel), **Link.match..** and a click on the **Match Link** address open the umpire view instead; for other sports they open the match view. The **Team Link** always opens the match view.

## Rtmp URL and streaming links
- A single streaming link is copied when its URL is clicked. The snackbar says "URL copied to clipboard", or "Failed to copy URL" when the copy fails.
- Several streaming links open a small list. Each entry shows its label (or "Table" and the venue table number when there is no label) and its Rtmp URL. Clicking the URL or the copy button copies that link, and the snackbar names it, for example "Table 2 RTMP URL copied to clipboard!".
- A match is given several streaming links when it is scheduled on more than one table (one stream per table).
## Hide/Unhide (show on table)
- The **Hide/Unhide** toggle on a Live Matches row decides whether the match is shown on the table display.
- The new state is sent to the server at once. There is no confirmation and no success message.
- Changing the toggle needs the **Update Stream** permission in edit mode. Without it the server refuses the change ("Access Denied"), but the screen shows no message.
- If the save fails the screen shows no message and does not reload the list, so the toggle can show a state the server did not keep. Reload the screen to see the saved state.

## Exports
- **Export** on Live Matches and All matches downloads the full match list as "matches.xlsx".
- The file has one row per match, or one row per sub match for a team match. Its columns are **Match ID**, **Date/Time**, **Table No.**, **Category**, **Round**, **Team**, **Match**, **Club**, **Broadcast Link T1**, **Broadcast Link T2** (the Rtmp URLs), **Hide/Unhide**, **match_link**, **table_link** and, for sub matches, **sub_match_link**.
- **match_link**, **table_link** and **sub_match_link** are the **overlay links** of that match, its table and its sub match. Copy the one you need into the streaming software.
- The live export on Live Matches downloads only the matches in progress.
- **Export** on the Tables tab downloads the table list (see the next section).
- A loader shows while the file is prepared. If the download fails, the loader stops and no message is shown.

## Display Setting export file details
- **Date/Time** is written as day/month/year hours:minutes.
- A match on several tables lists all its table numbers in **Table No.**, and its **table_link** cell holds one overlay link per table, separated by commas.
- For a sub match row, **Table No.** and **table_link** use the table the sub match is playing on, when that is known.
- **Broadcast Link T1** and **Broadcast Link T2** hold the first and second Rtmp URL of the match (the second only when the match streams on two tables).
- In the live export (Live Matches tab), a team match only gives rows for its sub matches that are being scored live.
- The Tables tab file has the columns **Table ID**, **Match Count**, **Date**, **Event ID** and **Link**: one row for each table and day with a match in progress. **Match Count** is the number of those matches on that table that day. **Link** is the table's score card view address (`/table/:event_id/:table_id`), not an overlay link.
- When the server cannot build the file (also when there is no match to export) it answers "Failed To Create Excel Export" (or "Failed To Create Table Summary Excel Export" for the table list); the screen shows no message, and nothing is downloaded.

## LED Settings sidebar
- **LED Settings** opens the sidebar titled **Settings**, with the heading **Select what to display**.
- Two cards sit at the top: **Live scores** (selectable) and **Live streaming** (greyed out and disabled).
- **Layouts** – "Pick a score card layout based on your pixels". Five layouts are shown as grids: 3 by 3, 1 by 3, 2 by 3, 2 by 2 and 3 by 4. Click a layout to select it.
- **Card details** – "Select what to display". The options **Parent logo**, **Serve icon**, **T-shirt color**, **Back No.**, **Player Name**, **Specify the live game**, **Overall results** and **Previous results** are shown as toggles. All of them are switched on and locked; they cannot be changed on this screen.
- When the sidebar opens, the layout saved for the event is highlighted. If no layout was ever saved, none is highlighted.
- **Generate Preview** opens the **LED Preview** dialog. It shows a picture for layouts 1, 2 and 3; layouts 4 and 5 show no picture.
- **Save** stores the selected layout for the event (see the API guide). On success the server message ("Led Setting Updated") shows in a snackbar, the saved settings are read again and the sidebar closes. On failure the server message shows in the error style and the sidebar stays open.
- Saving needs the **Display Settings** permission in edit mode (administrators always have it). Without it the error snackbar shows "Access Denied".
- Closing the sidebar with the **X** does not save the layout you clicked.

## LED Output
- **LED Output** opens the live LED card of the event in a new tab: `/tms/display-live-card/:event_id`, or `/tms/stupa-live-card/:event_id` when the sport id is 2 (Padel).
- The live card draws the layout saved here (see the LED live card guide).

## Venue LED link
- The **Generate Display Link** button appears on the toolbars of all three tabs, but only when the venue LED feature is switched on for the organisation.
- It opens a small panel titled **Display link** with the text "Public view, no admin login required.", a **Link** field with the board address (`/tms/venue-led/:event_id`) and a **Copy** button.
- **Copy** copies the full address and shows "Venue LED link copied" (or "Failed to copy URL").
- The panel closes when you click outside it, press Escape or click its close icon.
- The board it links to is the **Live Match Centre**, a separate public page for unattended screens.

## Messages
- Snackbars: "URL copied to clipboard", "Failed to copy URL", "Team link copied to clipboard!", "Match link copied to clipboard!", "Venue LED link copied", the named "... RTMP URL copied to clipboard!", and the server message after **Save** (or its error message when the save fails).
- An empty list shows "No data found" or the sport's no-data text.
- Hide/Unhide and Export show no message.

## Permissions
- Reading the screen needs the login.
- Saving the LED layout needs the **Display Settings** feature in edit mode.
- Changing the **Hide/Unhide** toggle needs the **Update Stream** feature in edit mode.
- Without the needed permission the server refuses the change with "Access Denied". For Hide/Unhide the screen shows no message.

## Frequently asked questions: Display Setting screen
**What is the Display Setting screen for?** Choosing which matches appear on the table and streaming displays, copying links, exporting lists and saving the LED layout.

**What does the Tables tab show?** One row per table, with its broadcast link. Export on this tab downloads the table list.

**What does the All matches tab show?** Every match of the chosen day and venue, with its Rtmp URL. It has no Hide/Unhide toggle.

**How do I hide a match from the table display?** On the Live Matches tab, toggle **Hide/Unhide** off for the match. Toggle it on again to show it.

**How do I copy the Rtmp URL?** Click the URL in the Rtmp URL column. With several streaming links, click **View Links** and then the link you need.

**Where do I get the team link and the match link?** On the Live Matches tab, click **View Links** (or **Link.match..** for a single match) and copy the address in the row.

## Frequently asked questions: Display Setting screen (part 2)
**How do I generate the LED or overlay link?** First choose the display. For the **big LED**, open **LED Settings**, pick a layout, click **Save**, then click **LED Output** and use that page's address. For the **overlay**, click **Export**; the Excel file has the overlay links in the **match_link**, **table_link** and **sub_match_link** columns. For Padel the **umpire screen** link opens from the **Broadcast link**. The overlay shows data only while the match is scored live on the mobile app.

**Which display should I use, big LED, overlay or umpire screen?** The **big LED** is the hall board with many matches at once. The **overlay** is the score graphic over a live video stream of one match or table. The **umpire screen** is the overlay page used for Padel.

**What are the LED layouts and how do I save one?** Open **LED Settings**, click a layout, then click **Save**. The snackbar shows the server message. The layout applies only to the big LED (**LED Output**), not to the overlay.

**How do I export the match list?** Click **Export** on the Live Matches or All matches tab. The file is matches.xlsx. It also holds the overlay links (match_link, table_link and sub_match_link).

## Frequently asked questions: Display Setting screen (part 3)
**Why does the Hide/Unhide toggle not change?** Check that the event is valid and that you have the **Update Stream** edit permission. If the server refused the change, no message is shown; reload the screen to see the saved state.

**Why is there no date or venue filter on Live Matches?** The Live Matches tab always shows every match in progress for the event. The venue, month, year and date filters are on the All matches and Tables tabs.

**Why does the screen say "No record found" with a Go to Event button?** The event is missing or has no categories yet. Click **Go to Event**, finish the event and add categories, then open Display Settings again.

**How do I get the link for an unattended venue screen?** Click **Generate Display Link** (shown only when the venue LED feature is on), then **Copy**. The link needs no admin login.

**Can I change the Card details toggles?** No. They are all switched on and locked on this screen.

**What does LED Output open?** It opens the live LED card of the event in a new tab, which draws the layout saved on this page.
