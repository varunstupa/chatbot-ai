---
doc_id: tms.fixture.api-group
title: Backend logic of the group stage APIs – groups, participants, draft, bench, swap and seeding
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - swap played participants
  - swap rules backend
  - swap after match played
  - group api
  - create group rules
  - group participants api
  - draft group fixture rules
  - bench participant rules
  - unbench participant rules
  - swap participants rules
  - seeding api
  - seed rules
  - reset seeding rules
  - match formats api
  - circular berger format rules
  - elite excluded backend
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What does the backend check when I draft the groups?
  - Why can I not bench a player after scoring has started?
  - What does "Participants Already Benched" mean?
  - What does the backend check when I swap two participants?
  - What does "Duplicate Seed" mean?
  - Why does the reset seeding say "Configuration Missing"?
  - What does the backend say when the logic type is wrong?
backend_sources:
  - gateway/src/routers/group_router.py (create_group, get_groups, get_groups_with_benched, get_group_participants, upsert_group_participants, get_dummy_group_matches, get_group_matches)
  - gateway/src/routers/fixture_router.py (draft_group_fixture, upsert_stage_participants_seeds, upsert_stage_participants_seeds_with_auto_seeding)
  - gateway/src/routers/stage_router.py (get_stage_participants, upsert_stage_participants, bench_stage_participant, unbench_stage_participant, get_benched_stage_participants, swap_stage_participants, reset_stage_seeding, shuffle_stage_participants)
  - gateway/src/routers/registration_router.py (manage_elite_excluded_players)
  - tms/src/router/stage_router.py (bench, unbench, get benched)
  - tms/src/service/stage_service.py (bench_player, unbench_player, upsert_stage_participants, swap_stage_participants, reset_stage_seeding, get_benched_players)
  - tms/src/service/fixture_service.py (draft_group_fixture, upsert_stage_participants_seeds_with_auto_seeding)
  - tms/src/service/match_service.py (get_match_formats)
source_files:
  - src/app/modules/tms/fixture-configuration/groups-stage-view/groups-stage-view.component.ts
  - src/app/modules/tms/fixture-configuration/fixture-popups/swap-player/swap-player.component.ts
  - src/app/core/services/fixture-service/fixture.service.ts
---
# Backend logic – group stage APIs

Each section gives the gateway step, the TMS checks in order, and the message shown. The gateway checks the login and the permission (Edit on Fixture Access or Edit Stage) before it forwards each call.

## Create group (POST group/v1/create_group)

- Gateway: needs a login only.
- TMS: the group name is required: "Group Name Required" (400).
- Success: "Group Created" (201). The response code is 201.

## Read groups (GET group/v1/get_groups, get_groups_with_benched, get_group_participants)

- get_groups: returns the groups of the stage with filters (name, status, search, ranking sort). Success: "Group Fetched" (200).
- get_groups_with_benched: stage not found: "Stage Not Found" (404). Benched participants are left out of the group lists. Success: "Group Fetched" (200).
- get_group_participants: returns the participants of a group (or one participant). Success: "Group Participants Fetched" (200).

## Update group participants (POST group/v1/upsert_group_participants)

- Group not found: "Group Not Found" (404).
- Success: "Participant Updated" (200).

## Group metadata (create, get, update and delete groups_metadata)

- The screen calls these four endpoints, but no gateway or TMS route with these paths exists in the repos. The server cannot answer them from the repos as they stand. This is reported as a finding and is not described as working.

## Match formats for the round robin logics (GET group/v1/get_dummy_group_matches)

- The gateway passes the group strengths and the logic type to the TMS (dummy_match_formats).
- Strengths in the wrong format: "Invalid Group Strengths Format" (400).
- Logic type not circular or Berger: "Invalid Logic Type Circular Berger" (400).
- A group size below two is refused with "Invalid Group Strengths Format" (400).
- Success: "Match Formats Generated Successfully" (200).

## Group matches (GET group/v1/get_group_matches)

- Needs a stage ID: "Stage Id Required" (400). An invalid search combination is refused with code 400 (the message has no English translation yet).
- Success: "Group Matches Fetched" (200).
- The response includes the groups, the rounds and the matches with their results. Where the rule settings allow it, the score details are added.

## Draft group fixture (POST fixture/v1/draft_group_fixture)

- Needs Edit on Fixture Access. Gateway: the umpire match permissions are synced after a successful draft when the event has umpire assignments.
- When matches are to be created: refused with "Stage Update Not Allowed" (400) when a dependent stage is in progress or completed.
- Padel: the Padel match configuration is applied.
- The group participants are cleared and set again from the draft. Groups that are kept are renamed or re-ordered when their name or order changed.
- Existing matches of a group are removed when the matches are re-created.
- Success: "Groups Updated Successfully" (200), and "Matches Updated Successfully" when matches are created.

## Stage participants (GET and POST stage/v1/get_stage_participants, upsert_stage_participants)

- get_stage_participants: returns the participants of the stage. Success: "Stage Participants Fetched" (200).
- upsert_stage_participants: stage not found: "Stage Not Found" (400). Refused with "Participants Update Not Allowed" (400) when the stage does not allow changes. Category not found: "Event Category Not Found" (404).
- Success: "Participant Updated" (200).

## Bench participants (POST stage/v1/bench_stage_participant)

- Stage not found: "Stage Not Found" (404).
- Refused when scoring has started in the stage: "Cannot bench players: scoring has already started for this stage." (400).
- Participants not in the stage: "Participants not found in this stage: {participant_ids}" (400).
- Participants already benched: "Participants already benched in this stage: {participant_ids}" (400).
- Benched participants keep their seed in their saved details, so an unbench can restore it. Elite and excluded players are handled as well.
- The draw is re-created once after all the players are benched.
- Success: "{count} player(s) benched successfully." If the re-draw fails: "Players benched but fixture re-draw failed: {failure_detail}".

## Unbench participants (POST stage/v1/unbench_stage_participant)

- Stage not found: "Stage Not Found" (404). Refused when scoring has started: "Cannot un-bench players: scoring has already started for this stage." (400).
- A group ID that does not exist: "Group Not Found" (404). Participants not in the event category: "Participant(s) {participant_ids} are not in this event category" (400).
- The saved seed is restored when it is free. Groups are set from the group ID when one is sent.
- The success response of this call is not traced in this pass.

## List benched participants (GET stage/v1/get_benched_stage_participants)

- Send either the stage ID or the event category ID. Success: "Benched players fetched successfully." (200).

## Swap two participants (POST stage/v1/swap_stage_participants)

- Needs Edit on Edit Stage. Same participant on both sides: "Swap Not Allowed" (400).
- Neither participant is in the stage: "Stage Participant Not Found" (400).
- Refused with "Swap Not Allowed" (400) when either participant has already played a match in this stage.
- Success: "Fixture Updated" (200). The screen shows its own text for the swap result.

## Seeding (POST fixture/v1/upsert_stage_participants_seeds and _with_auto_seeding)

- The plain route hands the request to the auto seeding route.
- Stage not found: "Stage Not Found" (404).
- Seed not a whole number: "Stage Seed Must Be An Integer" (400).
- The first seed must be 1: "Stage Seed Must Start With 1" (400). Seeds must count up without gaps: "Stage Seed Must Be Incremental And Continuous" (400).
- The participant count must be a power of two (2, 4, 8 and so on): "Enter A Valid Number Of Participants" (400).
- A seed used twice: "Duplicate Seed" (400).
- Success: "Seed Update Success" (200).

## Reset seeding (POST stage/v1/reset_stage_seeding)

- Stage not found: "Stage Not Found" (404). No stage configuration: "Configuration Missing" (403).
- Success: "Seeding Updated" (200).

## Shuffle knockout participants (POST stage/v1/{stage_id}/participants/shuffle)

- Only for knockout stages: "Shuffle is only available for knockout stages." (400).
- Stage configuration missing: "Stage Configuration Missing" (400).
- Refused when scoring has started. This message has no English translation yet, so the screen may show the key.
- Otherwise the draw is re-created with the separation rules, the seeds are saved, and the new fixture is returned.

## Elite and excluded players (PATCH registration/v1/manage_elite_excluded_players)

- The gateway passes the request to the registration service rules for elite and excluded players. The rules of that step are not traced in this pass.
