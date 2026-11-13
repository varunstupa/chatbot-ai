---
doc_id: tms.awards.api
title: Backend logic of the Awards and Standings APIs – toggles, global and event awards, sync, standings and publishing
routes:
  - tms/awards/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - awards api
  - awards backend
  - standings api
  - generate standings rules
  - publish standings rules
  - cumulative standings api
  - sync awards rules
  - why was an award skipped
  - award toggle api
  - award name already exists
  - weightage backend
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What does the backend check before it generates the stage standing?
  - Why can I not publish the standings?
  - Why was an award skipped when I synced it?
  - What does "Cumulative Standings Already Generated" mean?
  - What does the backend do when I turn on the Best Player award?
  - What does the backend refuse for an Order of Merit weightage?
backend_sources:
  - gateway/src/routers/awards_router.py (awards/v1 endpoints)
  - gateway/src/routers/award_standing_config_router.py (standings/v1 config)
  - gateway/src/routers/standings_router.py (standings/v1 endpoints)
  - tms/src/router/award_router.py
  - tms/src/router/standings_router.py
  - tms/src/service/award_service.py
  - tms/src/service/standings_service.py
  - tms/src/service/award_calculators.py
source_files:
  - src/app/modules/tms/award-standings/award-standings.component.ts
  - src/app/modules/tms/award-standings/shared/services/awards-event-api.service.ts
  - src/app/modules/tms/award-standings/shared/services/awards-global-api.service.ts
  - src/app/core/constants/api-constant.ts
---
# Backend logic – Awards and Standings APIs

Each section gives the gateway step, the checks in order, and the message the server sends. The gateway checks the login and the permission before it forwards each call: every change needs **Edit** on the Awards and Standings feature; the event award lists and positions need **Read**; the award type flags and the global award list need only the login.

## Award type toggles (GET awards/v1/config, PUT awards/v1/toggle)

- Read: returns whether Best Player and Order of Merit are enabled for the tenant.
- Save: the new flags are merged with the saved ones, so a flag that is not sent stays as it was. Success: code 200 with the merged flags.

## Global awards (GET, POST, DELETE awards/v1/global)

- List: filtered by award type. An unknown type: "Invalid award_type" (400).
- Create or update: an award name already used by another global award of the same type: "Award name '{name}' already exists" (409). Updating an award that does not exist: "Award not found" (404).
- Delete: an award that does not exist: "Award not found" (404).

## Event awards (GET awards/v1/event/awards, POST and DELETE awards/v1/event/awards)

- List: the awards of the event (synced and event-only), filtered by type. Unknown type: "Invalid award_type" (400).
- Create or update:
  - Order of Merit with the weightage method, where a category's win, loss and participation weights add up to more than 100: "Weightage for category '{category_name}' must not exceed 100% (got {total_weight}%)" (400);
  - new award only: the type is disabled at federation level: "This award type is disabled at federation level" (403); the name is used by another award of the event: "Award name '{name}' already exists in this event" (409);
  - update: the award does not exist in this event: "Award not found" (404). The name and type checks are skipped on update.
- The form itself is also checked: a name, at least one category, for Best Player a position limit of 1 or more with exactly one points entry for each position up to the limit, and for Order of Merit the per-category points. Points are whole numbers of 0 or more; a weight is 0 to 100.
- Delete: "Award not found" (404). The award is removed, but a standing it already published is not removed (see the operations API guide).

## Syncable global awards (GET awards/v1/event/syncable)

- Lists the global awards that can be added to the event (the Sync Awards list). Only global awards published at federation level are listed, each marked when it is already synced to this event. Unknown type: "Invalid award_type" (400).

## Sync awards (POST awards/v1/event/sync)

- The type must be enabled at federation level: "This award type is disabled at federation level" (403).
- Each selected global award is checked in turn. It is skipped when:
  - it does not exist ("not_found");
  - it is already synced to this event ("already_synced");
  - it is not published at federation level ("not_published").
- Each award that passes is copied to the event, keeping its points and a link to the global award. Later changes to the global award are not copied again.
- Success: code 200 with the number of awards synced, the synced awards and the skipped awards with their reasons.

## Generate the event standings (POST awards/v1/event/standings/generate)

- Award not found: "Award not found" (404). Unknown type: "Invalid award_type" (400).
- None of the award's categories is in the event: "None of the award's categories exist in this event. Please update the award categories or sync a matching award." (400). Categories that are missing are skipped when at least one exists.
- Every player of the active entries of those categories is counted. In doubles and team entries each member gets the entry's final standing; for team categories only the sub matches the player played count as wins and losses.
- The points are worked out with the award's calculator (see the award types guide), sorted with the tie-breakers, numbered 1, 2, 3 … without shared positions, and saved as a snapshot. The publish state of an earlier snapshot is kept.
- Success: code 200 with the standing.

## Read the event standings (GET awards/v1/event/standings)

- Award not found: "Award not found" (404). No standing generated: "Standings not generated yet" (404).

## Publish the standings (PUT awards/v1/event/standings/publish)

- Award not found: "Award not found" (404).
- Publish requires a generated standing: "Generate standings before publishing" (409).
- Publish requires finalized results in the mapped categories: "Cannot publish: mapped categories have no finalized results" (409). A category has finalized results when at least one participant has a final standing.
- Unpublish is always allowed. Success: code 200 with the award and the new state.

## Publish all (PUT awards/v1/event/standings/publish-all)

- Unknown type: "Invalid award_type" (400).
- Only awards with generated positions are touched. When publishing, an award is skipped unless one of its categories has a final standing. Unpublish applies to all of them.
- Success: code 200 with the number of awards changed and a result per award; skipped awards are not reported as an error.

## Category use check (GET awards/v1/event/category-usage)

- Tells whether an event category is used by any award, so that the screen can warn before a category is deleted.

## Published standings (GET awards/v1/event/published-standings)

- Unknown type: "Invalid award_type" (400). No published standing: "Published standings not found" (404).

## Stage standings (POST standings/v1/generate)

- Stage not found: "Stage Not Found" (404).
- The stage must be completed: "Cant Generate Standings" (400).
- The standing already exists: "Standings Already Generated" (400).
- A group stage without group participants: "No Group Participants Found" (404). A knockout stage whose matches cannot be read: "Error Fetching Knockout Matches" (404).
- Success: "Stage Standings Generated" (200).

## Swap stage positions (PUT standings/v1/swap)

- A participant not in the stage: "Stage Participant Not Found" (404). A swap that is not allowed: "Swap Not Allowed" (400).
- Success: "Standings Updated" (200).

## Stage priority and cumulative order (PUT and GET standings/v1/upsert_priority, get_priority, reset_priority)

- Event or category not found: "No Event Found" (404), "No Category Found" (404).
- Save: "Stage Priority Updated" (200). Read with no order saved: "Stage Priority Not Found" (404). Reset: "Stage Priority Reset" (200).

## Award settings and prize money (PUT and GET standings/v1/upsert_rewards, get_rewards, PUT reset_rewards)

- Save: "Award Settings Updated" (200). Read with nothing saved: "No Award Settings Found" (404). Reset clears the prize table and switches prize money off: "Award Settings Reset" (200).
- Event or category not found: "No Event Found" or "No Category Found" (404).
- Reading the settings needs only the login.

## Cumulative standings (POST standings/v1/cumulative_generate, GET cumulative_status)

- Checks in order: event and category ("No Event Found", "No Category Found", 404); a saved stage priority ("Stage Priority Not Found", 404); no participant already has a final position ("Cumulative Standings Already Generated", 400); stage results exist ("No Stage Results Found", 404); every chosen stage has a generated standing ("Standings for stage(s) {stage_ids} have not been generated yet. Please generate them or remove them from cumulative standings priority and then regenerate.", 400).
- The first stage in priority gives its participants their stage positions. Participants who appear only in later stages are placed after them, in their stage order; equal stage positions share a final position.
- Success: "Cumulative Standings Generated" (200). The status read ("Cumulative standings status fetched.") is used inside the server only; the gateway has no admin route for it.

## Calls not traced in this pass

- The cumulative swap, manual standing, stage and cumulative publish, reset, the public published-standings reads and the export are described in the operations API guide (awards-api-operations). The section categories list is not traced in this pass.
