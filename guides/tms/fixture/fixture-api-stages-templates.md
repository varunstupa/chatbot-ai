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

Each section gives the gateway step, the TMS checks in order, and the message shown. The gateway checks the login and the permission (Edit on Edit Stage or Fixture Access) before it forwards each call.

## Create stage (POST stage/v1/create_stage)

- Needs Edit on Edit Stage.
- Checks: the stage name is required ("Stage Name Required", 400); the event category must exist ("Event Category Not Found", 404); stages can only be created under a sub category ("Create Stages Only For Sub Categories", 400).
- For a team category that has a playing order, the stage order is updated.
- Success: "Stage Created" (201).

## Update stage (PUT stage/v1/update_stage)

- Needs Edit on Edit Stage. Stage not found: "Stage Not Found" (404).
- Points guard: when points are published for this stage category, the edit or delete is refused with code 403 (the server text has no English translation yet).
- "Stage Update Not Allowed" (400) when the change is not allowed. Publish and unpublish are always allowed. Deleting is refused when a dependent stage is in progress or completed. Changing the structure is refused when this stage is in progress or completed.
- A configuration with a position match is refused when the max rounds is more than 2: "Position Match Not Allowed" (400).
- Changing the elite or excluded settings clears the saved elite or excluded players that no longer apply.
- Deleting a stage removes its stage participants and re-orders the remaining stages.

## Set stage configuration (PUT stage/v1/set_stage_configuration)

- Stage not found: "Stage Not Found" (404). Otherwise it applies the same rules as update stage, for the configuration only.

## Apply to all stages (PUT stage/v1/apply_to_all_stages)

- Keys that are not allowed for apply to all are refused with code 400 (the message has no English translation yet).
- Category not found: "Event Category Not Found" (404). No stages: "No Stages Found" (404).
- Success: "Updates applied to all stages successfully" (200).

## Stage list and previous stages summary (GET stage/v1/get_stages, previous_stages_summary)

- get_stages: returns the stages matching the filters with the rule settings of each stage. Success: "Stage Fetched" (200).
- previous_stages_summary: current stage not found, or no earlier stage: "Stage Not Found" (404).
- For each earlier stage the summary counts the groups (group stage) or the rounds (knockout), and the number of matches expected per round. Success: "Stage Fetched" (200).

## Create fixture from template (POST stage/v1/create_fixture_from_template)

- Event category not found: "Event Category Not Found" (404). Sub categories only: "Create Stages Only For Sub Categories" (400).
- If the category already has stages, the request is refused with code 400 (the message has no English translation yet).
- The stages of the template are created in their order. An error at one stage stops the request and returns that error.
- Success: "Fixture template created successfully" (201).

## Delete fixture template (DELETE stage/v1/delete_fixture_template)

- Category not found: "Event Category Not Found" (404). No stages: "No Stages Found" (404).
- Each stage standings are deleted and the cumulative standings are rebuilt.
- Success: "Fixture template deleted successfully" (200).

## Template list (GET match/v1/get_templates and CTMS fixture templates)

- The gateway sends the request to the CTMS template catalogue, which holds the global and tenant templates. The list can be filtered by usage (global or tenant), code, status and name, and it can be paged.
- One template: "Template Not Found" (404) when the ID does not exist. Lists: "Templates Retrieved Successfully" (200). Errors: "Error retrieving templates" (500).
- CTMS message keys such as FIXTURE_TEMPLATES_RETRIEVED_SUCCESS have no English text in the repos, so the screen may show the key itself.

## Generate fixtures for a stage (POST fixture/v1/generate_fixtures)

- Needs Edit on Fixture Access. Stage not found: "Stage Not Found" (404). No stage configuration: "Configuration Missing" (403).
- Sample fixtures need an expected participant count: "Expected Participants Count Missing" (403).
- Pair events (doubles, mixed) need at least two players for each pair: "Cannot Generate Fixture Pair Not Compete" (400).
- Group stage: the groups and matches are created from the draft layout (or randomly when no layout is sent). Success: "Group Created" (200).
- Knockout stage: the draw is created. A failed draw returns its own message.
- A redraw can send the same draft layout again; benched participants are filtered out.

## Generate fixtures for a category (POST fixture/v1/generate_fixtures_for_category)

- Needs Edit on Fixture Access. Category not found: "Event Category Not Found" (404). No stages: "No Stages Found" (404).
- Refused with code 400 when a stage is in progress or completed (the message has no English translation yet).
- Stages are processed in order. A failure stops the run with a stage message (the generation failure text has no English translation yet), or "Draft creation failed at stage '{stage_name}' (order {stage_order})".
- Success: "Fixtures generated for all stages successfully" (200).

## Delete fixtures (POST fixture/v1/delete_fixtures)

- Needs Edit on Fixture Access. Stage not found: "Stage Not Found" (404).
- Refused with "Stage Update Not Allowed" (400) when the stage or a dependent stage is in progress or completed.
- When unbench is asked for, the benched participants go back into the draw first.
- The groups are soft deleted, their participants are removed, and dummy participants are removed from the stage.
- Success: "Fixture Deleted" (200).

## Dummy participants replaced (POST fixture/v1/dummy_participants_replaced)

- Stage not found: "Stage Not Found" (404). Event category not found: "Event Category Not Found" (404).
- Dummy participants of the stage are removed and the groups are cleared. If the event auto publishes fixtures, the stage is published.
- Success: "Fixture Updated" (200).

## Replace a participant (POST stage/v1/replace_stage_participant)

- Needs Edit on Edit Stage. Checks, in order:
  1. Only the first stage: "Replace is only allowed in the first stage" (400).
  2. Not for team categories: "Replace is not allowed for team" (400).
  3. The outgoing participant must be in the stage: "Stage Participant Not Found" (400).
  4. The outgoing participant must have no match in progress or scored: "Replace is not allowed" (400).
  5. The incoming participant must differ from the outgoing one and must not already be in the stage: "Replace is not allowed" (400).
  6. An order ID and payment mode are needed for a new registration: "Missing required order fields for replace" (400).
- A dry run returns "Replace dry run completed successfully" (200) without changing anything.
- Success: "Fixture Updated" (200). The screen shows its own success text, "Participant replaced successfully.".
