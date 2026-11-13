---
doc_id: tms.score-stream.badminton
title: Scoring and Streaming for Badminton – games, deuce, sudden death cap, decider and fast entry
routes:
  - tms/score-stream/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
sports: [badminton]
aliases:
  - badminton score
  - badminton scoring
  - badminton deuce
  - badminton 21 points
  - badminton cap
  - badminton sudden death
  - badminton golden point
  - badminton decider game
  - badminton invalid score
  - badminton walkover
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I enter a badminton score?
  - When is a badminton game won?
  - What is the cap in badminton scoring?
  - Why is 21-20 not accepted in badminton?
  - What is the difference between the standard and golden rule in badminton?
  - How does the decider game work in badminton?
  - Why does the cursor move on after two digits in badminton?
  - Why am I seeing "Wrong score input for set"?
  - Why does the system say "Set exceeded"?
  - Can I enter scores after recording a walkover?
  - What does "Wrong Data Input" mean in badminton?
backend_sources:
  - gateway/src/routers/scoring_router.py (update_score)
  - tms/src/utils/scoring/calculators/badminton.py (BadmintonScoreCalculator)
  - tms/src/utils/scoring/strategies/register_strategies.py (sport 4)
source_files:
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts
  - src/app/modules/tms/score-and-streaming/score-input-feedback.util.ts
  - src/app/modules/tms/score-and-streaming/redundant-set.util.ts
  - src/assets/i18n/en.json
  - src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts
  - src/app/shared/game-play-config/game-play-config.defaults.ts
answer_notes: |
  Answering guidance for the TMS assistant:
  1. Identify whether the user is asking about a normal game, the cap, the decider, fast entry, a validation message, or a walkover/disqualification.
  2. Explain the applicable rule in plain language before giving the technical message.
  3. When a score is rejected, ask for or use the game number, entered score, and relevant Game Play settings if those details are available.
  4. If the rule configuration is unknown, explain the standard default and clearly state that the event's configured settings may differ.
  5. Do not invent decider points, cap values, match formats, reset restrictions, or causes for generic validation errors.
  6. Distinguish **games** from the word **sets** when helpful: the interface/backend may use "set" in messages even though this guide describes badminton games.
  7. Treat the server's validation result as authoritative for whether a submitted score was saved.
---

# Scoring and Streaming for Badminton

## Scope and source of truth

This guide applies to events whose sport is **Badminton (sport ID 4)**. It documents the scoring rules the server applies when a badminton score is saved, and the score-entry interface.

The server validates a score when it is saved. If the interface appears to accept an entry but saving fails, use the server validation message and the configured Game Play rules to diagnose the rejection.

This document covers badminton game scoring, standard and golden rules, the sudden-death cap, decider-game settings, fast score entry, validation messages, walkovers, and disqualifications. It does not describe every tab or control on the Scoring and Streaming page.

## Quick answers

- **Game target:** 21 points, unless **Points to win per game** (Game Level Rules) sets another value.
- **Standard rule:** A game is won at the target or later with a two-point lead, subject to any configured cap.
- **Golden rule:** No deuce; the first side to reach the target wins, so 21–20 is valid.
- **Cap:** A configured **Max Point** ends a long deuce, but the loser must be within two points of it.
- **Decider:** The last game can use its own decider points, always without deuce.
- **Whole match required:** A score saved on this page must decide the match.
- **Fast entry:** For badminton, the cursor advances after two digits are entered in a score box.
- **Walkover/disqualification:** Save the reason and let the server set the result; game scores are not needed.

## How a badminton match is scored

A match consists of multiple games. In the system, games may be labelled as **sets** in validation messages.

1. Enter the points for side A and side B for each game.
2. Each score box accepts at most two digits.
3. With **ST** the match is won by the side that first wins the majority of games; with **SP** every game is played.
4. Every game entered must be finished, and the games together must decide the match. A partial match (for example only one game of a best of three) is refused with "Wrong Data Input".
5. With ST, games entered after the match is decided are ignored by the server.

## The two game rules

### Standard rule (deuce; default)

A side wins at the target (21 by default) with at least a two-point lead. From 20–20, play continues until one side leads by exactly two points.

Examples: **21–19**, **22–20** and **23–21** are valid; **21–20** is not a final score; **22–19** is rejected because the game ended at 21–19.

### Golden rule (simple)

Chosen with **Golden Point System**. There is no deuce: the first side to reach the target wins, so **21–20 is valid**. A score above the target is refused, and the cap does not apply.

## The cap (sudden death)

The cap is the **Max Point** of **Sudden Death Point** (standard rule only), for example 30.
- No side may score above the cap, and both sides cannot be on it.
- A score on the cap wins only if the loser is within two points: **30–29** and **30–28** are valid; **30–27** is invalid; **30–30** is invalid.

Without a cap, the two-point lead continues with no upper limit. Do not assume that every event uses a cap or that the cap is always 30; use the event's configured Game Play settings.

## The decider game

With **Decider set** on, the last game of the match (for example game 3 of a best of three) uses the decider **Point** as its target and is played without deuce: the first side to reach it wins, no higher score is accepted and the cap does not apply. Without a decider Point, the normal game target is used.

Do not assume a specific decider-point value unless it is available in the event's settings.

## Valid and rejected scores: standard rule, 21 points, no cap

| Score | Result | Reason |
|---|---|---|
| 21–0 through 21–19 | Valid winning score | The winner reaches 21 and leads by at least two |
| 21–20 | Rejected as final score | Only a one-point lead |
| 21–21 | Rejected as final score | No winner |
| 22–20 | Valid winning score | Two-point lead after deuce |
| 23–21 | Valid winning score | Two-point lead after deuce |
| 22–19 | Rejected as final score | The game should already have ended at 21–19 |

Under the golden rule, **21–20 is a valid winning score**. A different game target, cap or decider setting changes which result is accepted.

## Special rule (SP) in badminton

- Every game must be played. A game left at 0–0 is refused: "Under Special Rule, all configured sets must be completed before saving the match. Set {n} was not played."
- The winner is the side with more games. If the games are level, the side with more total points wins; equal points make the match a tie.

## Fast score entry

Badminton uses a sport-specific cursor behavior:

1. Enter two digits for side A; the cursor moves to side B.
2. Enter two digits for side B; the cursor moves to the next game's score.
3. Continue entering scores without clicking each box.

This two-digit auto-advance behavior is specific to badminton. Other sports may advance the cursor according to different rules. If the cursor moves before you expect it to, check whether the current box has received two digits.

## Validation messages and troubleshooting

### "Wrong score input for set {set_number}"

**Meaning:** The score for the named game is not a finished game under the configured badminton rules, or the game number is beyond the match format.

**Check:** the two-point lead of the standard rule, the golden rule, the game target, the cap and the decider points, and whether the score would have ended the game earlier.

Example: 21–20 is rejected under the standard rule but accepted under the golden rule.

### "Set exceeded"

**Meaning:** More games were entered than the match format allows. Remove the extra games.

### "Wrong Data Input"

**Meaning:** The games entered are each valid but do not decide the match (for example one game of a best of three, or 1–1 in games). On screen this appears as "The submitted set scores do not match the configured number of sets."

**What to do:** Enter the remaining games until one side has won the match.

## Validation messages and troubleshooting – badminton scoring (2)

### All games required (Special rule)

Under SP, a game left at 0–0 is refused with "Under Special Rule, all configured sets must be completed before saving the match. Set {n} was not played." The page shows this text as the server sends it.

### "Match Already Walkover Reset First"

**Meaning:** The match has a recorded walkover and cannot accept new game scores until the walkover is cleared.

### Reset refused

"Cannot reset a match that has not started" means the match has no score. "Reset blocked because of an active forfeit" means a player has an active forfeit.

### "Score Updated Successfully"

**Meaning:** The score was saved.

## Walkovers and disqualifications

A walkover or disqualification is saved with its reason, and the server sets the result: the walkover winner is given the games needed to win (ST) or all games (SP) at the game target, the loser none. A double walkover is saved as a tie.

- Team matches do not offer the **Double Walkover** option.
- A match with a recorded walkover cannot accept new game scores until the walkover is cleared ("Match Already Walkover Reset First").

Do not recommend entering placeholder game scores for a walkover or disqualification; save the reason and let the server set the result.

## Badminton score messages as shown on screen

| Server message | Shown on screen |
|---|---|
| Wrong Data Input | The submitted set scores do not match the configured number of sets. |
| Wrong score input for set {n} | Shown as is. |
| Set exceeded | Shown as is. |
| Under Special Rule, all configured sets must be completed … | Shown as is. |

For Badminton the page does not reject a game while you type; all checks happen when you click **Save**. After a save that decides the match, the **Winner Confirmation** popup opens; **Cancel** there clears the saved score.

Once the entered sets decide the match, later empty sets are locked; a later set that still holds a score blocks saving with "Invalid Score: Set {n} cannot be scored because the match has already concluded." (not when the rules play every set).

## Frequently asked questions

### How do I enter a badminton score?

Enter side A and side B points for each game until the match is decided, then click **Save**. The cursor advances automatically after two digits in a box.

### When is a badminton game won?

At the game target (21 by default) with a two-point lead. Under the golden rule, the first side to reach the target wins without deuce. A cap or decider setting can change the end condition.

### Why is 21–20 not accepted?

Under the standard rule, the winner must lead by two points, so 21–20 is not final; play continues to 22–20 or another two-point margin. Under the golden rule, 21–20 is accepted.

### What is the cap in badminton scoring?

The configured Max Point of Sudden Death Point. Nobody may go above it, and a score on it is valid only when the loser is within two points (30–29 or 30–28 with a cap of 30).

### What is the difference between the standard and golden rules?

- **Standard:** Deuce applies; a two-point lead is required.
- **Golden:** No deuce; the first side to reach the target wins, making 21–20 valid at a target of 21.

### How does the decider game work?

The last game of the match is played to the decider Point without deuce, and the cap does not apply. Check the configured decider points rather than assuming a fixed value.

## Frequently asked questions – badminton scoring (2)

### Why does the cursor move on after two digits?

That is the fast-entry behavior for badminton: two digits move the cursor from side A to side B, and two digits in side B move it to the next game.

### Can I save a badminton match that is not finished?

No. On this page a badminton score must decide the match; otherwise the server answers "Wrong Data Input" (shown as "The submitted set scores do not match the configured number of sets.").

### Can I enter scores after recording a walkover?

Not until the walkover is cleared. The server returns **"Match Already Walkover Reset First"** while the walkover remains recorded.

### Why am I seeing "Wrong score input for set"?

The score for that game is not a finished game under the configured badminton rules. Check the two-point lead, the golden rule, the game target, the cap and the decider points.

### Why does the system say "Set exceeded"?

More games were entered than the match format allows. Remove the extra games.

### What does "Wrong Data Input" mean in badminton?

The games entered do not decide the match yet. Enter the remaining games until one side has won.

## Natural-language and Hinglish query patterns

Treat the following as equivalent intents when retrieving this document:

- "Badminton ka score kaise dalun?"
- "21-20 accept kyun nahi ho raha?"
- "Badminton mein deuce kab lagta hai?"
- "Golden rule aur standard rule mein kya difference hai?"
- "Badminton ka cap kya hota hai?"
- "Decider game ka score alag hota hai kya?"
- "Score type karte hi cursor aage kyun chala jaata hai?"
- "Wrong score input for set ka matlab kya hai?"
- "Set exceeded error kyun aa raha hai?"
- "Walkover ke baad score update kyun nahi ho raha?"
- "Wrong Data Input ka kya matlab hai?"

## Source references

- Backend score update: `gateway/src/routers/scoring_router.py` (`update_score`)
- Badminton scoring calculator: `tms/src/utils/scoring/calculators/badminton.py` (`BadmintonScoreCalculator`)
- Sport strategy registration: `tms/src/utils/scoring/strategies/register_strategies.py` (sport ID 4)
- Score entry UI: `src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts`
- Score feedback constants: `src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts`
- Game Play defaults: `src/app/shared/game-play-config/game-play-config.defaults.ts`
