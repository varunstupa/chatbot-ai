---
doc_id: tms.fixture.scoring
title: Scoring – enter scores, walkovers, manual scoring, match status, line-ups and streaming
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - score and streaming
  - enter score
  - edit score
  - update score
  - walkover
  - double walkover
  - walk over
  - injured player
  - disqualified player
  - manual scoring
  - start match scoring
  - stop match scoring
  - match status
  - lineup
  - team lineup
  - umpire notes
  - referee notes
  - enable streaming
  - scoring filter
  - filter preferences
  - ready for print
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I enter the score of a match?
  - How do I record a walkover?
  - What is the difference between Walkover and Double Walkover?
  - How do I start manual scoring for a match?
  - How do I enable streaming for a match?
  - How do I set the lineup of a team?
  - Why do I see "Invalid normal set score in set 2"?
  - What does "Same participant selected for both slots" mean?
backend_sources:
  - gateway/src/routers/scoring_router.py (update_score; feature UPDATE_SCORE, Edit; LMC or resource permission)
  - gateway/src/routers/match_router.py (update_match_status)
  - gateway/src/routers/teams_router.py (fetch_lineup, update_lineup)
  - gateway/src/routers/registration_router.py (update_event_participant)
source_files:
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.html
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts
  - src/app/modules/tms/score-and-streaming/manual-scoring-toggle-button
  - src/app/modules/tms/score-and-streaming/umpire-refree-notes
  - src/app/modules/tms/score-and-streaming/manual-scoring.constants.ts
  - src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts
  - src/app/modules/tms/score-and-streaming/score-input-feedback.util.ts
  - src/app/modules/tms/score-and-streaming/manual-scoring.util.ts
  - src/app/modules/tms/score-and-streaming/redundant-set.util.ts
  - src/app/modules/tms/score-and-streaming/bulk-streaming
  - src/app/modules/tms/fixture-configuration/fixture-configuration.component.ts
  - src/app/modules/tms/fixture-tree/single-tree/single-tree.component.ts
  - src/assets/i18n/en.json
---
# Scoring – enter scores, walkovers, manual scoring and streaming

Scores are entered in the score dialog. On the fixtures page you open it from the edit (pencil) icon of a match in the group matches or in the knockout bracket; the same dialog is used on the **Scoring and Streaming** screen, which lists all matches with **Scoring** and **Streaming** tabs. Scores entered here feed the group matrix, the standings and the knockout bracket (see the results guides).

## Scoring – opening the score dialog from the fixtures page

- Group stage: click the edit icon of a match in the group matches list.
- Knockout bracket: the edit icon is shown only when both participants of the match are known. It is hidden while a side is still "TBD" or a BYE, for a skipped match, and for a match played over two legs.
- For a team match, the playing order must be set first. Otherwise the message is "Please set playing order in preference for update score for team matches."
- After you save, the group matrix, standings or bracket on the fixtures page refresh by themselves.

## Scoring tab – the screen

- This list is on the **Scoring and Streaming** screen. Choose the participant type, the category (and **Sub Category** or **Sub Division** when the category has children) and the stage (S1, S2 ...).
- The filter buttons **ALL**, **Without results** and **With results** narrow the list. The **Search** box searches the matches; a separate **Search by Match ID** box ("Enter Match ID") finds one match by its ID.
- The **Filter Preferences** button and the **Stream Settings** tab are currently hidden on this screen.
- **Ready for Print** (with a count of matches waiting) and **Go to Fixtures** (opens the fixture list) are in the header. **Ready for Print** is hidden when print alerts are turned off for the event.
- Columns: **Match ID**, **Date/Time**, **Table No.**, **Round**, **Match**, **Status**, **Score**, **Action**, **VS**, **Match Umpire**.
- If nothing matches the filters, the table shows "No records found".
- The status is **Completed** when all tables of the match are finished, otherwise **In Progress**.

## Entering a score

- Click the match row's score or the edit action to open the score dialog.
- The dialog shows **Venue**, **Group Name**, **Match Order**, **Date**, **Time**, **Table**, **Umpire** and the two sides, **Team A** and **Team B** (or the two players of a pair).
- Each set has a score box for side A and side B. A score box accepts at most 2 digits. When a set needs a tie-break, a small tie-break box appears next to the set score.
- **Total Score** and the sets-won figure are calculated from the sets.
- The eraser icon in the **Action** column clears the score of the match. The **W/O** button opens the walkover panel (tooltip "Edit Walkover").
- **Update** saves the score. **Reset** clears the changes made in the dialog, and **Cancel** closes it.
- Invalid set scores are explained in the validation section below.
- Choosing the same participant for both slots shows "Match #{{matchNumber}}: The same participant is selected for both slots on Side A." (or Side B).
- For a golden match the same check reads "Golden Match #{{matchNumber}}: Same participant selected for both slots on Side A."

## Score dialog – score validation messages

Invalid set scores are flagged with a red shake on the set and a message:
- "Invalid normal set score in set {{set_number}}" (for example "Invalid normal set score in set 2") – a Padel or Tennis set that the game rules do not allow.
- "This score is not valid for your Game Play Settings. Sets are first to {{setPoint}} games (best of {{setCount}}), win by {{winBy}}, and tie-break is off. {{scoreA}}-{{scoreB}} cannot be a completed set." – a tied set at or above the set target when tie-break is off.
- Refusals from the server when saving include "Tie-break is required for this set.", "Invalid tie-break score in set {{set_number}}.", "The tie-break is not complete. Win by the configured margin.", "The submitted set scores do not match the configured number of sets.", "The match is not concluded. Complete the required sets before saving.", "Wrong score input for set {{set_number}}" and "Set exceeded".
- Some are shown exactly as the server sends them, for example "Extra set 3 provided after match already decided", "Super tie-break can only be played when the sets are level in set 3" and "Under Special Rule, all configured sets must be completed before saving the match. Set 2 was not played."

The game rules are in the Game Play guides and the Scoring and Streaming guides for your sport.

## Score dialog – when the server refuses a save

- "Match Already Walkover Reset First" – the match has a walkover; clear it before entering sets.
- "Cannot update score: a dependent stage is already in progress or completed." – a later stage that takes players from this stage has started; this stage's scores are locked.
- "Next round already scored" – a knockout result was already carried forward and the next match is in progress or scored.
- "Participant payment is pending" – a replacement player's payment has not cleared.
- "Please reset golden match first." – the golden match of this team tie has started.
- "Cannot reset a match that has not started" and "Reset blocked because of an active forfeit" – the eraser (reset) was refused.
- "Access Denied" – you do not have scoring permission for this match.

## Score dialog – sets after the match is decided

- Once the sets entered decide the match, the remaining empty set boxes are locked (greyed out) for every sport.
- A later set that still holds a score is outlined in red and the score cannot be saved: "Invalid Score: Set {{set_number}} cannot be scored because the match has already concluded." Clear that set to save.
- Team matches: once the tie has a winner, sub-matches that were never played are locked, including their action buttons. Entering a score in one shows "Score Entry Not Allowed: The match winner has already been decided." When the Special rule covers matches, every sub-match is played and nothing is locked.

## Score dialog – Winner Confirmation popup

- After a score that decides the match, the **Winner Confirmation** popup shows "{{name}} has won the match, please confirm to proceed with the winner", with the winner card marked by a trophy.
- For a double walkover it shows "Match resulted in a Double Walkover. No winner has been declared".
- **Confirm** saves the result. **Cancel** (or the close icon) clears the score just entered instead of saving it.
- Team matches show the same popup for each sub-match winner.

## Walkover, double walkover and other reasons

- Click **W/O** in the score dialog. The panel reads "Select the participant won by walkover with reason." Click a participant card to mark it (it shows a W/O tag), then choose the reason in the "Select walkover reason" dropdown.
- Options: **Walkover**, **Disqualified**, **Injured**, **Double Walkover** and **Others**. For a team match the **Double Walkover** option is not offered.
- For a double walkover, both participants are marked automatically (click a card to unmark or re-mark it; at most two).
- **Update** stays disabled until a reason is chosen and a participant is marked; for a double walkover both participants must be marked.
- **Cancel** closes the walkover panel without saving. **Clear Walkover** (shown once a participant is marked) removes the walkover.
- The walkover reason is shown in the matrix as "walk over" or "D W/O" for a double walkover.

## Manual scoring

- The manual scoring button in the **Action** column starts or stops manual scoring for a match. Its tooltip is "Start match scoring" (play icon) or "Stop match scoring" (stop icon), and the same text is shown as the success message.
- The button is shown only for organisations that use venue LED displays (the same setting that shows **Generate Display Link**).
- Starting sets the match status to In Progress; stopping sets it back to Not Started.
- It is locked after the match is scored: "Manual scoring is unavailable after the match is scored".
- For a team match it is locked once any sub-match has a score: "Manual scoring cannot be changed after a sub-match has been scored".
- If the change fails, the message is "Failed to update manual scoring", or the server message when one is sent.

## Streaming and stream settings

- To reach it, open **Scoring and Streaming** from the sidebar and click the **Streaming** tab (it is not on the Event page). The **Streaming** tab lists the matches that can be streamed. **Enable Streaming** turns streaming on for a match.
- A match that has already started cannot have streaming turned off: "The match has already started. You can't disable streaming right now."
- The **Stream Settings** tab (filter types **Participant specific**, **Round specific** and **Match specific**) exists but is currently hidden.
- The RTMP link of a live stream can be copied from the streaming row: "RTMP URL copied to clipboard!" (with the table name when there are several links, chosen from a small list). Without a link: "No RTMP URL available to copy". If copying fails: "Copy failed. Try selecting and copying manually."

## Streaming tab – bulk enable or disable streaming

- Users with Edit on Update Stream see a checkbox on each streaming row and a "Select all matches on this page" checkbox in the header.
- Completed matches ("Completed matches cannot be selected") and matches streaming right now ("Matches streaming right now cannot be selected") cannot be ticked.
- With matches ticked, a bar shows "1 match selected" or "{{count}} matches selected", **Clear selection**, **Enable stream** and **Disable stream**. While a selection exists, the search, the match ID search and the row streaming toggles are locked ("Locked while matches are selected").
- A confirmation "Enable streaming for {{count}} matches?" (or Disable) lists what will change and what is skipped ("Already enabled", "Already disabled") and notes matches "Not scheduled yet". It applies by itself after 10 seconds; **Enable now ({{seconds}} s)** / **Disable now ({{seconds}} s)** applies at once, or **Cancel**.
- A result banner shows, for example, "{{count}} matches streaming enabled", "{{count}} already enabled and skipped" and "{{count}} failed", with **Retry**. Failed rows show "Streaming change failed: {{reason}}". If the request fails: "Could not update streaming. Your selection is kept, please try again."

## Line-ups and player status (team matches)

- For team matches, the lineup panel shows **Players in the Lineup**, with **Player Name** and a status dropdown for each player.
- Choose a team to see its players. Without a team: "Please select a team to view players".
- Loading a team's players shows "Team Match Participants Fetched", or "Team Match Participants Created" the first time (the lineup is then built from the team's members). A team without members: "No Team Participants For Auto Creation".
- A player status change is saved at once and shows "Participant Status Updated".
- **Reserve Players** lists the players not in the lineup. **Participant Selection** opens the list of players to add.
- Adding players without choosing any shows "Please select at least one player".
- If the lineup save fails, the server message is shown.

## Umpire and referee notes

- The notes panel lists the **Umpire** and the **Referee** for the match. Umpires are numbered (Umpire 1, Umpire 2).
- The **Add Note** popup has an **Umpire Note** and a **Referee Note** box ("Enter note here"), each up to 500 characters.
- At least one note is needed: "Please enter at least one note". The button reads **Save**, or **Update** when notes already exist, and **Saving...** while saving.
- Success shows the server's message "Success". Failure shows the server message (for example "Invalid Input"), "Failed to save notes" or "Error saving notes".

## Sub-matches and playing tables

- A sub-match of a team match needs a playing table before it is saved: "Select a playing table for sub-match {{matchNumber}} before saving."
- The **Tables** column and the **Actions** column show the table and the actions for each sub-match.
- The playing order of a team match is set from the playing order dialog (see the results guide).

## Ready for Print and New Match Ready popups

- When matches become ready to print, a popup "{{round}} Ready" appears at the bottom right; a newly ready match shows **New Match Ready**. From it you can print the matches or add them to the print queue.
- If the popup is not used it closes by itself with "Pop-up auto-dismissed. Match added to queue automatically."
- **Ready for Print** in the header opens the print queue. None of this appears when print alerts are turned off for the event. See the printing guide.

## Messages

- Score saved: "Score Updated Successfully" in a snackbar with **Close**. A refusal shows the server's reason (see the score dialog sections).
- "Error searching matches" – the search for the match ID failed; try again.
- "Something went wrong" – a request failed with no message from the server.

## Permissions

- Entering, resetting or walking over a score needs **Edit** on **Update Score**. In the admin app the user must also be the main admin, have Live Match Centre access, have "Event Access" scoring permission for the event, or have Update Score on that match. Otherwise: "Access Denied".
- Manual scoring, sub-match selections and umpire/referee notes need **Edit** on **Update Score**.
- Streaming needs **Edit** on **Update Stream**.
- Lineup loading and player status changes only need a login.

## Frequently asked questions about scoring

**How do I enter the score of a match?** Open the match row in the Scoring tab, enter the score of each set for both sides, then click **Update**.

**How do I record a walkover?** Open the match, click **W/O**, click the participant, choose **Walkover** (or **Disqualified**, **Injured** or **Others**) in the reason dropdown, then **Update**.

**What is the difference between Walkover and Double Walkover?** A walkover is one side not playing. A double walkover means neither side plays, so both sides are marked.

**How do I start manual scoring?** Use the manual scoring button on the match row ("Start match scoring"). Turn it off with "Stop match scoring". The button only appears for organisations with venue LED displays.

## Frequently asked questions about scoring – streaming, lineups and errors

**How do I enable streaming?** 1. Open **Scoring and Streaming** from the sidebar. 2. Click the **Streaming** tab. 3. Click **Enable Streaming** on the match. It cannot be turned off once the match has started.

**How do I set the lineup of a team?** Choose the team in the lineup panel and set the status of each player. Each status change is saved at once ("Participant Status Updated").

**Why can't I see the edit icon on a knockout match?** Both participants must be known. The icon is hidden while a side is TBD or a BYE, for skipped matches and for two-leg matches.

**Why are some set boxes greyed out?** The match is already decided by the earlier sets, so the remaining sets cannot be scored.

**Why is the manual scoring button greyed out?** The match is already scored, or (team match) a sub-match already has a score.

**Why do I see "Invalid normal set score in set 2"?** The score of that set is not allowed by the game rules of your sport. Correct the score using the Game Play guide for the rules.

**Why can I no longer change a score in this stage?** "Cannot update score: a dependent stage is already in progress or completed." means a later stage has started; "Next round already scored" means the next knockout match is in progress or scored.

**What does "Same participant selected for both slots" mean?** The same player or team was chosen for side A and side B. Choose two different participants.
