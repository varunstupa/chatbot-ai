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

Each section gives the gateway step, the TMS checks in order, and the message shown. Messages are the English text the gateway returns. Where a call needs a permission, it is named; a missing permission gives "Access Denied" (403) and an expired login "Unauthorized Access" (401).

## Create group (POST group/v1/create_group)

- Gateway: needs a login only.
- TMS: the group name is required: "Group Name Required" (400).
- Success: "Group Created" (201).

## Read groups (GET group/v1/get_groups, get_groups_with_benched, get_group_participants)

- All three need a login only.
- get_groups: returns the groups of the stage with filters (name, status, search, ranking sort).
- get_groups_with_benched: stage not found: "Stage Not Found" (404). Benched participants are left out of each group list and returned in a separate benched list. Success: "Group Fetched" (200).
- get_group_participants: returns the participants of a group (or one participant). Success: "Group Participants Fetched" (200).

## Update group participants (POST group/v1/upsert_group_participants)

- Needs a login only. Group not found: "Group Not Found" (404).
- Success: "Participant Updated" (200).

## Group metadata (create, get, update and delete groups_metadata)

- The screen calls these four endpoints, but no gateway or TMS route with these paths exists on the server branches. The server cannot answer them as they stand. This is reported as a finding and is not described as working.

## Match formats for the round robin logics (GET group/v1/get_dummy_group_matches)

- Gateway: needs a login. It reads the group sizes as a comma-separated list of whole numbers; a value that is not a number fails at the gateway before the TMS is asked.
- Logic type not circular or Berger: "Invalid Logic Type Circular Berger" (400).
- A group size below two: "Invalid Group Strengths Format" (400).
- Success: "Match Formats Generated Successfully" (200).

## Group matches (GET group/v1/get_group_matches)

- Gateway: needs a login. The event ID is taken from the query or the event-id header; it is required only when the organiser details are asked for: "Event Id Required" (400). With the organiser details, the gateway adds who may score each match.
- Needs a stage ID: "Stage Id Required" (400).
- An invalid search combination is refused with code 400 (that message has no English translation yet). Unreadable highlight filters: "Invalid match filters" (400).
- A stage without groups returns "Group Matches Fetched" with an empty list.
- Success: "Group Matches Fetched" (200), with the groups, rounds and matches.

## Draft group fixture (POST fixture/v1/draft_group_fixture)

- Needs Edit on Fixture Access. An empty draft: "Invalid Json Payload" (400).
- When matches are to be created: refused with "Stage Update Not Allowed" (400) when a dependent stage is in progress or completed.
- Benched participants are left out of the draft. Padel: the Padel match configuration is applied.
- Groups that are kept are renamed or re-ordered when their name or order changed. Groups missing from the draft are deleted. The matches of a group are rebuilt when matches are created.
- A custom match format with no format: "Custom Match Format Required" (400); no format for a group size: "No custom format defined for group size: {group_size}" (400).
- The stage becomes Fixture Created (draft only) or Group Matches Created (with matches). With matches and automatic fixture publishing on the event, the stage is published.
- With matches, dependent stages are rebuilt and player umpires are auto-assigned; the gateway then syncs the umpire match permissions.
- Success: "Groups Updated Successfully" (draft only) or "Matches Updated Successfully" (with matches), code 200.

## Stage participants (GET and POST stage/v1/get_stage_participants, upsert_stage_participants)

- Both need a login only.
- get_stage_participants: Success: "Stage Participants Fetched" (200).
- upsert_stage_participants: stage not found: "Stage Not Found" (400). Refused with "Participants Update Not Allowed" (400) when this stage or a dependent stage is in progress or completed (unless the stage allows adding participants). Category not found: "Event Category Not Found" (404).
- Success: "Participant Updated" (200).

## Bench participants (POST stage/v1/bench_stage_participant)

- Needs Edit on Edit Stage. Stage not found: "Stage Not Found" (404).
- Refused when scoring has started in the stage: "Cannot bench players: scoring has already started for this stage." (400).
- Participants not in the stage: "Participants not found in this stage: {participant_ids}" (404).
- Participants already benched: "Participants already benched in this stage: {participant_ids}" (400).
- Benched participants keep their seed, saved so an unbench can restore it. Elite players lose the elite flag; excluded players keep it.
- The draw is not re-created here: the stage is marked as needing a redraw, and the fixture must be generated again before drafting.
- Success: "{count} player(s) benched successfully." (200).

## Unbench participants (POST stage/v1/unbench_stage_participant)

- Needs Edit on Edit Stage. Stage not found: "Stage Not Found" (404). Refused when scoring has started: "Cannot un-bench players: scoring has already started for this stage." (400).
- A group ID that is not in this stage: "Group Not Found" (404). A participant who is not benched here is imported from the category; one not in the event category: "Participant(s) {participant_ids} are not in this event category" (400).
- The saved seed is restored when it is free. With a group ID, all the players go into that group.
- Group stage: no redraw is needed. Knockout: a redraw stays needed while players are still benched or unseeded.
- Success: "{count} player(s) successfully imported and fixture re-drawn." (200).

## List benched participants (GET stage/v1/get_benched_stage_participants)

- Send either the stage ID or the event category ID; with neither: "Provide either stage_id or event_category_id." (400). Success: "Benched players fetched successfully." (200).

## Swap two participants (POST stage/v1/swap_stage_participants)

- Needs Edit on Edit Stage. Same participant on both sides, or a completed stage: "Swap Not Allowed" (400). Stage not found: "Stage Not Found" (400).
- Neither participant is in the stage: "Stage Participant Not Found" (400).
- Either participant has a match in progress or scored in this stage: "Swap Not Allowed" (400).
- Both in the stage: they exchange seeds and group, round and match places; for teams the line-ups of the affected matches are cleared.
- Only one in the stage: the other (who must belong to the same event category, otherwise "Stage Participant Not Found") takes that place and the first leaves the stage.
- Success: "Fixture Updated" (200). The screen shows its own text for the result.

## Seeding (POST fixture/v1/upsert_stage_participants_seeds and _with_auto_seeding)

- Both need Edit on Fixture Access. Stage not found: "Stage Not Found" (404). Seed not a whole number: "Stage Seed Must Be An Integer" (400).
- Auto seeding route only: the first seed must be 1 ("Stage Seed Must Start With 1"), seeds must count up without gaps ("Stage Seed Must Be Incremental And Continuous"), and the number of seeded entries must be a power of two ("Enter A Valid Number Of Participants"), all 400.
- A seed used twice, or a seed held by a benched player: "Duplicate Seed" (400).
- The other participants get the next free seeds. The auto seeding route marks the stage as partially placed and, for a knockout, re-creates the draw.
- Success: "Seed Update Success" (200).

## Reset seeding (POST stage/v1/reset_stage_seeding)

- Needs a login only. Stage not found: "Stage Not Found" (404). No stage configuration: "Configuration Missing" (403).
- Success: "Seeding Updated" (200).

## Shuffle knockout participants (POST stage/v1/{stage_id}/participants/shuffle)

- Needs Edit on Edit Stage. Stage not found: "Stage Not Found" (404).
- Only for knockout stages: "Shuffle is only available for knockout stages." (400).
- Stage configuration missing: "Stage Configuration Missing" (400).
- Refused when scoring has started: "Cannot shuffle participants: scoring has already started for this stage." (400).
- Otherwise the draw is re-created with the separation rules, the seeds are saved, and the new fixture is returned.

## Elite and excluded players (PATCH registration/v1/manage_elite_excluded_players)

- The gateway passes the request to the registration service rules for elite and excluded players. The rules of that step are not traced in this pass.
