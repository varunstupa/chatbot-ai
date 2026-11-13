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

Each section gives the gateway step, the TMS checks in order, and the message shown. Messages are the English text the gateway returns. A missing permission gives "Access Denied" (403).

## Draft the knockout fixture (POST fixture/v1/draft_knockout_fixture)

- Needs Edit on Fixture Access.
- Refused with "Stage Update Not Allowed" (400) when a dependent stage is in progress or completed.
- Refused with "A redraw is required before creating a draft" (400) when the stage is flagged as needing a redraw and the bracket still has open places (benched players, or players without a seed). Generate the fixture again first.
- The bracket follows the saved stage seeds. Seeded players come first in display seeding order, then the others.
- With minimise byes, only one round is built from the players present. Otherwise the full bracket is built, with position matches and the maximum rounds from the stage settings.
- A player drawn against a bye moves on at once. A match of two byes is skipped and the bye moves on.
- Publishing: when the event publishes fixtures automatically, the stage and its position matches are published; otherwise their current publish settings are kept.
- Dependent stages whose expected participant count changed are rebuilt.
- Success: "Knockout Fixtures Created" (200).

## Knockout fixtures (GET fixture/v1/get_knockout_fixtures)

- Gateway: needs a login.
- Stage not found: "Stage Not Found" (404).
- No stage configuration: "Stage Configuration Missing" (400).
- No groups in the stage: "No Groups Found" (404).
- The preview is read from the saved seeds; nothing is re-drawn by this call.
- Success: "Knockout Fixtures Fetched" (200), with the groups and the benched participants.
- Errors that are not expected return code 500 with the error text.

## Knockout bracket (GET fixture/v1/get_knockout_matches)

- Gateway: needs a login and the event-id header: "event-id header is required" (400), or "event-id header must be a valid integer" (400). The gateway checks the scoring permission of the event and whether the user is a live match scorer, and adds who may score each match.
- Stage not found: "Stage Not Found" (404). Category missing on the stage: "Event Category Or Category Not Found" (404).
- A stage that is not a knockout: "Shuffle is only available for knockout stages." (400). This is the wrong text for a fetch and is reported as a finding.
- No groups: "No Groups Found" (404). No rounds: "Rounds Not Found" (404).
- The bracket is built from the rounds. Each round has its matches, the legs of each match, the golden match (when there is one) and the winners. A consolation bracket is built as a separate tree when the stage has one.
- Success: "Knockout Matches Fetched" (200).

## Update a round (POST round/v1/update_round)

- Gateway: needs a login only.
- No round found: "Rounds Not Found" (404).
- Round name longer than 15 characters: "Round Name Invalid" (400).
- When the stage is sent, a name already used by another round of that stage: "Round Name Already Exists" (400).
- Success: the updated round is returned. The success text of this call is not traced in this pass.

## Round names by position (GET round/round_names)

- Returns the names of the rounds for a round or a list of rounds, from the number of positions each round covers. A round without a position range has no name.
