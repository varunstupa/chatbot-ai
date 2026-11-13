---
doc_id: tms.fixture.golden-match
title: Golden match – when it is created, the logic behind it, and how it is played, scored and counted
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
  - tms/score-stream/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - golden match
  - golden matches
  - golden match created
  - golden match logic
  - when is golden match created
  - golden match not created
  - tie breaker match
  - tied legs
  - decider match teams
  - golden match order
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - When is a golden match created?
  - What is the logic for golden matches?
  - Why was no golden match created?
  - Who plays in the golden match?
backend_sources:
  - tms match_service.is_golden_match_allowed, match_service.create_golden_match (POST match/v1/matches/create-golden-match)
  - tms scoring service team score update (checks is_golden_match_allowed after every team score save)
source_files:
  - src/app/modules/tms/fixture-tree/single-tree/single-tree.component.html
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts
  - src/app/modules/admin/playing-order-creation/playing-order-creation.component.html
  - src/app/shared/game-play-config/game-play-config.component.html
---
# Golden match

A **golden match** is an extra deciding match between two **teams** when their team match (or, with several legs, the whole tie) ends level. Nobody creates it by hand: the system creates it automatically when the scores are saved, if **Golden Game Configuration** is switched on in Game Settings.

## When is a golden match created

After every score save of a team match, the server creates the golden match only when **all** of these are true:
1. The category is a **Teams** category. Singles and doubles never get a golden match.
2. **Golden Game Configuration** is switched on in **Game Settings** for the stage or category.
3. The team match ends **level** under the point system of the stage (for example both teams win the same number of individual matches).
4. With **2 or more legs**: every leg is finished, and the legs together are level (the totals are compared across all legs, by the rules of the point system).
5. No golden match exists yet for that match.

This works in **knockout** and **group** stages. In a group stage both teams first get the tie points of the point system, and the golden match then decides the winner.

## What happens to the tied match

- With **Golden Game Configuration** on, a level team match stays **In Progress** (not finished) until the golden match is scored.
- With it off, a level team match is saved as **Scored** with a draw, and no golden match is created.

## What the system does when it is created

- A new match is added to the same round and position, marked as golden, with the **same two teams** as the legs.
- It starts **Not Started** with all sets and points at 0.
- The last leg is marked "golden match created", so the tie stays open (no winner moves to the next round) until the golden match is scored.
- The winner of the golden match wins the tie and moves on in the bracket.

## Where you see it

- **Fixtures screen (knockout bracket)**: in the match popup the legs show as tabs **Leg 1**, **Leg 2** … and a **Golden Match** tab appears next to them.
- **Scoring and Streaming**: the tie gets a golden icon, and a **Golden** tab opens the golden match sub matches for scoring.
- **Leaderboard (teams)**: a **G** column and a golden marker appear when the category has golden matches.
- Printing, the LED live card (a **G** badge) and the stream overlay (**Golden** label) also mark it.

## Which individual matches are played in it

- The sub matches of a golden match come from the **Golden Match Order** of the playing order format: "Add a golden match order that is only a part of the created playing order. (Performed on tie between the teams)".
- It is set in **Playing Order Configuration** (admin manage menu → Playing Orders), where you also **Choose Selection Type for Golden Match**: **Single Player** or **Multi Player**.
- If the format has no Golden Match Order, the golden match has no sub match line-up to fill.
- When picking the golden match players in **Scoring and Streaming**, one side may be saved while the other is still empty. The same player cannot fill both slots of one side: "Golden Match #n: Same participant selected for both slots on Side A." (or Side B).

## Points for a golden match (Game Settings)

In **Game Settings** on the Fixtures screen (or the event's Game Play page, Result Management):
- **Win After Tie (Golden Match)** in Point System Configuration – standing points for a team that wins after a tie through the golden match.
- **Golden Match** under the **Match Point System** / **Set Point System** (Teams) – points per golden match or set.
- **Golden Game Configuration** (Teams) – how the golden game is played: set-wise (players picked set by set) or point-wise ("multiple players participate in a single set, with dedicated end point").

## Why no golden match was created

- The category is not **Teams**.
- **Golden Game Configuration** is off in Game Settings, so a level match is saved as a draw.
- The match (or the legs together) is not level under the point system.
- With several legs: a leg is still **not finished** (not started, in progress, walkover not saved).
- A golden match already exists for that match.

## Frequently asked questions about golden matches

**When is a golden match created?** Automatically, when a Teams match (or all its legs together) ends level and **Golden Game Configuration** is on in Game Settings.

**What is the logic for golden matches?** After each team score save the server checks: Teams category, Golden Game Configuration on, the match (or all legs together, once every leg is finished) level under the point system, and no golden match yet. If all are true it adds a Not Started golden match between the same two teams; its winner wins the tie.

**Can I create a golden match manually?** No, there is no button for it; it is created by the system when the legs end level.

**Who plays in the golden match?** The same two teams. The individual matches follow the Golden Match Order of the playing order format.

**Can a group stage have a golden match?** Yes. When Golden Game Configuration is on and a Teams group match ends level, both teams get the tie points and a golden match decides the winner. With it off, the match stays a draw and the standings use Winner Comparison and Winner Basis.

**Is a golden match the same as the golden point?** No. The golden point (Golden Point System) is a scoring rule inside a game (next point wins at deuce); the golden match is an extra team match that breaks a level knockout tie.
