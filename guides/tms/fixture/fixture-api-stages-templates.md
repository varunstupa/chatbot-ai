---
doc_id: tms.fixture.api-stages-templates
title: Backend logic of the stage, template, generate, delete and replace APIs
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - can I delete a stage
  - delete stage rules
  - stage delete backend check
  - stage api
  - create stage rules
  - update stage rules
  - stage configuration api
  - apply to all stages rules
  - create fixture from template rules
  - delete fixture template rules
  - generate fixtures rules
  - generate fixtures for category rules
  - delete fixtures rules
  - replace participant rules
  - previous stages summary
  - why can I not delete the stage
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What does the backend check when I create a stage?
  - Why does the update say "Stage Update Not Allowed"?
  - What does "Position Match Not Allowed" mean in the backend?
  - What does generate fixtures check before it runs?
  - What happens when I delete the fixtures of a stage?
  - Why does replace say "Replace is only allowed in the first stage"?
backend_sources:
  - gateway/src/routers/stage_router.py (create_stage, update_stage, set_stage_configuration, apply_to_all_stages, create_fixture_from_template, delete_fixture_template, get_stages, get_previous_stages_summary, replace_stage_participant)
  - gateway/src/routers/fixture_router.py (generate_fixtures, generate_fixtures_for_category, delete_fixtures, dummy_participants_replaced)
  - gateway/src/routers/match_router.py (get_templates)
  - tms/src/service/stage_service.py (create_stage, update_stage, is_update_stage_allowed, is_delete_fixtures_allowed, apply_to_all_stages, get_previous_stages_summary, create_fixture_from_template, delete_fixture_template, replace_stage_participant)
  - tms/src/service/fixture_service.py (generate_fixtures, generate_fixtures_for_category, delete_fixtures, dummy_participants_replaced)
  - ctms/src/router/fixture_template.py (list and get fixture templates)
source_files:
  - src/app/modules/tms/fixture-configuration/fixture-configuration.component.ts
  - src/app/modules/tms/fixture-templates/fixture-templates.component.ts
  - src/app/modules/tms/fixture-configuration/fixture-popups/swap-player/swap-player.component.ts
---
# Backend logic – stages, templates, generate, delete and replace

Each section gives the gateway step, the TMS checks in order, and the message shown. Messages are the English text the gateway returns. A missing permission gives "Access Denied" (403).

## Create stage (POST stage/v1/create_stage)

- Needs Edit on Edit Stage.
- Checks: the stage name is required ("Stage Name Required", 400); the event category must exist ("Event Category Not Found", 404); stages can only be created under a sub category ("Create Stages Only For Sub Categories", 400); State, District or Association separation is refused ("State, District and Association separation are no longer supported. Choose a parent level instead.", 400).
- The event draw settings fill in the defaults of the new stage. For a team category that has a playing order, it becomes the playing format. The stage order is updated.
- Success: "Stage Created" (201).

## Update stage (PUT stage/v1/update_stage)

- Needs Edit on Edit Stage. Stage not found: "Stage Not Found" (404). A new State, District or Association separation is refused as in create stage.
- Points guard: when points are published to OTT for this stage category, an edit is refused with "This action is not permitted. Points for this event have been published to OTT. ..." and a delete with "Deletion is not permitted. Points for this event have been published to OTT. ..." (403).
- "Stage Update Not Allowed" (400) when the change is not allowed: publish and unpublish are always allowed; deleting is refused when a dependent stage is in progress or completed; other changes are refused when this stage or a dependent stage is in progress or completed.
- A position match with more than 2 max rounds: "Position Match Not Allowed" (400). Category not found: "Event Category Not Found" (404).
- Changing the elite or excluded settings clears the saved elite or excluded players that no longer apply.
- Deleting a stage removes its stage participants and re-orders the remaining stages. Success: "Stage Updated" (200).

## Set stage configuration (PUT stage/v1/set_stage_configuration)

- Gateway: needs a login only. Stage not found: "Stage Not Found" (404). Otherwise it runs update stage with the new configuration, with the same checks and messages.

## Apply to all stages (PUT stage/v1/apply_to_all_stages)

- Needs Edit on Edit Stage.
- Fields that are not allowed: "Unknown or disallowed keys for apply-to-all: {keys}. ..." (400).
- Category not found: "Event Category Not Found" (404). No stages: "No Stages Found" (404).
- Success: "Updates applied to all stages successfully" (200).

## Stage list and previous stages summary (GET stage/v1/get_stages, previous_stages_summary)

- get_stages: returns the stages matching the filters with the rule settings of each stage. Success: "Stage Fetched" (200).
- previous_stages_summary: needs a login. Current stage not found: "Stage Not Found" (404). A first stage gets an empty list.
- For each earlier stage the summary counts the groups (group stage) or the rounds (knockout), and the number of matches expected per round. Success: "Stage Fetched" (200).

## Create fixture from template (POST stage/v1/create_fixture_from_template)

- Needs Edit on both Edit Stage and Fixture Access.
- Event category not found: "Event Category Not Found" (404). Sub categories only: "Create Stages Only For Sub Categories" (400).
- The category already has stages: "Stages already exist for this event category. Delete existing stages before creating from a template." (400).
- The stages of the template are created in order. An error at one stage stops the request and returns that error (a bad stage configuration: "Invalid configuration for stage '{name}': ..." (400)).
- The default cumulative standings priority is set up for the new stages.
- Success: "Fixture template created successfully" (201).

## Delete fixture template (DELETE stage/v1/delete_fixture_template)

- Needs Edit on Edit Stage. Category not found: "Event Category Not Found" (404). No stages: "No Stages Found" (404).
- The stages are deleted from the last to the first. For each, its standings are deleted and the cumulative standings rebuilt, its stage rule settings are removed, and it is deleted like a single stage.
- Success: "Fixture template deleted successfully" (200).

## Template lists (GET ctms/v1/fixture-template and match/v1/get_templates)

- Fixture templates: the gateway passes ctms/v1/fixture-template to the CTMS template catalogue, which holds the global and tenant templates (filters: usage, code, status, name; paged). List success: "Fixture Templates Retrieved Success {count} {total}" (200). An unknown template ID: "Fixture Template Not Found {fixture_template_id}" (404).
- match/v1/get_templates (needs a login) returns the match order templates by group size from the TMS, not the fixture templates.

## Generate fixtures for a stage (POST fixture/v1/generate_fixtures)

- Needs Edit on Fixture Access. Stage not found: "Stage Not Found" (404). No stage configuration: "Configuration Missing" (403).
- When an earlier stage that feeds this one is not completed, the stage becomes a sample fixture. A sample fixture needs an expected participant count: "Expected Participants Count Missing" (403); placeholders are created for it.
- Pair events (doubles, mixed) need two players in each real pair: "Cannot Generate Fixture, Pair Not Complete" (400).
- Group stage: the groups are created from the draft layout sent with a redraw, or randomly (seeds shuffled within equal display seeding). Knockout: the draw is created and saved. A failed step returns its own message.
- The redraw flag of the stage is cleared. Success: "Group Created" (200).

## Generate fixtures for a category (POST fixture/v1/generate_fixtures_for_category)

- Needs Edit on Fixture Access. Category not found: "Event Category Not Found" (404). No stages: "No stages found for this category" (404).
- A stage in progress or completed: "Cannot generate fixtures: stage '{stage_name}' is {stage_status}. All stages must not be IN_PROGRESS or COMPLETED." (400).
- Stages are generated in order; every stage after the first also gets its draft (matches). The first failure stops the run: "Fixture generation failed at stage '{stage_name}' (order {stage_order})" or "Draft creation failed at stage '{stage_name}' (order {stage_order})".
- Success: "Fixtures generated for all stages successfully" (200).

## Delete fixtures (POST fixture/v1/delete_fixtures)

- Needs Edit on Fixture Access. Stage not found: "Stage Not Found" (404).
- Refused with "Stage Update Not Allowed" (400) when the stage or a dependent stage is in progress or completed.
- When unbench is asked for, the benched participants go back into the draw first.
- The groups are soft deleted, their participants are removed, placeholder participants are removed, and the stage goes back to Draft.
- Success: "Fixture Deleted" (200).

## Dummy participants replaced (POST fixture/v1/dummy_participants_replaced)

- Gateway: needs a login only. Stage not found: "Stage Not Found" (404). Event category not found: "Event Category Not Found" (404).
- The stage becomes a genuine fixture in Draft. Elite and excluded placeholders are replaced by the real players, other placeholders are removed and the groups are cleared. If the event publishes fixtures automatically, the stage is published.
- Success: "Fixture Updated" (200).

## Replace a participant (POST stage/v1/replace_stage_participant)

- Needs Edit on Edit Stage. A dry run checks first, in order:
  1. Stage not found: "Stage Not Found" (400); a completed stage: "Replace is not allowed" (400).
  2. Only the first stage: "Replace is only allowed in the first stage" (400).
  3. Not for team categories: "Replace is not allowed for team" (400).
  4. The outgoing participant must be in the stage: "Stage Participant Not Found" (400).
  5. No match of the outgoing participant in progress or scored: "Replace is not allowed" (400).
- A new player is then registered (cash mode), the replacement is committed and the old participant withdrawn. Commit checks: order details missing ("Missing required order fields for replace"); the incoming player not found in the category ("Stage Participant Not Found"); the same player or one already in the stage ("Replace is not allowed"), all 400.
- Success: "Participants Registered Successfully" (new player) or "Participant replaced successfully" (existing player), code 201. The screen shows "Participant replaced successfully.". Details are in the replace participant guide.
