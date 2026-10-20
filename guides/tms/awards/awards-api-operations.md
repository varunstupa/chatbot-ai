---
doc_id: tms.awards.api-operations
title: Backend logic of the standings operation APIs – publish, reset, swaps, manual standings, automatic recalculation and public reads
routes:
  - tms/awards/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - publish standings api
  - standings publish backend
  - reset standings api
  - cumulative swap api
  - manual standing api
  - automatic standings recalculation
  - public standings api
  - ott awards standings
  - standings not published
  - player standings visibility
  - ranking tie breakers backend
  - award ranking backend
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What does the backend check when a stage standing is published?
  - Why does the public participant list say "Standings Not Published"?
  - What does the backend do after a score is saved to the standings?
  - How does the backend rank Order of Merit players?
  - What does the backend refuse for a manual standing?
  - Which permission is needed to publish or reset the standings?
backend_sources:
  - gateway/src/routers/standings_router.py (publish, reset, cumulative_swap, manual_standing, swap, cumulative_generate)
  - gateway/src/routers/award_router.py (awards/v1 publish, publish-all, standings read)
  - gateway/src/routers/ott_router.py (ott/v1/awards/standings)
  - tms/src/router/standings_router.py
  - tms/src/router/award_router.py (event/published-standings)
  - tms/src/service/standings_service.py (publish_standings, reset_standings, swap_cumulative_standings, set_manual_standings, swap_stage_positions, auto_generate_and_publish_standings)
  - tms/src/service/award_service.py (_apply_tie_breakers, get_published_standings, list_published_awards)
  - tms/src/crud/config_crud.py (fetch_published_standings_for_ott, list_published_standings_summaries)
  - tms/src/service/registration_service.py (get_event_participants, call_for_standings_ott)
  - tms/src/crud/player_dashboard_crud.py (STANDING_PUBLISHED join)
  - tms/src/utils/scoring/phases/finalize.py (standings refresh after scoring)
source_files:
  - src/app/modules/tms/award-standings/award-standings.component.ts
  - src/app/core/services/common-service/common-service.service.ts
  - src/app/core/constants/api-constant.ts
---
# Backend logic – standings operation APIs

Each section gives the gateway step, the checks in order, and the message. The screen-level behaviour is in the operations guide (awards-standings-operations). Permissions: the standings routes need Edit on the awards-standings feature; the event award reads need Read; the public route needs no login.

## Publish a stage or cumulative standing (PUT standings/v1/publish)

- Query: event, category and, for a stage, the stage. Body: publish (true or false).
- Checks: the event must exist ("No Event Found", 404); the category must exist ("No Category Found", 404). When a stage is given, the stage must exist ("Stage Not Found", 404). The standing itself is not checked here.
- When publishing a stage, a notice that the category's standings were generated is sent to the public side (only when the request carries the tenant). An error in the notice is logged and does not stop the publish.
- The publish state is saved with the prize money setting of the category. A stage publish is saved on the stage; a cumulative (category) publish is saved on the category.
- Success: "Standings Published" (200). Unexpected error: the error text (500).

## Reset standings (PUT standings/v1/reset)

- Query: event, category, optional stage, and the flag "only cumulative".
- With a stage: only that stage's standings are cleared (unless only cumulative is set).
- Without a stage, or with only cumulative: the cumulative positions of the category are cleared. Without a stage the stage standings are cleared as well.
- Success: "Standings Reset" (200). Unexpected error: the error text (500).

## Cumulative swap (PUT standings/v1/cumulative_swap)

- Body: swaps, each with an event participant ID and a new position.
- Every participant ID must belong to the category: otherwise "Event Participant Not Found" (404).
- The positions of the listed participants are exchanged.
- Success: "Cumulative Standings Updated" (200).

## Manual standing (PUT standings/v1/manual_standing)

- Body: standings, each with an event participant ID and a standing of at least 1. The schema refuses a standing below 1 and a participant listed twice.
- Every participant must belong to the category: otherwise "Event Participant Not Found" (404).
- The listed participants get the given cumulative standings. Other participants are not moved by this call.
- Success: "Manual Standings Updated" (200).
- The change is overwritten by the next automatic recalculation after a finalized score (see below).

## Stage swap (PUT standings/v1/swap)

- Body: swaps with stage participant IDs and new positions.
- A participant not found in the stage: "Stage Participant Not Found" (404).
- Participants from more than one group: "Swap Not Allowed" (400).
- Success: "Standings Updated" (200).

## Automatic recalculation after a finalized score

- Runs at the end of every finalized score in the category (the shared finishing step).
- Steps, in order:
  1. The stage standings and the cumulative positions of the category are cleared (the reset with no stage).
  2. Each completed stage is regenerated from its results, and its standing is published automatically.
  3. For a predefined fixture where every stage is complete: the cumulative priority is checked (and repaired when the stages changed), the cumulative standing is generated and published.
- A stage that cannot be generated (for example no rule settings) is logged and skipped; the other stages still regenerate.
- Effect: manual cumulative positions and cumulative swaps are cleared by the next finalized score. Manual stage swaps are not guaranteed to survive a regeneration; check them after each score.

## Ranking of award players (tie-breakers)

- The award standing is sorted by total points, highest first.
- Players with equal points are then compared by the visible tie-breakers, in priority order (the first tie-breaker is the first category of the award).
- For each tie-breaker, the value of a player in that category is:
  - WINS – matches won;
  - WIN_RATIO – matches won divided by matches played (zero when none were played);
  - WIN_LOSS – matches won minus matches lost.
- A player with no record in the category gets zero for that tie-breaker, so is neither helped nor penalised.

## Published award list and standings (OTT: GET ott/v1/awards/standings, TMS GET awards/v1/event/published-standings)

- The OTT route needs no login and its answer is cached for 60 seconds.
- Without an award ID: the list of published awards of the type, with their names and row counts. An award is listed only when its snapshot has publish set to true.
- With an award ID: the paged rows of that award, filtered by name when a search is sent. An unpublished or missing award: "Published standings not found" (404).
- An unknown award type: "Invalid award_type" (400).

## Public participant list gate (GET register/v1/get_event_participants with the OTT flag)

- When the caller asks for the public standings, the category's publish toggle is read first.
- Not published: "Standings Not Published" (200) with no participants and a count of 0.
- The listing reads the category-level publish toggle. A stage-level publish is stored on the stage, so it does not open this listing by itself.

## Player dashboards

- The player dashboard queries join the category's publish toggle, so a player's standing is shown only when the category is published.

## Export

- The export of the standings uses the fixtures export job on the worker (the gateway route worker/export/fixtures). The worker code is not in the repos, so the file rules are not described here.

## Calls not traced in this pass

- The publish-all and the event standings publish routes for awards are described in the awards API guide. The worker export contents and the cumulative priority repair details are not traced beyond the description above.
