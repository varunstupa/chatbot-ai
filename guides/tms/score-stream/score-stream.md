---
doc_id: tms.score-stream
title: Scoring and Streaming page – score matches, walkovers, streaming, lineups and print queue
routes:
  - tms/score-stream/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - score stream
  - scoring and streaming
  - scoring page
  - score matches
  - enter scores page
  - streaming page
  - live streaming
  - stream matches online
  - show matches live
  - stream settings
  - match id search
  - search by match id
  - scoring tab
  - scoring walkthrough
  - winner confirmation popup
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Scoring and Streaming page for?
  - How do I enter a score on this page?
  - How do I search a match by its match ID?
  - How do I enable streaming for a match?
  - What are the Stream Settings?
  - How do I filter the matches on this page?
  - Why is there no record on the Scoring and Streaming page?
  - How is the scoring different for each sport?
  - Why is the Update button disabled for a walkover?
  - Why can't I disable streaming after a match starts?
  - Why can't I save a team sub-match?
  - Why can't I see players in the lineup?
backend_sources:
  - gateway/src/routers/scoring_router.py (update_score, _authorize_update_score)
  - gateway/src/routers/match_router.py (matches, update_match_status, sub-matches, reverse-participants-order)
  - gateway/src/routers/teams_router.py (fetch_lineup, update_lineup)
  - gateway/src/routers/rule_setting_router.py (get_rule_settings)
  - gateway/src/routers/playing_order_router.py (get_team_playing_order_with_matches bulk)
  - gateway/src/routers/planner_router.py (event official notes)
  - gateway/src/decorators/decorator.py (permission_decorator)
  - gateway/src/utils/permission_utils.py
source_files:
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.html
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts
  - src/app/modules/tms/score-and-streaming/manual-scoring-toggle-button
  - src/app/modules/tms/score-and-streaming/manual-scoring.constants.ts
  - src/app/modules/tms/score-and-streaming/manual-scoring.util.ts
  - src/app/modules/tms/score-and-streaming/next-unscored-match.util.ts
  - src/app/modules/tms/score-and-streaming/umpire-refree-notes
  - src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts
  - src/app/modules/tms/score-and-streaming/score-input-feedback.util.ts
  - src/app/modules/tms/score-and-streaming/redundant-set.util.ts
  - src/app/modules/tms/score-and-streaming/bulk-streaming
  - src/app/core/services/bulk-streaming/bulk-streaming.service.ts
  - src/app/shared/print-queue-sidebar/print-queue-sidebar.component.html
  - src/app/shared/match-print-popup/match-print-popup.component.html
  - src/app/shared/match-print-popup/match-print-popup.component.ts
  - src/app/modules/tms/tms.module.ts
  - src/assets/i18n/en.json
answer_notes: |
  Answering guidance for the TMS assistant:
  1. Identify which part of the page the user means: match list, score popup, winner confirmation, walkover, manual scoring, streaming, banner, lineup, sub-match, notes, or print queue.
  2. Give the shortest relevant UI path using the exact control labels in this document.
  3. For empty results, distinguish **No records found** (nothing fits the selection) from **Create fixtures to begin with** (Streaming tab, no matches exist).
  4. For score errors, identify the sport and use its sport-specific guide; do not generalize one sport's scoring rules to another.
  5. For streaming or score updates that fail, check the relevant permission and the specific error message.
  6. Do not invent extra controls, permissions, reset conditions, or streaming behavior not stated in the source.
  7. Treat server validation and permission responses as authoritative for whether an action succeeded.
---

# Scoring and Streaming page

## Scoring and Streaming page: scope and purpose
The **Scoring and Streaming** page is used to enter match results, record walkovers or disqualifications, confirm winners, manage manual scoring, enable streaming, manage team-match lineups and sub-matches, add umpire/referee notes, and send scoresheets to print.

Route pattern: `tms/score-stream/:participant_id/:category_id/:event_id/:event_category_id/:stage_id`.

This is the same screen as the Scoring tab on the Fixtures and Results page, opened directly. The sport configured for the event determines how scores are entered and validated. Refer to the sport-specific guides for Table Tennis, Badminton, Padel, and Tennis.

Example URL: `tms/score-stream/0/87/487/1495/11562` (participant type 0 = all participant types, category 87, event 487, event category 1495, stage 11562). The page uses the event saved in the browser session; without a selected event it asks you to select one.

## Scoring and Streaming page: where to find it and its tabs
Open **Scoring and Streaming** from the sidebar.

The page has two tabs:
- **Scoring:** the **Update score** list, where you enter scores and manage match results.
- **Streaming:** enable streaming for matches and view their stream status and links.

A **Stream Settings** tab and a **Filter** button (Filter Preferences) exist in the page design but are currently not shown on the page.

## Scoring and Streaming page: header, categories and stages
- **Search by Match ID** (top right): opens the **Search by Match ID** popup (see its own section).
- **Ready for Print:** opens the **Print Queue**. A badge shows how many matches are waiting to be printed. The button is hidden when print mode is turned off for the event in Print Settings.
- **Participant type dropdown:** the first dropdown filters the category list by participant type.
- **Categories:** the category list shows the event's categories, with the number of subcategories in brackets. Use the arrows to scroll.
- **Subcategories:** labelled **Sub Division** for a league and **Sub Category** otherwise.
- **Stages:** stage tiles such as **S1**, **S2** and so on select the stage.

## Scoring tab: match list views and search
Use these buttons to narrow the list:
- **ALL**
- **Without results**
- **With results**

The **Search** box next to them searches the matches of the selected category and stage as you type.

Columns with sort arrows (**Match ID**, **Date/Time**, **Table No.**, Group and **Round**) can be sorted by clicking the arrows.

The table is paginated. The page-size control is at the bottom of the table.

## Scoring tab: match list columns
The list can display:
- **Match ID**
- **Date/Time** and **Table No.** (shown as "--" when the stage is not scheduled by time or table)
- **Group** or **Knockout**, depending on the stage format
- **Legs** (only in a knockout stage with more than one leg)
- **Round**
- **Match**: both participants with **VS**. For doubles both players are shown. A forfeited player is shown in red with a forfeited icon.
- **Umpire** or **Umpires** (when two umpires are used per match). Extra officials show as "N more"; hover to see them.
- **Status**: the match status: Not Started, In Progress, Scored or Completed.
- **Score**: sets won, or match points for a match-point system. A walkover adds **W/O**, a double walkover **D W/O**.
- **Action**: edit score, manual scoring (when available) and notes icons. Rows without both participants show "--".

In a league, the edit-score icon only appears on matches you are allowed to score; other rows only show the notes icon.

## Scoring and Streaming page: empty states
- **No records found:** no matches fit the selected category, stage, view or search.
- On the **Streaming** tab, when there are no matches: **No records found** with "Create fixtures to begin with. Trigger streaming from the mobile app to view here." and a **Go to Fixtures** button.

If the list is empty, first check the selected participant type, category, stage, view (ALL / Without results / With results) and search text. If there are no fixtures for the event, go to Fixtures to create them.

## Search by Match ID popup
1. Click **Search by Match ID** in the header.
2. Type the match ID in **Enter Match ID** and press **Enter**.
3. The search covers the whole event (all categories and stages). When a match is found, its score popup opens directly.

The results show Match ID, Date/Time, Table No., Category, Round, Match, Member Association or Club (when the event uses them), Umpire, Status and Score.

- No match with that ID: **No records found**.
- The search request failed: `Error searching matches`.

## Edit score popup (singles and doubles)
Click the edit-score icon on a match row to open the **Edit** popup. It shows the venue, group name, match order (group stages), date, time, table and umpires, then one row per side.

- Each set has one score box per side; each box accepts at most two digits.
- A tie-break, where the format supports it, has its own two small score boxes.
- **Total Score** shows the sets won so far.
- The eraser icon in **Action** clears the match score.
- **W/O** opens the walkover settings (see Walkover settings).
- Click **Save** to save the score. Close the popup with the X icon.
- Once the entered sets already decide the match, the remaining empty sets are locked (greyed out). This does not apply when the rules play every set.

For Padel and Tennis the page checks set scores as you type, marks a rejected set in red and explains the rule. The server validates the full score again when it is saved and shows **Score Updated Successfully** on success. Use the sport-specific guide to interpret validation messages.

## Edit score popup: sets after the match is decided
If a set after the deciding set still contains a score, it is marked red and **Save** is refused with: "Invalid Score: Set {n} cannot be scored because the match has already concluded." Clear that set and save again.

For team matches, once the team result is decided, sub-matches that were never played are locked (their set boxes and actions are disabled), unless the sub-match rule plays every match. Saving a score in such a sub-match shows: "Score Entry Not Allowed: The match winner has already been decided."

## Edit score popup: when the server refuses a save
- "Match Already Walkover Reset First": clear the walkover before entering sets.
- "Cannot update score: a dependent stage is already in progress or completed.": a later stage that takes players from this stage has started, so this stage's scores can no longer be changed or reset.
- "Next round already scored": a knockout result was carried forward and the next match (winner's or loser's) is in progress or scored.
- "Participant payment is pending": a replacement player's payment has not cleared.
- "Please reset golden match first.": the golden match of this team tie has started.
- Team matches: "Playing format not found" (no playing order) or "Sub-match lineup is incomplete".
- Eraser (reset): "Cannot reset a match that has not started" or "Reset blocked because of an active forfeit".
- A result with a winner (or a tie) sets the match to **Scored**; otherwise it stays **In Progress**.

## Winner Confirmation popup
After a saved score decides a singles or doubles match, the **Winner Confirmation** popup opens over the Edit popup:
- "{name} has won the match, please confirm to proceed with the winner", with a trophy on the winner's card.
- For a double walkover: "Match resulted in a Double Walkover. No winner has been declared".

Buttons:
- **Confirm** (also the Enter key): accepts the result and closes the Edit popup. In a group or other non-knockout stage, the next unscored match in the list opens automatically so you can keep scoring.
- **Cancel** or the X icon: **clears the score that was just saved** and keeps the Edit popup open, so you can enter it again.

Team matches show the same popup for each sub-match result; there **Cancel** clears that sub-match score.

## Walkover settings (singles and doubles)
Click **W/O** in the Edit popup to switch it to **Walkover Settings**: "Select the participant won by walkover with reason."

The **Select walkover reason** dropdown offers **Walkover**, **Disqualified**, **Injured**, **Double Walkover** and **Others**. **Double Walkover** is not offered for team matches.

1. Click the participant card to mark it **W/O** (for a double walkover, mark both).
2. Choose the reason.
3. Click **Update**. It stays disabled until a participant is selected (for a double walkover, at least one).

**Cancel** leaves walkover mode. **Clear Walkover** (shown once a participant is selected) removes the walkover. A recorded walkover must be cleared before new set scores can be saved; otherwise the server returns `Match Already Walkover Reset First`.

## Manual scoring toggle (Scoring tab)
The manual scoring button in the **Action** column starts or stops manual scoring for a match. It is only shown when the organisation's setup includes the venue display feature.

- **Start match scoring**: starts it (the match status becomes In Progress).
- **Stop match scoring**: stops it (status back to Not Started).
- After a successful change the same text appears as a confirmation and the list refreshes.

The button is locked:
- "Manual scoring is unavailable after the match is scored" when the match status is Scored.
- "Manual scoring cannot be changed after a sub-match has been scored" for a team match whose score is no longer 0-0.

If the change fails, the server message or `Failed to update manual scoring` is shown.

## Streaming tab: list and statuses
To access streaming controls:
1. Open **Scoring and Streaming** from the sidebar.
2. Select the **Streaming** tab.

The Streaming tab is not on the Event page. Its columns are Match ID, Date/Time, Table No., Group or Knockout, Round, Match, Match Umpire, Status, Score and Action.

The **Status** column shows:
- **Streaming**: live
- **Completed**
- **Not Streamed**

Hover over the status to see each table's stream (for matches streamed on several tables).

## Streaming tab: enabling streaming and the action icons
Use the toggle in the **Action** column to enable streaming (publish the stream) for a match. When it is turned on, a stream is created for the match (one per table when the match uses several tables).

Other icons in the **Action** column:
- **Copy RTMP URL**: works only while the toggle is on. Copies the link ("RTMP URL copied to clipboard!"). With several tables a list of links opens; click one to copy it. Messages: "No RTMP URL available to copy", "Copy failed. Try selecting and copying manually."
- **Reset**: removes the match's stream.
- **Banner** (only while the toggle is on): opens **Upload Banner**.
- **View**: switches the stream video on or off.

If a request fails, the toggle returns to its previous state and the error (or "Something went wrong") is shown.

## Streaming tab: bulk streaming (select several matches)
Users with the **Update Stream** edit permission see a checkbox column on the **Streaming** tab.

- Tick matches one by one, or use the header box ("Select all matches on this page").
- Matches that are **Streaming** or **Completed** cannot be selected ("Matches streaming right now cannot be selected", "Completed matches cannot be selected").
- While matches are selected, a bar shows "{count} matches selected" with **Clear selection**, **Disable stream** and **Enable stream**. Search by Match ID, the Search box and the row action icons are locked ("Locked while matches are selected").
- Changing the stage or tab clears the selection.

## Streaming tab: bulk streaming confirmation and results
**Enable stream** or **Disable stream** opens a confirmation, for example "Enable streaming for {count} matches?", listing the matches under "Will be enabled ({count})" and those skipped under "Skipped ({count})" (**Already enabled** / **Already disabled**). Matches without date, time or table are tagged **Not scheduled yet**; streaming can still be set for them.

The change is applied automatically after 10 seconds ("Streaming will be enabled automatically in {seconds} s. Click the button to do it now, or Cancel."). Click **Enable now ({seconds} s)** / **Disable now ({seconds} s)** to apply at once, or **Cancel**. If nothing would change: "0 matches will change" with **Close**.

A result banner then shows, for example, "{count} matches streaming enabled", "{count} already enabled and skipped" and "{count} failed" with **Retry**. Failed rows get a warning icon: "Streaming change failed: {reason}". If the request fails: "Could not update streaming. Your selection is kept, please try again."

## Streaming tab: when streaming cannot be turned off
The toggle is disabled once the stream status is **Streaming** or **Completed**. Clicking it while the match is streaming shows:

`The match has already started. You can't disable streaming right now.`

If the match has started, this is an expected restriction rather than a generic streaming failure.

## Upload Banner popup (Streaming tab)
Opened from the banner icon of a match whose streaming toggle is on.

- **Banner Image**: "Upload Image of resolution 250X150", "Supported: JPEG, PNG (Max: 2MB)".
- **Upload Another**: choose a .png, .jpg or .jpeg file. A file over 2 MB is refused with "Size Exceed more than 2mb".
- **Update**: saves the image as the stream's banner. It does nothing until a new image has been chosen and uploaded.

Closing the popup discards the new image.

## Stream Settings (Select Stream Preferences)
The **Stream Settings** tab is currently hidden on the page. Its popup, **Select Stream Preferences**, offers:

- **Participant specific:** matches involving selected participants.
- **Round specific:** matches in selected rounds.
- **Match specific:** selected individual matches.

Do not assume streaming preferences automatically enable streaming for any match; use the toggle on the Streaming tab.

## Edit popup for team matches: tabs
For a team match the edit popup has three tabs:
- **Lineup**: the players of each team and their status.
- **Participants**: choose who plays each sub-match and on which table.
- **Scores**: enter each sub-match score.

The header shows the umpires and, when assigned, the referee.

Before a team match can be scored, a playing order must be set. Otherwise the page shows: "Please set playing order in preference for update score for team matches."

## Edit popup for team matches: Lineup tab
Select a team tab to see its players.

- **Players in the Lineup**: players with **Active** status, with a player count.
- **Reserve Players**: players with **Reserve** status (shown only when there are any).
- Opening a team shows `Team Match Participants Fetched`, or `Team Match Participants Created` the first time (the lineup is built from the team's members). A team without members: `No Team Participants For Auto Creation`.
- Each player has a status dropdown (**Active** / **Reserve**). A change is saved at once and shows `Participant Status Updated`.
- A **Loan** tag marks a loan player.
- If no team is selected: `Please select a team to view players`.

**Loan Players** and **Team Parent** buttons appear in the footer when they are turned on in the category's sub-match settings.

## Loan Players and Team Parent popup
Opened from **Loan Players** or **Team Parent** on the Lineup tab. The title is **Select Loan Players** or **Select Team Parent**.

- **Search** filters the list.
- Columns: a selection checkbox (the header box selects all), **Seeding**, **Name**, **Club Name**, **Points**.
- **Add Player** adds the selected players. With none selected: "Please select at least one player".
- An empty list shows "No data found for this event".

Closing the popup returns you to the Edit popup.

## Edit popup for team matches: Participants tab
Under **Participant Selection**, each sub-match row has a player dropdown for each side (two for doubles), a **Tables** column (**Select table**) and an **Actions** column.

- The swap icon between the team names reverses the sides of the sub-matches.
- **Clear** (on a saved row) clears that sub-match's selection.
- **Reset** (shown once sub-matches exist) resets all sub-match selections.
- A **Golden Match** section, with its own Reset, appears when a golden match has been created.

Click **Save** to save the selections. One side may be saved while the other is still empty.

## Team sub-match validation messages
When several tables are used, each sub-match needs a playing table:

`Select a playing table for sub-match {matchNumber} before saving.`

The same participant cannot be selected in both slots on the same side:
- `Match #{n}: The same participant is selected for both slots on Side A.`
- `Match #{n}: The same participant is selected for both slots on Side B.`
- Golden match: `Golden Match #{n}: Same participant selected for both slots on Side A.` (or Side B).

Check the player selections for the side named in the error and make sure each slot has a different participant.

## Edit popup for team matches: Scores tab
- The left list shows each sub-match (and the golden match); click one to score it.
- Each sub-match row shows the sides, **Scorer**, set boxes, **Total Score**, **Match Score** and **Action**.
- A sub-match can be scored only after both sides of its lineup are filled; otherwise its action shows "-".
- **Save** in the row saves that sub-match. The eraser clears it; **W/O** opens its walkover settings (**Update**, **Cancel**, **Clear Walkover**).
- **Reset** (once sub-matches exist) clears the team score; a team-level **W/O** records a walkover for the whole team match.
- **League events:** a **Publish** toggle publishes the match result ("Updated" on success, "Something went wrong" on failure).

The team-match playing order is set in the playing order preference; see the results guide.

## Add Note popup (umpire and referee notes)
Click the notes icon on a match row to open **Add Note**.

- The left side shows the **Umpire** names and an **Umpire Note** box; the right side shows the **Referee** names and a **Referee Note** box.
- Each note is limited to 500 characters ("0/500 characters" counter).
- At least one note is required: "Please enter at least one note".
- The button reads **Save** for new notes and **Update** when notes already exist ("Saving..." while saving).
- Success shows the server's message "Success"; failures show the server message (for example "Invalid Input"), "Failed to save notes" or "Error saving notes".

## Print popups and Print Queue (Scoring and Streaming page)
When print mode is on for the event (Print Settings), saving a result in a **knockout** stage of an individual (non-team) category can make new matches ready to print:
- One match: a **New Match Ready** popup "Is now available for printing" with **Print Now** and **Queue**.
- Several: a "{round} Ready" popup ("{count} matches created in this category", "+ {count} more matches") with **Print All matches** and **Queue All**.

Closing a popup, or letting it auto-dismiss ("Auto-dismissing in {seconds}s"), adds its matches to the queue: "Pop-up auto-dismissed. Match added to queue automatically." These popups wait until the Edit and Winner Confirmation popups are closed.

**Ready for Print** opens the **Print Queue** panel: search ("Search by player, match or category..."), a **Category** filter, and columns **Category/Round/Match**, **Players**, **Time Added**. **Print All** and **Print Selected** stay disabled until there are queued or selected matches. Empty: "No queued matches found."

## Scoring and Streaming page: common messages
| Message | Meaning / next check |
|---|---|
| `Score Updated Successfully` | The server saved the score. |
| `Invalid normal set score in set {set_number}` | The set score is invalid under the sport rules. See the sport guide. |
| `Match Already Walkover Reset First` | Clear the walkover before changing set scores. |
| `Cannot reset a match that has not started` | The eraser was used on a match without a score. |
| `Next round already scored` | The next knockout match is in progress or scored. |
| `Access Denied` | The user is not allowed to make this change. |
| `Something went wrong` | A request failed without a more specific message. |
| `Error searching matches` | The match-ID search failed. Verify the ID and retry. |
| `Failed to update manual scoring` | The manual-scoring change failed. |

## Scoring and Streaming page: permissions
- **Scoring:** needs the **Update Score** edit permission. In the admin app the user must also be an administrator, have Live Match Centre edit access, have the event's "Event Access" scoring permission, or have **Update Score** for that match. Others get `Access Denied`.
- **Manual scoring, team sub-matches and notes:** need the **Update Score** edit permission.
- **Streaming:** needs the **Update Stream** edit permission. Bulk streaming changes at most 100 matches at a time, all from the current event.
- **Lineup:** loading players and changing their status only need a login.

If an action is refused, check that the user has the relevant permission before assuming the score or stream settings are invalid.

## Frequently asked questions: Scoring and Streaming page
**What is the Scoring and Streaming page for?** It is used to enter match results, record walkovers or disqualifications, start or stop manual scoring, enable streaming, manage team lineups and sub-matches, add umpire/referee notes, and print scoresheets.

**How do I enter a score on this page?** Click the edit-score icon on the match row, enter each set's score (and tie-break points when needed), click **Save**, then **Confirm** in Winner Confirmation.

**How do I search a match by its match ID?** Click **Search by Match ID**, type the ID in **Enter Match ID** and press **Enter**. The score popup of the found match opens directly.

**How do I filter the matches on this page?** Choose the participant type, category, subcategory and stage, then use **ALL**, **Without results** or **With results** and the **Search** box. The Filter Preferences button is currently not shown.

**Why is there no record on the Scoring and Streaming page?** "No records found" means no matches fit the current category, stage, view or search. On the Streaming tab, "Create fixtures to begin with." means there are no matches yet; use **Go to Fixtures**.

## Frequently asked questions: Scoring and Streaming page: streaming and lineup questions
**How do I enable streaming for a match?** Open **Scoring and Streaming**, select the **Streaming** tab, and turn on the toggle in the match's **Action** column.

**How do I show my matches live on the internet?** Stream them: on the **Streaming** tab, turn on each match's toggle and use the copied RTMP URL in your streaming software. Streaming cannot be turned off once the match has started.

**Why can't I disable streaming after a match starts?** The toggle is locked once the stream is Streaming or Completed: `The match has already started. You can't disable streaming right now.`

**What are the Stream Settings?** Participant-specific, round-specific or match-specific stream preferences. The Stream Settings tab is currently hidden.

**Why can't I see players in the lineup?** Select a team tab first. Without a selected team the page displays `Please select a team to view players`.

## Frequently asked questions: Scoring and Streaming page: team, walkover and sport questions
**How do I turn streaming on for many matches at once?** On the **Streaming** tab tick the matches (or the header box), click **Enable stream**, then confirm or wait 10 seconds.

**Why can't I save a team sub-match?** Check that a playing table is selected for each sub-match (when several tables are used), that the same participant is not selected in both slots of a side, and that a playing order is set.

**Why is the Update button disabled for a walkover?** No participant is marked **W/O** yet. Click the participant's card (for a double walkover, at least one card).

**What happens if I click Cancel in Winner Confirmation?** The score you just saved is cleared so you can enter it again.

**Why is the manual scoring button greyed out?** The match is already scored, or for a team match a sub-match already has a score.

**How is the scoring different for each sport?** The accepted scores and validation rules depend on the event's sport and Game Play settings. Use the sport-specific guide for Table Tennis, Badminton, Padel or Tennis.

## Natural-language and Hinglish query patterns (Scoring and Streaming page)
Treat these as equivalent intents when retrieving this document:

- "Scoring and Streaming page ka use kya hai?"
- "Match ka score kahan enter karna hai?"
- "Match ID se match kaise search karun?"
- "Scoring page par records kyun nahi aa rahe?"
- "Without results aur With results mein kya difference hai?"
- "Streaming kaise enable karun?"
- "Match start hone ke baad streaming off kyun nahi hoti?"
- "Lineup mein players kyun nahi dikh rahe?"
- "Team sub-match save kyun nahi ho raha?"
- "Walkover ke baad score edit kyun nahi ho raha?"
- "Winner confirmation mein cancel karne se kya hota hai?"
- "Ready for Print ka use kya hai?"
- "Manual scoring start ya stop kaise karun?"
