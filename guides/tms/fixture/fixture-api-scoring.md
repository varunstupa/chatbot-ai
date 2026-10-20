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
  - Why does the server say "Match Data Not Reset"?
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
---
# Backend logic – scoring APIs

Each section gives the gateway step, the TMS checks in order, and the message shown. The gateway checks the login and the permission before it forwards each call. Scoring calls that need the event ID check the event ID header first.

## Update score (PUT score/v1/update_score)

- Gateway: needs the event ID header ("event-id header is required", 400) and a score payload. Needs Edit on Update Score. A live match scorer or a user with the resource permission can also score.
- TMS checks, in this order:
  1. Event not found, or event category not found: "No Event Found" (404).
  2. Stage not found: "Stage Not Found" (404). Match not found: "Match Not Found" (404).
  3. A match that already has a winner in a knockout stage must pass the progression check; if a later round has already used the result, the change is refused with that check's message.
  4. A match that was walked over cannot take new sets until the walkover is reset: "Match Already Walkover Reset First" (422).
  5. The sets are checked by the game rules of the sport. A rejected score is refused with code 403 and the rule message from the calculator.
  6. A reset is refused with "Match Data Not Reset" (403) when the reset is blocked.
- The match is set to IN_PROGRESS while the score is saved. A reset sets it back to NOT_STARTED.
- Success: "Score Updated" (200). A winner is stored with the calculated score.

## Update matches (PUT match/v1/matches)

- Gateway: needs Update Score and Edit.
- TMS: a score publish setting is checked against the match data. Moving a match to another round needs its group ID.
- The success text of this call is not traced in this pass.

## Match status: stream, publish and table (PATCH match/v1/update_match_status)

- Gateway: needs Update Stream and Edit.
- Event not found: "Event Not Found" (400).
- Show on table true or false: the match is updated and "Match Updated Successfully" (200) is returned.
- Publish: the streaming publish is handled, and the streaming service is used (the streaming service is not in the repos).
- Live stream off: "Match Updated Successfully" (200).
- Video active or image change with no video: "Video Not Found" (404).
- Reset: the live stream flag is cleared and the video is deleted in the streaming service.

## Sub-matches (POST match/v1/sub-matches)

- Gateway: needs Edit and Update Score.
- Parent match not found, or not a team match: refused with the message "Parent match {id} not found or is not a team match" (raised as an error).
- Group not found: "Group Not Found" (raised). Stage not found: "Stage Not Found". Category not found: "Event Category Not Found".
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
- PUT: needs Update Score and Edit. The planner saves the notes. The planner rules are not traced in this pass.

## Update event participant (PUT register/v1/update_event_participant)

- The gateway passes the request to the registration update. The rules of that step are not traced in this pass.

## Players list for lineups (GET user/v1/list_all_players)

- Used by the lineup and the player pickers. The rules of the player list are not traced in this pass.
