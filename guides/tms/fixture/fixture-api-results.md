---
doc_id: tms.fixture.api-results
title: Backend logic of the results, standings, head-to-head, playing order and rule settings APIs
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - results api
  - standings api
  - head to head api
  - head to head rules
  - group matches api
  - playing order api
  - playing order rules
  - rule settings api
  - point system rules
  - game play settings rules
  - update rule settings backend
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What does the backend check when I open the group matches?
  - What does the head-to-head stats call return?
  - Why does the point system save say "Rule Settings Invalid Request"?
  - What does the backend say when a match has no playing order?
  - Who can change the game play settings in the backend?
backend_sources:
  - gateway/src/routers/group_router.py (get_group_matches)
  - gateway/src/routers/scoring_router.py (get_head_to_head_stats)
  - gateway/src/routers/round_router.py (get_rounds)
  - gateway/src/routers/playing_order_router.py (get_team_playing_order, get_team_playing_order_with_matches)
  - gateway/src/routers/rule_setting_router.py (get_rule_settings, update_rule_settings)
  - gateway/src/routers/ctms_router.py (get_sport_config, update_sport_config, get_tenant_info)
  - tms/src/service/rule_setting_service.py (get_rule_settings, update_rule_settings_v2)
  - tms/src/service/scoring_service.py (get_head_to_head_stats)
  - tms/src/service/playing_order_service.py (get_team_playing_order_with_matches)
source_files:
  - src/app/modules/tms/fixture-configuration/groups-stage-view/matches-standings/groups-stage-matches-standings.component.ts
  - src/app/shared/point-system/point-system.component.ts
  - src/app/shared/game-play-config/game-play-config.component.ts
  - src/app/modules/tms/fixture-configuration/fixture-popups/playing-order/playing-order.component.ts
---
# Backend logic – results, standings, head-to-head, playing order and rule settings

Each section gives the gateway step, the TMS checks in order, and the message shown. Where a call is served by the CTMS service (sport configuration and tenant information), that is said, and its rules are not traced in this pass.

## Group matches (GET group/v1/get_group_matches)

- Gateway: needs the event ID header ("event-id header is required", 400). It checks the scoring permission of the event and whether the user is a live match scorer, so the match list can show the scores the user may change.
- Needs a stage ID: "Stage Id Required" (400).
- An invalid search request is refused with code 400.
- Success: "Group Matches Fetched" (200), with the groups, the rounds and the matches.

## Rounds (GET round/v1/get_rounds)

- Returns the rounds of the event category or stage, filtered by name, status and search. Matches are not included.

## Head-to-head statistics (GET score/v1/get_head_to_head_stats)

- Event not found: "No Event Found" (404). Event category not found: "Event Category Not Found" (404).
- For singles, doubles and mixed doubles, the statistics are built from the matches between each pair of players of the group.
- For teams, the statistics are built from the team matches and their sub-matches.
- Success: "Head To Head Stats Fetched Successfully" (200).

## Playing order (GET playing_order/v1/get_team_playing_order)

- Returns the playing orders of the event, with paging and search. The team playing order with its matches is in the fixture guides (Results).

## Rule settings – read (GET rule_setting/v1/get_rule_settings)

- Gateway: needs a login. The TMS reads the rule settings for the tenant (global), the event, the category or the stage.
- A request that is neither global nor for an event: "Unauthorized Access" (401).
- Success: "Rule Settings Get" (200) with the settings.

## Rule settings – save (PUT rule_setting/v1/update_rule_settings)

- Gateway: needs Edit on Game Play Settings.
- Global settings (for the tenant): "Rule Settings Updated" (200). A setting locked at the global level is refused with code 400 and a message that has no English translation yet.
- Event category settings: saved for the category, with "Rule Settings Updated" (200). A setting locked by the global configuration is refused with code 400 and the same untranslated message.
- Event level settings: saved for the event, with "Rule Settings Updated" (200).
- A request that matches none of these: "Rule Settings Invalid Request" (400).

## Sport configuration and tenant information (GET and PUT ctms/v1/sport/config, GET ctms/v1/tenant/info)

- These calls are served by the CTMS service (the sport and tenant catalogue), not by the TMS. The rules of those calls are not traced in this pass.
