---
doc_id: tms.fixture.api-knockout
title: Backend logic of the knockout stage APIs – draft, bracket, rounds and shuffle
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - knockout api
  - draft knockout rules
  - knockout bracket api
  - knockout fixtures rules
  - update round rules
  - round name rules
  - knockout matches api
  - bye rules backend
  - why is the knockout draft blocked
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What does the backend check before it creates the knockout fixtures?
  - Why does the draft say "A redraw is required before creating a draft"?
  - What is the rule for the round name?
  - What does the backend return when the knockout bracket is empty?
  - Why does the bracket fetch say "Shuffle is only available for knockout stages"?
backend_sources:
  - gateway/src/routers/fixture_router.py (draft_knockout_fixture, get_knockout_fixtures, get_knockout_matches)
  - gateway/src/routers/round_router.py (update_round, get_rounds)
  - gateway/src/routers/match_router.py (matches)
  - tms/src/router/round_router.py (update_round)
  - tms/src/service/round_service.py (update_round)
  - tms/src/service/knockout_fixture_service.py (draft_knockout_fixture, get_knockout_fixtures, get_knockout_matches)
source_files:
  - src/app/modules/tms/fixture-configuration/knockout-creation-wizard/knockout-creation-wizard.component.ts
  - src/app/modules/tms/fixture-configuration/knockout-draft-participants/knockout-draft-participants.component.ts
  - src/app/modules/tms/fixture-configuration/knockout-customise-participants/knockout-customise-participants.component.ts
---
# Backend logic – knockout stage APIs

Each section gives the gateway step, the TMS checks in order, and the message shown. The gateway checks the login and the permission (Edit on Fixture Access) before it forwards each draft call.

## Draft the knockout fixture (POST fixture/v1/draft_knockout_fixture)

- Needs Edit on Fixture Access.
- Refused with "Stage Update Not Allowed" (400) when a dependent stage is in progress or completed.
- Refused with "A redraw is required before creating a draft" (400) when the stage is flagged as needing a redraw. A redraw must be done first.
- The participants are placed by seed. Seeded players come first, then the others. Byes are placed so that:
  - with minimise byes, the byes are spread to keep the bracket small;
  - two byes never share a match, and a bye never meets a bye.
- The publish setting follows the event: when the event auto publishes fixtures, the stage is published; otherwise the position match publish setting is kept.
- Success: "Knockout Fixtures Created" (200).

## Knockout fixtures (GET fixture/v1/get_knockout_fixtures)

- Stage not found: "Stage Not Found" (404).
- No stage configuration: "Stage Configuration Missing" (400).
- No groups in the stage: "No Groups Found" (404).
- Success: "Knockout Fixtures Fetched" (200), with the groups and the benched participants.
- Errors that are not expected return code 500 with the error text.

## Knockout bracket (GET fixture/v1/get_knockout_matches)

- Gateway: needs the event ID header. The gateway checks the scoring permission of the event and whether the user is a live match scorer.
- Stage not found: "Stage Not Found" (404). Category missing on the stage: "Event Category Or Category Not Found" (404).
- A stage that is not a knockout: refused with code 400. The server text for this case is "Shuffle is only available for knockout stages.", which is the wrong text for a fetch. This is reported as a finding.
- No groups: "No Groups Found" (404). No rounds: "Rounds Not Found" (404).
- The bracket is built from the rounds. Each round has its matches, the legs of each match, the golden match (when there is one) and the winners of each match. A consolation bracket is built as a separate tree when the stage has one.
- Success: "Knockout Matches Fetched" (200).

## Update a round (POST round/v1/update_round)

- Gateway: needs a login.
- No round found: "Rounds Not Found" (404).
- Round name longer than 15 characters: "Round Name Invalid" (400).
- A name already used by another round of the same stage: "Round Name Already Exists" (400).
- Success: the updated round is returned. The success text of this call is not traced in this pass.

## Round names by position (GET round/round_names)

- Returns the names of the rounds for a round or a list of rounds, using the position range of each round.
