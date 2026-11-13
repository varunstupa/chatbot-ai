---
doc_id: tms.fixture.api-scoring
title: Backend logic of the scoring APIs – score update, match status, sub-matches, lineups and official notes
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - score api
  - update score rules
  - why is the score not saved
  - score rejected by the server
  - walkover reset rules
  - match status api
  - stream status rules
  - sub match api
  - reverse order rules
  - lineup api
  - fetch lineup rules
  - update lineup rules
  - official notes api
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What does the backend check before it saves a score?
  - Why does the server say "Match Already Walkover Reset First"?
  - Why does the server say "Next round already scored"?
  - What does the match status call do when a video is missing?
  - What does the backend do when a lineup has no participants?
  - What does "Participant not found or invalid status description" mean?
backend_sources:
  - gateway/src/routers/scoring_router.py (update_score)
  - gateway/src/routers/match_router.py (update_matches, update_match_status, upsert_sub_matches, reverse_participants_order)
  - gateway/src/routers/teams_router.py (fetch_lineup, update_lineup)
  - gateway/src/routers/planner_router.py (get_event_official_notes, update_event_official_note)
  - gateway/src/routers/registration_router.py (update_event_participant)
  - tms/src/service/scoring_service.py (update_score)
  - tms/src/service/match_service.py (update_matches, upsert_sub_matches, reverse_participants_order)
  - tms/src/service/teams_service.py (fetch_lineup, update_lineup)
source_files:
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts
  - src/app/modules/tms/score-and-streaming/umpire-refree-notes
  - src/app/modules/tms/score-and-streaming/manual-scoring-toggle-button
  - src/app/modules/tms/score-and-streaming/manual-scoring.util.ts
  - src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts
---
# Backend logic – scoring APIs

Each section gives the gateway step, the TMS checks in order, and the message shown. The gateway checks the login and the permission before it forwards each call. Scoring calls that need the event ID check the event ID header first.

## Update score (PUT score/v1/update_score)

- Gateway: needs the event ID header ("event-id header is required", 400). The header must be a whole number ("event-id header must be a valid integer", 400) and must match the event of the score ("event-id header must match the request event_id", 422). Needs Edit on Update Score (see the permission section). When the request has no sport, the gateway uses the organisation's default sport.
- TMS checks, in this order:
  1. "No Event Found", "Event Category Not Found", "Stage Not Found" or "Match Not Found" (404).
  2. The sides must belong to the match. A recorded walkover blocks new sets: "Match Already Walkover Reset First" (400). A side whose replacement payment is pending: "Participant payment is pending" (400).
  3. A later stage that depends on this stage is in progress or completed: "Cannot update score: a dependent stage is already in progress or completed." (400).
  4. Knockout: a match that already has a winner cannot be changed once the next match of the winner or loser is in progress or scored: "Next round already scored" (403).
  5. The sets are checked by the sport's rules; a refused score returns 403 with the rule message (see the sport guides).
- Status: a result with a winner (or a tie) sets the match to Scored; otherwise it becomes In Progress.
- Success: "Score Updated Successfully" (200).

## Update score – reset and team match refusals

- Reset of a match that has not started: "Cannot reset a match that has not started" (400).
- Reset while a participant has an active forfeit: "Reset blocked because of an active forfeit" (400).
- Reset is also refused by the dependent-stage and knockout checks above.
- Team match without a playing order: "Playing format not found". A sub-match whose lineup is not complete: "Sub-match lineup is incomplete".
- Re-scoring a team match whose golden match has already started: "Please reset golden match first."
- A save that changes nothing: "No scoring changes computed" (400).

## Update score – rule messages for Padel and Tennis

- Some Padel and Tennis refusals are shown in the admin app's own wording: "Tie-break is required for this set.", "Invalid tie-break score in set {{set_number}}.", "The tie-break is not complete. Win by the configured margin.", "Invalid super tie-break score in the last set.", "The submitted set scores do not match the configured number of sets." and "The match is not concluded. Complete the required sets before saving."
- Others appear as the server sends them, for example "Extra set 3 provided after match already decided", "Super tie-break can only be played when the sets are level in set 3" and "Under Special Rule, all configured sets must be completed before saving the match. Set 2 was not played."
- A tied set at or above the set target with tie-break off is stopped in the admin app before saving: "This score is not valid for your Game Play Settings. Sets are first to {{setPoint}} games (best of {{setCount}}), win by {{winBy}}, and tie-break is off. {{scoreA}}-{{scoreB}} cannot be a completed set."

## Update score – who may score (gateway permission check)

- First the gateway checks Edit on Update Score for the event (users with LMC, admin-equivalent, permission also pass); without it: "Access Denied" (403).
- Allowed without further checks: the main admin and users with the LMC permission.
- Requests that do not come from the admin app skip the extra check.
- Otherwise the user needs the "Event Access" scoring permission for the whole event, or Edit on Update Score for the match itself (for a team sub-match, the permission on the parent team match also counts). Without it: "Access Denied" (403).
- For a live score of a team sub-match, a parent match ID of 0 is refused: "Parent Match Id Cannot Be Zero" (400). A live score that is saved is also pushed to live score screens.
- A refusal from the scoring service is passed back unchanged, so the admin app can show the exact rule message.

## Update matches (PUT match/v1/matches)

- Gateway: needs Update Score and Edit.
- The admin app uses this call for the manual scoring button: starting sends the status IN_PROGRESS, stopping sends NOT_STARTED. If it fails the app shows the server message or "Failed to update manual scoring".
- TMS saves the status that is sent. It does not check whether the match is already scored; that lock exists only in the admin app. Moving a match to another round needs its group ID.
- The call returns true on success; it has no success message.

## Match status: stream, publish and table (PATCH match/v1/update_match_status)

- Gateway: needs Update Stream and Edit.
- Event not found: "Event Not Found" (400).
- The server does not refuse turning streaming off for a match that has started; that lock is in the admin app.
- Bulk change (PATCH match/v1/matches/streaming): at most 100 matches per request, all from the event the permission was checked for (otherwise "Access Denied"). Matches already in the requested state are skipped; each match is reported on its own.
- Show on table true or false: the match is updated and "Match Updated Successfully" (200) is returned.
- Publish: the streaming publish is handled, and the streaming service is used (the streaming service is not in the repos).
- Live stream off: "Match Updated Successfully" (200).
- Video active or image change with no video: "Video Not Found" (404).
- Reset: the live stream flag is cleared and the video is deleted in the streaming service.

## Sub-matches (POST match/v1/sub-matches)

- Gateway: needs Edit and Update Score.
- Parent match not found, or not a team match: refused with an internal error (500); the server log reads "Parent match {id} not found or is not a team match".
- Group, stage or event category not found: also an internal error (500).
- With several tables, a sub-match's playing table must be one of the parent match's tables (otherwise an internal error). With one table, that table is set automatically; an unscheduled match has its table cleared.
- Golden parent matches are handled separately. Success returns the saved sub-matches.

## Reverse the participants order (POST match/v1/reverse-participants-order)

- Match not found: "Match Not Found" (404).
- The sub-matches of the parent team match are reversed so that the sides swap places. The new display order is returned.

## Fetch the team lineup (POST team/v1/fetch_lineup)

- Gateway: needs a login.
- Lineup for a team and match that already exists: returned with "Team Match Participants Fetched" (200).
- No lineup yet and the team has no members: "No Team Participants For Auto Creation" (404).
- No lineup yet and the team has members: the lineup is created: "Team Match Participants Created" (201).
- Nothing found: "No Participants Found" (404). Error: "Error fetching team match participants" (500).

## Update the lineup player status (PUT team/v1/update_lineup)

- Gateway: needs a login.
- Reset to the team default: the lineup goes back to the team default.
- Participant not found: "Participant Not Found" (404). A status that is not valid: "Participant not found or invalid status description" (404).
- Success: "Participant Status Updated" (200). Error: "Error updating participant status" (500).

## Event official notes (GET and PUT planner/v1/event_official_notes)

- GET: needs a login; the planner returns the notes of the event.
- PUT: needs Update Score and Edit. The notes are added to the match; success returns "Success" (200), which the admin app shows.
- No notes, or a note type other than umpire or referee: "Invalid Input" (400). An error: "Internal Server Error" (500).
- The 500-character limit per note is checked only in the admin app.

## Update event participant (PUT register/v1/update_event_participant)

- The gateway passes the request to the registration update. The rules of that step are not traced in this pass.

## Players list for lineups (GET user/v1/list_all_players)

- Used by the lineup and the player pickers. The rules of the player list are not traced in this pass.

## Frequently asked questions about the scoring APIs

**Why does the server say "Match Already Walkover Reset First"?** The match has a recorded walkover. Clear the walkover (W/O, **Clear Walkover**) before saving set scores.

**Why does the server say "Next round already scored"?** The knockout result was already carried forward and the next match is in progress or scored. Reset that next match first.

**Why does the server say "Cannot update score: a dependent stage is already in progress or completed."?** A later stage that takes its players from this stage has started. Scores of this stage can no longer be changed or reset.

**Why does a reset fail with "Cannot reset a match that has not started"?** The match has no score yet, so there is nothing to reset.
