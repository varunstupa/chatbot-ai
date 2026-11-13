---
doc_id: tms.schedular.api
title: Backend logic of the Scheduler APIs – slot assignment, auto schedule, swap, reset, visibility and umpires
routes:
  - tms/schedular/:event_id/:participant_id/:category_id
aliases:
  - scheduler api
  - scheduler backend
  - assign match slots rules
  - auto schedule backend
  - auto assign rules
  - swap match slots rules
  - why can I not swap matches
  - why is the match not placed
  - pending manual reasons
  - umpire assign rules
  - schedule visibility api
  - day schedule api
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What does the backend check before it places a match on a slot?
  - Why does the server say "Start time is outside planner range"?
  - What does the auto schedule do with a match that has no home participant?
  - What are the pending reasons of auto schedule?
  - Why can I not swap two matches in the Scheduler?
  - What does the backend return when an umpire assignment has no slots?
  - Why does auto scheduling require venue registration?
  - Why is a match missing from the available swap options?
  - How do I reset or remove match slots?
  - What does "No active planners found for this venue and date" mean?
backend_sources:
  - gateway/src/common/enum/enums.py (Schedule Match Access, Schedule Umpire Access)
  - gateway/src/routers/planner_router.py (assign, auto assign, swap, remove, reset, visibility, event slots, umpire endpoints)
  - tms/src/router/planner_router.py
  - tms/src/service/planner.py (assign_match_slots, assign_match_slots_by_venue, swap_match_slots, get_day_schedule)
  - tms/src/service/auto_schedule_service.py (auto_assign_match_slots)
  - tms/src/service/venue_schedule_service.py (pending reasons)
  - tms/src/service/event_official_service.py (assign, assign by IDs, remove, reset)
  - tms/src/common/enums.py (AutoAssignPendingReason)
source_files:
  - src/app/modules/tms/schedular/schedular.component.ts
  - src/app/core/services/schedular-service/schedular.service.ts
  - src/app/core/constants/api-constant.ts
answer_notes: |
  Answering guidance for the TMS assistant:
  1. Identify the operation: day schedule, manual assignment, auto schedule, swap, remove/reset, visibility, event slots, or official assignment.
  2. Use the exact endpoint-specific validation message where available.
  3. For auto-schedule pending matches, explain the returned pending reason directly.
  4. Distinguish a successful empty day-schedule response from a failed request.
  5. Distinguish official assignment by venue/date from assignment by match IDs; their validations differ.
  6. If the message has no English translation, say that the source indicates the UI may show a raw key; do not invent the missing text.
  7. Do not claim to cover untraced match-list, umpire-settings, live match-centre, official-notes, or venue-day behavior.
  8. The gateway checks login and permissions before forwarding each call. If a request is refused, consider permission/access before attributing the issue to scheduling data.
  9. Do not invent additional placement rules, conflict resolutions, or reset safeguards beyond the documented behavior.
---

# Backend logic – Scheduler APIs

## Scope and validation model

This guide describes the documented backend behavior for Scheduler APIs: day schedule retrieval, manual slot assignment, auto scheduling, swapping, removing/resetting slots, schedule visibility, event slots, and match-official assignment.

The gateway checks login and the required permission before forwarding each call. A successful response does not imply that every requested match was placed: auto scheduling can return a pending list, and manual assignment can follow a configured conflict-handling decision.

This guide does not cover every Scheduler UI or API: the match list, player umpiring settings, live match-centre status, event official notes, and event venue days were not traced in this pass.

## Quick reference

| Task | Main behavior |
|---|---|
| Get day schedule | Returns planner intervals and scheduled matches, or an empty schedule if no planner exists for the venue/date. |
| Assign match slots | Validates match IDs, table count, active planner, planner hours, slots, and scheduling conflicts. |
| Auto schedule | Requires match IDs or a stage ID, requires venue registration to be enabled, and returns matches that could not be placed with pending reasons. |
| Swap match slots | Both matches must exist and have assigned slots; the proposed swap is checked for scheduling conflicts. |
| Remove/reset slots | Removes assigned slots or clears slots for specified matches; whole-venue reset is confirmed in the UI. |
| Schedule visibility | Hide/Unhide updates schedule visibility. |
| Assign officials | Validates officials, planner availability, time range, match IDs, and assigned slots depending on the endpoint. |

## Day schedule

**Endpoint:** `POST planner/v1/get_day_schedule`

The backend behavior is:
- If no planner exists for the venue and date, it returns **200 / "Success"** with empty intervals and an empty schedule.
- If slot IDs are supplied, it returns the intervals for those slots.
- Otherwise, it returns the planner intervals and the matches assigned to them.
- The result can optionally be returned in table-wise form.

A successful empty response can therefore mean that no planner exists for the selected venue/date; it does not necessarily mean the request failed.

## Assign matches to slots

**Endpoint:** `POST planner/v1/assign_match_slots` (when a shared venue is sent instead of one event venue, the same endpoint spreads the matches over that venue's plans; it then needs a start table).

If the event uses Match Call Out, every slot action (assign, auto schedule, swap) is refused with 409 "This event uses Match Call Out: time slots cannot be assigned".

## Assign matches to slots – validation messages

The documented checks include:

| Condition | Response |
|---|---|
| Match IDs are invalid | `Invalid match IDs provided` (400) |
| Per-match table count is not 1 or 2 | `Invalid per-match table count provided` (400) |
| No active planner exists for the venue | `No active planners available` (404) |
| Requested start time is outside planner hours | `Start time is outside planner range` (400) |
| Planner has no configured slots | `No slots configured for planner` (400) |
| Only plans with status available or pending are used | otherwise `No active planners available` (404) |
| No free slots exist in the requested range | "There are no available slots to schedule the matches you have selected. All slots are either fully occupied or blocked. ..." (400, cannot be overridden) |
| Fewer free slots than selected matches | "It seems that you don't have enough slots to schedule all the matches you have selected. You can proceed with Partial Scheduling ..." (400) |
| By-venue request is invalid | `Invalid assign request: {reason}` (400) |
| No valid matches remain for a by-venue request | `No valid matches to schedule` (400) |
| By-venue assignment fails unexpectedly | `Planner assignment failed` (500) |

## Assign matches to slots – Scheduler APIs (2)

### Scheduling conflicts

The planner reports these conflicts (400), each with its own message:
- A player is in more than one match in the same or an overlapping slot ("... A player is involved in more than one match assigned to the same slot. ...").
- Matches from different rounds in the same slot ("... Matches from the different rounds cannot be placed in the same slot. ...").
- A later round in the same slot as, or before, an earlier round of the same group ("... Matches from a later round cannot be scheduled in the same slot as, or before, an earlier round. ...").
- More than one of these at once ("... Press Continue (Partial) to schedule only the valid matches, press Continue to force-schedule all selected matches, or press Cancel ...").

Unless the request specifies how to continue, a conflict stops the placement and nothing is saved. The documented continuation decisions are:
- Use the default behavior.
- Continue with valid matches only.
- Override all.

Do not assume that every conflicting assignment is automatically saved. The result depends on the decision supplied with the request.

On the Scheduler page a conflict opens an **Alert!** popup with the server message. **Continue ( Partial )** retries with valid matches only (not offered for a single match); **Continue** schedules all of them anyway; **Cancel** saves nothing. If nothing valid is left: "No valid matches to schedule".

## Auto schedule

**Endpoint:** `POST planner/v1/auto_assign_match_slots`

### Required inputs and prerequisites

- The request must include either a list of match IDs or a stage ID. If neither is supplied: "A filter (event_venue_id, venue_id, or match_ids) is required to auto-schedule" (400).
- Venue registration must be enabled for the event. Otherwise, the backend returns `Venue registration is not enabled for this event` (400).
- For a whole stage, only unscheduled matches that have both participants are used.
- Matches are grouped by the home side's registered venue and date, then placed. Matches that do not fit are tried at other registered venues.
- Auto scheduling does not force through conflicts; such matches end up pending.

## Auto schedule – pending matches and reasons

Auto scheduling can succeed overall while returning some matches as pending. The pending reason indicates why a match could not be placed.

| Pending reason | Meaning |
|---|---|
| `NO_HOME_PARTICIPANT` | The match has no home participant. |
| `NO_HOME_VENUE_REGISTRATION` | The home side is not registered for the venue. |
| `VENUE_AVAILABILITY_CANCELLED` | Venue availability was cancelled. |
| `NO_FEASIBLE_DATE` | No date fits the scheduling requirements. |
| `NO_FEASIBLE_SLOT` | No slot fits the scheduling requirements. |

A successful auto-schedule response is **200 / "Success"** and includes the pending list. An unexpected error returns **500 / "Internal Server Error"**.

When explaining a pending match, report the reason returned by the backend rather than guessing at a different cause.

## Swap two matches

**Endpoint:** `POST planner/v1/swap-match-slots`

The backend validates the proposed swap before saving it.

| Condition | Response |
|---|---|
| The same match is supplied on both sides | `Cannot Swap` (400) |
| A match does not exist | `Match Not Found` (400) |
| Either match has no assigned slot | `Match Slot Not Assigned` (400) |
| A match's planner cannot be found | `Not Found` (400) |
| The tables of one match do not fit in the other slot | `Match Cannot Move To Slot` (400) |
| The swap plan is missing required data | `Invalid Swap Plan` (500) |
| Swap succeeds | `Match Slots Swapped Successfully` (200) |

The swap is also checked for the same scheduling conflicts (player, different rounds, round order). A conflicting swap returns the conflict message (400) and offers only **Continue** (swap anyway) or **Cancel**.

If a swap fails, check that the two matches are different, both exist, both have assigned slots, both planners are available, and the proposed swap does not violate the scheduling rules.

## Remove and reset match slots

**Endpoints:**
- `POST planner/v1/remove_match_slots`
- `POST planner/v1/reset_match_slots`

- **Remove:** Removes slot assignments (slot, tables, start and end time) from the specified matches and makes their schedule visible again. Success: "Successfully removed slot assignments".
- **Reset:** Clears the slots of all matches that fit the chosen filters (event, category, stage, group, round, participant type, venue, date).
- Both remove automatically assigned player umpires from those matches; umpires assigned by hand stay linked. Matches handled by Match Call Out are skipped.
- Resetting the whole venue requires confirmation in the UI before the request is sent.

Assigning, auto-assigning, swapping, removing and resetting match slots need the **Schedule Match Access** permission with Edit; assigning umpires (officials) needs **Schedule Umpire Access** with Edit. Administrators and users with Live Match Centre access pass these checks; others get **403** "Access Denied". On the page, a reset is only sent about 3 seconds after confirmation, so it can still be cancelled with **Undo** in that time.

## Schedule visibility

**Endpoint:** `PUT planner/v1/update_schedule_visibility`

This endpoint is used by the **Hide** and **Unhide** actions.

- Success: `Updated Schedule Visibility` (200).
- Error: `Internal Server Error` (500).

Removing match slots also updates schedule visibility, according to the documented behavior.

## Event slots

**Endpoint:** `GET planner/v1/get_event_slots`

- Success: `Success` (200).
- Failure: `Error fetching event slots` with the error text (500).

If event slots cannot be fetched, the message indicates a request failure; the specific underlying cause must be taken from the returned error text rather than guessed.

## Assigning match officials / umpires

The documented endpoints are:
- `POST planner/v1/assign_event_official_match`
- `POST planner/v1/assign_event_official_match_ids`
- `POST planner/v1/remove_event_official_match`
- `POST planner/v1/reset_event_official_match`

### Assign by venue and date

For `assign_event_official_match`:

| Condition | Response |
|---|---|
| No officials supplied | `No officials provided for assignment` (400) |
| `user_role_ids` is supplied without a type | `type is required when user_role_ids is provided` (400) |
| No active planner exists for the venue/date | `No active planners found for this venue and date` (404) |
| No slots are available in the requested time range | `No slots available for the specified time range` (400) |
| No match is available to assign | `No matches available for assignment` (400) |
| More officials than available matches | `Not enough matches available for all officials` (400) |
| An official would be in two overlapping matches | `Some officials have overlapping assignments` (400) |
| Success | `Successfully assigned event officials to matches` (200) |

## Assigning match officials – by match IDs

For `assign_event_official_match_ids`:

| Condition | Response |
|---|---|
| No assignable official is found for the user on a match | `No assignable event official found for user on this match` (400) |
| Some match IDs are invalid or being modified | `Some match IDs are invalid or currently being modified` (400) |
| One or more matches have no assigned slot | `Some matches don't have slots assigned` (400) |
| More officials than the per-match limit in Umpire/Referee Settings | `Assignment would exceed per_match_limit for one or more matches` (400) |
| An official would be in two overlapping matches | `Event official has overlapping assignments` (400) |

Assigning by match IDs and resetting official assignments only check that you are signed in; assigning by venue/date and removing need **Schedule Umpire Access** (Edit).

## Assigning match officials / umpires – Scheduler APIs (2)

### Remove official assignments

- No assignments exist to remove: `No event official assignments found to remove` (404).
- Success: `Successfully removed event official assignments` (200).
- Failure: `Error removing event official assignments` (500).

### Reset official assignments

- No assignment matches the supplied criteria: `No event official assignments found matching the provided criteria` (404).
- Success: `Successfully reset event official assignments` (200).
- Failure: `Error resetting event official assignments` (500).

If official assignment fails, first identify which endpoint was used: venue/date assignment and match-ID assignment have different validation checks.

## Rounds used by filters

**Endpoint:** `GET round/v1/get_rounds`

Returns the rounds for a stage for use in the round dropdown and round tags. Detailed round behavior is covered by the results API guide.

## Frequently asked questions

### What does the backend check before placing a match on a slot?

It validates match IDs, the per-match table count, active planner availability, requested start time, configured slots, and scheduling conflicts. The exact checks depend on whether the regular or by-venue assignment endpoint is used.

### Why does the server say "Start time is outside planner range"?

The requested start time is outside the active planner's configured hours. Check the selected venue/date and planner time range.

### What happens if auto schedule cannot place a match?

The match is returned in the pending list with a reason such as `NO_HOME_PARTICIPANT`, `NO_HOME_VENUE_REGISTRATION`, `VENUE_AVAILABILITY_CANCELLED`, `NO_FEASIBLE_DATE`, or `NO_FEASIBLE_SLOT`.

### Why does auto scheduling require venue registration?

The documented API prerequisite is that venue registration must be enabled for the event. If it is disabled, the request is rejected with `Venue registration is not enabled for this event`.

### Why can I not swap two matches?

Check that the selected matches are different, both exist, both have assigned slots, both planners can be found, and the swap does not cause participant scheduling, round sequence, or round overlap conflicts.

## Frequently asked questions – Scheduler APIs (2)

### Why does an umpire assignment fail because there are no slots?

For venue/date assignment, the backend returns `No slots available for the specified time range` if no slots are available in that range. For assignment by match IDs, it returns `Some matches don't have slots assigned` if one or more matches lack assigned slots.

### What does an empty day schedule mean?

If no planner exists for the selected venue/date, the API returns success with empty intervals and an empty schedule. The request may have succeeded even though there are no schedule entries.

## Natural-language and Hinglish query patterns

Treat these as equivalent intents when retrieving this document:

- "Scheduler match ko slot par place karne se pehle kya check karta hai?"
- "Start time is outside planner range ka matlab kya hai?"
- "Auto schedule mein match pending kyun hai?"
- "NO_HOME_PARTICIPANT ka kya matlab hai?"
- "NO_FEASIBLE_SLOT kyun aa raha hai?"
- "Venue registration enable karna zaroori kyun hai?"
- "Do matches swap kyun nahi ho rahe?"
- "Match Slot Not Assigned ka matlab kya hai?"
- "Umpire assign karte waqt slots available kyun nahi hain?"
- "Day schedule empty kyun aa raha hai?"
- "Match slots remove aur reset mein kya difference hai?"
- "Schedule ko Hide ya Unhide kaise karte hain?"

## Source references

- Gateway Scheduler endpoints: `gateway/src/routers/planner_router.py`
- Planner router: `tms/src/router/planner_router.py`
- Slot assignment, swap, and day schedule: `tms/src/service/planner.py`
- Auto scheduling: `tms/src/service/auto_schedule_service.py`
- Pending reasons: `tms/src/service/venue_schedule_service.py`
- Official assignment/removal/reset: `tms/src/service/event_official_service.py`
- Pending-reason enum: `tms/src/common/enums.py` (`AutoAssignPendingReason`)
- Scheduler UI: `src/app/modules/tms/schedular/schedular.component.ts`
- Scheduler service: `src/app/core/services/schedular-service/schedular.service.ts`
- API constants: `src/app/core/constants/api-constant.ts`
