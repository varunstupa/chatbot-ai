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
  - src/assets/i18n/en.json
---
# Scoring – enter scores, walkovers, manual scoring and streaming

The **Scoring** tab of the fixtures page lists the matches of the stage (or category) so that you can enter results. The **Streaming** and **Stream Settings** tabs are on the same screen. Scores entered here feed the group matrix, the standings and the knockout bracket (see the results guides).

## Scoring tab – the screen

- The search box finds one match by its match ID.
- Category dropdown, and the filter tabs **ALL**, **Without results** and **With results**.
- **Filter Preferences** opens a dialog to filter by participant type, category, stage, rounds and groups.
- **Ready for Print** and **Go to Fixtures** (opens the fixture list) are in the header.
- Columns: **Match ID**, **Date/Time**, **Table No.**, **Round**, **Match**, **Status**, **Score**, **Action**, **VS**, **Match Umpire**.
- If nothing matches the filters, the table shows "No records found".
- The status is **Completed** when all tables of the match are finished, otherwise **In Progress**.

## Entering a score

- Click the match row's score or the edit action to open the score dialog.
- The dialog shows **Venue**, **Group Name**, **Match Order**, **Date**, **Time**, **Table**, **Umpire** and the two sides, **Team A** and **Team B** (or the two players of a pair).
- Each set has a score box for side A and side B. A score box accepts at most 2 digits.
- **Total Score** and the sets-won figure are calculated from the sets.
- **Update** saves the score. **Reset** clears the changes made in the dialog, and **Cancel** closes it.
- If a set is not valid for the game rules, the message is "Invalid normal set score in set {{set_number}}" (for example "Invalid normal set score in set 2"). The game rules are in the Game Play guides for your sport.
- Choosing the same participant for both slots shows "Match #{{matchNumber}}: The same participant is selected for both slots on Side A." (or Side B).
- For a golden match the same check reads "Golden Match #{{matchNumber}}: Same participant selected for both slots on Side A."

## Walkover, double walkover and other reasons

- The **Walkover** dropdown sets the reason a side did not play.
- Options: **Walkover**, **Disqualified**, **Injured**, **Double Walkover** and **Others**. For a team match the **Double Walkover** option is not offered.
- For a walkover, pick the player who did not play in the walkover player box.
- For a double walkover, both sides are marked; no single player is chosen.
- **Update** stays disabled until a player is picked (except for a double walkover).
- **Cancel** closes the walkover panel without saving.
- The walkover reason is shown in the matrix as "walk over" or "D W/O" for a double walkover.

## Manual scoring

- The **manual scoring toggle** starts or stops manual scoring for a match.
- Starting shows "Start match scoring"; stopping shows "Stop match scoring".
- If the change fails, the message is "Failed to update manual scoring", or the server message when one is sent.

## Streaming and stream settings

- To reach it, open **Scoring and Streaming** from the sidebar and click the **Streaming** tab (it is not on the Event page). The **Streaming** tab lists the matches that can be streamed. **Enable Streaming** turns streaming on for a match.
- A match that has already started cannot have streaming turned off: "The match has already started. You cannot disable streaming right now."
- The **Stream Settings** tab sets the streaming options. The filter types are **Participant specific**, **Round specific** and **Match specific**. For round specific, choose the round(s) to stream.
- The link of a stream can be copied from the streaming row.

## Line-ups and player status (team matches)

- For team matches, the lineup panel shows **Players in the Lineup**, with **Player Name** and a status dropdown for each player.
- Choose a team to see its players. Without a team: "Please select a team to view players".
- A status change shows "Player status updated successfully".
- Saving the lineup shows "Lineup saved successfully".
- **Reserve Players** lists the players not in the lineup. **Participant Selection** opens the list of players to add.
- If the lineup save fails, the server message is shown.

## Umpire and referee notes

- The notes panel lists the **Umpire** and the **Referee** for the match. Umpires are numbered (Umpire 1, Umpire 2).
- Notes and assignments are saved from this panel; if the save fails, the server message is shown.

## Sub-matches and playing tables

- A sub-match of a team match needs a playing table before it is saved: "Select a playing table for sub-match {{matchNumber}} before saving."
- The **Tables** column and the **Actions** column show the table and the actions for each sub-match.
- The playing order of a team match is set from the playing order dialog (see the results guide).

## Messages

- Score saved: the server's message (or a generic error) is shown in a snackbar with **Close**.
- "Error searching matches" – the search for the match ID failed; try again.
- "Something went wrong" – a request failed with no message from the server.

## Permissions

- Entering or changing scores needs **Edit** on the score feature (UPDATE_SCORE). Without it the server refuses the change.
- Walkover, lineup and manual scoring changes use the scoring permission of the match.

## Frequently asked questions about scoring

**How do I enter the score of a match?** Open the match row in the Scoring tab, enter the score of each set for both sides, then click **Update**.

**How do I record a walkover?** Open the match, choose **Walkover** (or **Disqualified**, **Injured** or **Others**) in the walkover dropdown, pick the player who did not play, then **Update**.

**What is the difference between Walkover and Double Walkover?** A walkover is one side not playing. A double walkover means neither side plays, so both sides are marked.

**How do I start manual scoring?** Use the manual scoring toggle on the match; it shows "Start match scoring". Turn it off with "Stop match scoring".

**How do I enable streaming?** 1. Open **Scoring and Streaming** from the sidebar. 2. Click the **Streaming** tab. 3. Click **Enable Streaming** on the match. It cannot be turned off once the match has started.

**How do I set the lineup of a team?** Choose the team in the lineup panel, set the status of each player, then save the lineup.

**Why do I see "Invalid normal set score in set 2"?** The score of that set is not allowed by the game rules of your sport. Correct the score using the Game Play guide for the rules.

**What does "Same participant selected for both slots" mean?** The same player or team was chosen for side A and side B. Choose two different participants.
