---
doc_id: tms.score-stream.api
title: Scoring and Streaming APIs — Backend Behaviour and Troubleshooting
routes:
  - tms/score-stream/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - score stream api
  - score save backend
  - update score backend
  - which calculator scores my match
  - sport calculator dispatch
  - live score backend
  - rule settings used for scoring
  - round rule override
  - scoring error 403
  - walkover backend
  - score not saving
  - wrong score input
  - live score versus final score
  - match status and streaming
  - team match lineup
tenants: all
exclude_tenants: []
overrides: null
document_type: technical_product_help
audience:
  - TMS support
  - developers
  - technical administrators
  - AI support assistant
supported_languages:
  - English
  - Hindi
  - Hinglish
suggested_questions:
  - How does the backend choose the scoring rules for a match?
  - What happens in the backend when I click Update on a score?
  - Which rule settings does the backend read for scoring?
  - Why does the score save return 403 with a set message?
  - What is the difference between the live and the manual score in the backend?
  - What does the backend do for a walkover?
  - Why is my match score not saving?
  - Which scoring calculator is used for each sport?
  - Why can't I update a match after a walkover?
  - What happens when I update match streaming status?
backend_sources:
  - gateway/src/routers/scoring_router.py (update_score)
  - gateway/src/routers/match_router.py (matches, update_match_status, sub-matches, reverse-participants-order)
  - gateway/src/routers/rule_setting_router.py (get_rule_settings)
  - tms/src/router/scoring_router.py (_dispatch_update_score)
  - tms/src/utils/scoring/scoring_factory.py (ScoringFactory)
  - tms/src/utils/scoring/strategies/register_strategies.py (sport registrations)
  - tms/src/service/scoring_service.py (update_score, rule lookup)
  - tms/src/utils/scoring/calculators/ (badminton, table_tennis, tennis, padel)
source_files:
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts
  - src/app/core/constants/api-constant.ts
answer_notes: |
  Guidance for the assistant:
  - Identify whether the user is asking about a score, a scoring rule, a walkover, match status, streaming, sub-matches, lineups or rule settings.
  - Explain the documented request flow and checks in order where relevant.
  - Use the exact error message and HTTP status code when the user supplies them.
  - Do not infer a specific cause from a status code alone if the message or context is missing.
  - Do not claim to inspect a live match, request payload, database record, permission or streaming provider unless live system data is available.
  - The streaming service's internal rules, live match-centre status logic and CTMS sport configuration are not described in this document. State this limitation instead of guessing.
  - Sport-specific scoring details belong to the separate sport guides for Table Tennis, Badminton, Padel and Tennis. This document explains dispatch and shared backend behaviour, not every sport's scoring rules.

  Intent: score will not save: Ask for or use the exact response message. A rule rejection can return 403 with a message such as “Wrong score input for set 2”. Check the relevant sport's scoring rules, sport ID, participant type and effective Game Play settings. If the message indicates a permission problem, check Update Score and Edit permissions or the live match scorer path. Do not treat every 403 as the same failure.

  Intent: identify which sport calculator is used: Use the sport ID mapping in this document. Padel uses the Padel calculator, which uses Tennis rules. If no sport ID is supplied, the legacy path is used. If the sport ID has no registered strategy, the request is refused with the documented error. Do not guess what an unlisted sport ID represents.

  Intent: rule settings do not match expectations: Explain that Game Play settings are read from event, stage, category and round. Round-level settings override stage-level settings, and the round is matched by name. For a group stage, the group-stage round's rule is used. Mention that detailed sport rules are in the separate sport guides.

  Intent: live score versus final score: The live flag selects the in-progress scoring path. Manual score entry is the final result and must resolve the match by identifying a winner before saving. Reset operations use a separate path.

  Intent: walkover blocks score entry: A walkover must be reset before new sets can be added. “Match Already Walkover Reset First” is 422. “Match Data Not Reset” is 403 when reset is blocked by rules. A knockout result change may be refused if a later round has already used the result. Do not infer a more specific reason without the exact response.

  Intent: streaming update failed: Check Update Stream and Edit permissions, confirm the event exists, and use the exact response. “Event Not Found” is documented as 400; “Video Not Found” is 404. The streaming service's internal rules are outside this document, so do not invent provider-specific fixes.

  Intent: team sub-match or lineup issue: Sub-matches require a team-match parent and are created one per playing table. Reversing order swaps sides of the team match's sub-matches. Automatic lineup creation requires team members. “Participant Not Found” means the requested participant could not be found during lineup update.

  When to ask a follow-up question:
  Ask one focused question if the reported problem is too broad to diagnose from the available details.

  - “Score not saving.” → “What exact error message or HTTP status do you see?”
  - “Rules are wrong.” → “Which sport and participant type is the match, and what rule or score is being rejected?”
  - “Streaming isn't working.” → “What exact response do you see: Event Not Found, Video Not Found, Access Denied, or something else?”
  - “Lineup failed.” → “Are you fetching/creating the lineup, or updating an existing participant's status?”
  - “Match can't be changed.” → “Is there a walkover, or has a later knockout round already used this match result?”

  Do not ask for information already present in the user's message. Ask for payloads, logs or identifiers only when needed for authorised technical diagnosis.
---

# Scoring and Streaming APIs — Backend Behaviour and Troubleshooting

## Purpose and scope

This document explains the documented backend behaviour behind scoring, match status and streaming-related APIs in Stupa TMS. It covers how score updates are routed, which scoring calculator is selected, how Game Play rule settings are read, how live and manual scores differ, how walkovers are handled, and how team-match sub-matches and lineups are managed.

It is a technical reference. When answering an organiser's question, explain the relevant behaviour in plain language and avoid exposing implementation details unless they help answer the question. When answering a developer or support question, preserve API names, response codes and source-file references.

## Quick reference

| User question or symptom | Relevant documented behaviour |
|---|---|
| “Which calculator scores this match?” | The request's sport ID selects the registered scoring calculator. |
| “Why did the score return 403?” | A scoring rule may reject the submitted score and return its rule message, such as “Wrong score input for set 2”. Check the exact message. |
| “Is this a live score or final score?” | The live flag selects the in-progress score path. Manual score entry is expected to resolve the match with a winner before saving. |
| “Which rules are applied to this match?” | Game Play settings are read from the event, stage, category and round. A round-level setting overrides a stage-level setting. |
| “Why can't I add sets after a walkover?” | The walkover must be reset first. The documented error is “Match Already Walkover Reset First” (422). |
| “Why can't I change a score in a knockout match?” | If a later round has already used the result, the progression check can refuse the change. |
| “Why did streaming status fail?” | The gateway requires Update Stream and Edit permissions. Streaming-service-specific rules are outside this document. |
| “Why can't I create team sub-matches?” | Sub-matches are supported for team matches; a non-team parent match is refused. |

## Save or update a score

### API

`PUT score/v1/update_score`

### Request and permission checks

- The gateway requires the event ID header and a score payload.
- The request needs **Update Score** and **Edit** permissions. A live match scorer can also save.
- The payload includes the sport ID, participant type, match, sets and walkover details.
- TMS dispatches the request to the scoring implementation for the relevant sport. Live scoring follows the live path.

### Success and validation failure

- Successful response: **200**, message **“Score Updated”**.
- If a scoring rule rejects the submitted score, the response is **403** with the message from that rule. Example: **“Wrong score input for set 2”**.

A 403 response with a set-specific message means the submitted score did not satisfy a scoring rule. Use the exact message and the relevant sport's scoring guide to identify the rule. Do not assume every 403 is a score-validation error; permissions also apply to the request.

### Suggested troubleshooting sequence

1. Read the exact response message, not only the HTTP status.
2. If the message names a set, check the submitted score for that set against the relevant sport's rules.
3. Confirm the request is using the intended sport ID and participant type.
4. If the response indicates access is denied, check the required permissions.
5. If the error concerns a walkover or knockout progression, follow the relevant sections below.
6. If the cause is still unclear, inspect the request payload and server response in the authorised logs or debugging tools.

## Which scoring calculator is used?

The request's **sport ID** determines the scoring calculator selected by the scoring factory and registered strategies.

| Sport ID | Sport | Scoring implementation |
|---:|---|---|
| `1` | Table Tennis | Table Tennis calculator |
| `2` | Padel | Padel calculator, which uses Tennis rules |
| `3` | Tennis | Tennis calculator |
| `4` | Badminton | Badminton calculator |

- If the request contains a sport ID that has no registered calculator, the request is refused with: **“No scoring strategy registered for sport_id {id}”**.
- If no sport ID is supplied, the legacy scoring path is used.
- The participant type determines the path within the selected sport:
  - **Singles (`1`)** — individual path.
  - **Doubles (`3`)** — individual path.
  - **Mixed doubles (`4`)** — individual path.
  - **Team (`2`)** — team path.

The individual path for doubles and mixed doubles is the documented dispatch behaviour; do not reinterpret it as saying that only one person participates in those matches.

## Live score versus manual score

The backend distinguishes a live, in-progress score from a manually entered final score.

### Live score

- The call sets the live flag.
- The live path updates the score while the match is being played.
- A live score represents the current in-progress score, not necessarily the final result.

### Manual score

- A manual score is entered as the final result after the match.
- It must resolve the match by identifying a winner before it can be saved.

### Resetting a score

Resetting a score or resetting a walkover is handled by a separate reset path. Do not treat reset as the same operation as submitting an ordinary score update.

## Which Game Play rule settings are used?

The scoring service reads Game Play settings associated with the event, stage, category and round.

### Rule precedence

- A **round-level** setting overrides the **stage-level** setting.
- The round is matched by its name.
- For a group stage, the rule for the group-stage round is used.

When explaining an unexpected score validation result, check the effective rule for the match's round instead of assuming that the stage-level rule always applies.

### Settings read by scoring

The documented settings include:

- **Number of sets / rule set**.
- **Match type**:
  - **ST** — sets to win.
  - **SP** — play every set.
- **Point rule**:
  - Standard rule: deuce, value `1`.
  - Golden rule: value `2` when the standard rule is off.
- **Decider set** setting.
- **Sudden death / cap** setting.
- **Sub-match rule** for team matches.
- **Winner logic** and **point system** used for standings.

The sport-specific guides explain what these settings mean for each sport. This API document does not define all the detailed scoring rules for each sport.

## Walkovers and disqualifications

A walkover is saved with its reason, and the server calculates the match result from the walkover details.

### Adding sets after a walkover

A match with a walkover cannot receive new sets until the walkover has been reset.

- Error: **“Match Already Walkover Reset First”**
- HTTP status: **422**
- Resolution: reset the walkover first, then submit the score if the workflow permits it.

### Reset blocked by the rules

- Error: **“Match Data Not Reset”**
- HTTP status: **403**

The message indicates that the reset was blocked by the applicable rules. Do not claim a more specific cause unless the relevant rule or server response identifies it.

### Changing a result in a knockout stage

If a match has already been won in a knockout stage, the system checks progression before allowing the score to change. If a later round has already used that result, the change is refused with the relevant progression error.

When a user reports that a score cannot be changed after the next round has been populated, explain that the result may already have affected later-round progression. The exact response message should be checked before diagnosing further.

## Match status and streaming

### API

`PATCH match/v1/update_match_status`

### Gateway checks and documented responses

- The gateway requires **Update Stream** and **Edit** permissions.
- If the event is not found, the response is **400**, message **“Event Not Found”**.
- On the documented successful path, the response is **200**, message **“Match Updated Successfully”**.
- Publishing a stream, turning streaming off, or changing the video uses the streaming service.
- If the requested video is missing, the response is **404**, message **“Video Not Found”**.

### Scope limitation

The streaming service is not included in the source repositories covered by this documentation. Its internal rules and failure modes are therefore not described here.

If a user asks why a stream is unavailable, use the documented checks first: confirm the event and the exact error, and check the relevant permissions. If the failure depends on streaming-provider behaviour, explain that the provider-specific cause cannot be determined from this document alone.

## Team-match sub-matches and reverse participant order

### Create sub-matches

API: `POST match/v1/sub-matches`

- Team-match sub-matches are saved one per playing table.
- A parent match that is not a team match is refused.

If sub-match creation fails, first confirm that the parent match is a team match. Do not assume that sub-matches can be created for an individual match.

### Reverse participants' order

The reverse-participants-order operation swaps the sides of the sub-matches belonging to a team match.

- If the match does not exist, the response is **404**, message **“Match Not Found”**.

## Team-match lineups

### Fetch lineup

API: `POST team/v1/fetch_lineup`

Documented responses:

- **200** — “Team Match Participants Fetched”.
- **201** — “Team Match Participants Created” when a new lineup is created because the team has members.
- **404** — “No Team Participants For Auto Creation” when there are no team members to use for automatic creation.

### Update lineup

API: `PUT team/v1/update_lineup`

Documented responses:

- **200** — “Participant Status Updated”.
- **404** — “Participant Not Found” when the participant cannot be found.

When troubleshooting a lineup issue, distinguish between fetching an existing lineup, automatically creating one from team members, and updating a participant's status.

## Read Game Play rule settings

### API

`GET rule_setting/v1/get_rule_settings`

The Score and Streaming page reads the event's Game Play settings so that the score boxes and rule messages match the configured rules.

- Login is required.
- A request that is neither global nor for an event returns **401**, message **“Unauthorized Access”**.
- Success returns **200**, message **“Rule Settings Get”**.

If the page's score inputs or rule messages appear inconsistent with the expected rules, verify which rule settings the page retrieved and whether the request was made in the correct event/global context. Do not claim that a settings request failed unless its actual response is available.

## Match list, playing order and official notes

- The match list shown on the page comes from the match-list API. Its behaviour is documented in the separate results API guide.
- Team-match playing order is read using the playing-order bulk call. Its behaviour is also documented in the results API guide.
- Event official notes are read and saved through `GET` and `PUT planner/v1/event_official_notes`. These notes are associated with umpires and the referee of a match; further details belong to the scoring API guide.

Do not infer undocumented match-list or playing-order behaviour from this document.

## Natural-language question patterns

Users may describe these issues without knowing API names. These examples are alternate phrasings of documented behaviour, not additional product features.

### Intent: score will not save

Possible questions:
- “Why is my score not saving?”
- “Score update karte hi error aa raha hai.”
- “It says Wrong score input for set 2.”
- “Why did the score API return 403?”
- “I entered the result, but it was rejected.”

### Intent: identify which sport calculator is used

Possible questions:
- “Which calculator handles this match?”
- “Padel ka score kis rules se calculate hota hai?”
- “Why is the wrong scoring logic being used?”
- “What happens if sport ID is missing?”
- “No scoring strategy registered for sport_id 5 — what does that mean?”

### Intent: rule settings do not match expectations

Possible questions:
- “Why is the match using different rules?”
- “Round rule override kaise work karta hai?”
- “Why is the score box enforcing this rule?”
- “Does the round setting override the stage setting?”
- “Which rule settings are read when saving a score?”

### Intent: live score versus final score

Possible questions:
- “Is this score final or live?”
- “Why is the match showing an in-progress score?”
- “Live score aur manual score mein kya difference hai?”
- “Why does manual score need a winner?”

### Intent: walkover blocks score entry

Possible questions:
- “Why can't I add sets after a walkover?”
- “Match Already Walkover Reset First aa raha hai.”
- “What does Match Data Not Reset mean?”
- “Can I change a knockout result after the next round is ready?”

### Intent: streaming update failed

Possible questions:
- “Why can't I turn streaming on?”
- “Video Not Found aa raha hai.”
- “The match status did not update.”
- “Why is the streaming API returning an error?”

### Intent: team sub-match or lineup issue

Possible questions:
- “Why can't I create sub-matches?”
- “Can I reverse the order of team matches?”
- “Team lineup auto-create nahi ho rahi.”
- “No Team Participants For Auto Creation aa raha hai.”
- “Why does it say Participant Not Found?”

## API and error quick reference

| Operation | API | Documented response or check |
|---|---|---|
| Update score | `PUT score/v1/update_score` | 200 “Score Updated”; scoring-rule rejection may return 403 with the rule message |
| Update match status / streaming | `PATCH match/v1/update_match_status` | Requires Update Stream and Edit; event missing: 400 “Event Not Found”; video missing: 404 “Video Not Found”; success: 200 “Match Updated Successfully” |
| Read Game Play rules | `GET rule_setting/v1/get_rule_settings` | Login required; invalid global/event context: 401 “Unauthorized Access”; success: 200 “Rule Settings Get” |
| Create team sub-matches | `POST match/v1/sub-matches` | Only a team-match parent is supported |
| Reverse participant order | reverse-participants-order operation | Missing match: 404 “Match Not Found” |
| Fetch team lineup | `POST team/v1/fetch_lineup` | 200 fetched; 201 created when members exist; 404 when no team participants are available for auto creation |
| Update team lineup | `PUT team/v1/update_lineup` | 200 “Participant Status Updated”; missing participant: 404 “Participant Not Found” |
| Add sets after walkover | Score update path | 422 “Match Already Walkover Reset First” until walkover is reset |
| Reset match data | Reset path | May be blocked with 403 “Match Data Not Reset” |

## Source-of-truth and scope limitations

- This document describes only the backend behaviour listed in the referenced source files.
- It does not document every sport-specific scoring rule. Use the relevant Table Tennis, Badminton, Padel or Tennis guide for those details.
- It does not describe the streaming service's internal rules.
- It does not describe live match-centre status logic or CTMS sport configuration.
- It does not contain the full behaviour of the match-list API or playing-order bulk API; consult the results API guide.
- It does not confirm the current state of a match, the request payload, user permissions, event settings or stream. Do not claim to have inspected these unless live system data is available.
- If a question depends on an undocumented service or missing runtime information, state the limitation and ask for the exact response or recommend checking authorised logs/source code.
