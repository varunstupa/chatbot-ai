---
doc_id: tms.score-stream.table-tennis
title: Scoring and Streaming for Table Tennis – games, deuce, sudden death, decider and errors
routes:
  - tms/score-stream/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
sports: [table_tennis]
aliases:
  - table tennis score
  - table tennis scoring
  - tt score entry
  - table tennis deuce
  - table tennis game point
  - table tennis golden point
  - table tennis sudden death
  - table tennis decider score
  - table tennis invalid score
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I enter a table tennis score?
  - When is a table tennis game won?
  - What is deuce in table tennis scoring?
  - What does "Wrong score input for set 1" mean in table tennis?
  - What is the golden point rule in table tennis?
  - How does the decider game work in table tennis?
  - What is sudden death in table tennis?
  - Why does the system say "Set exceeded"?
  - Can I change scores after recording a walkover?
  - Why is a table tennis score rejected?
backend_sources:
  - gateway/src/routers/scoring_router.py (update_score)
  - tms/src/utils/scoring/calculators/table_tennis.py (TableTennisScoreCalculator)
  - tms/src/utils/scoring/strategies/register_strategies.py (sport 1)
source_files:
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts
  - src/app/modules/tms/score-and-streaming/score-input-feedback.util.ts
  - src/app/modules/tms/score-and-streaming/redundant-set.util.ts
  - src/assets/i18n/en.json
  - src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts
  - src/app/shared/game-play-config/game-play-config.defaults.ts
answer_notes: |
  Answering guidance for the TMS assistant:
  1. Identify whether the user is asking about standard scoring, golden point, sudden death, the decider game, fast entry, or a validation message.
  2. Explain the applicable rule in plain language before discussing the error message.
  3. When diagnosing a rejected score, use the entered score and the event's configured Game Play settings if available.
  4. If the rule configuration is unknown, explain the default target and standard rule, and clearly state that event settings may differ.
  5. Do not invent a death-point value, decider target, match format, or reset restriction not specified by the source.
  6. Clarify that the backend may call a game a "set" in its validation messages.
  7. Do not attribute Badminton's two-digit auto-advance behavior to Table Tennis.
  8. Treat the server's validation result as authoritative for whether a submitted score was accepted.
---

# Scoring and Streaming for Table Tennis

## Scope and source of truth

This guide applies to **Table Tennis (sport ID 1)**. It explains table tennis score entry, game-winning rules, deuce, golden point, sudden death, decider settings, and common validation messages.

The server checks the score when it is saved. If a score is rejected, use the validation message and the event's configured Game Play rules to investigate. In the system, a game may be referred to as a **set** in validation messages.

## Quick reference

- **Game target:** 11 points. The server always uses 11 for table tennis games.
- **Standard rule (deuce):** A side must reach 11 and lead by two points.
- **Golden point:** The first side to reach 11 wins; no two-point lead is needed and no score above 11 is accepted.
- **Sudden death (cap):** Reaching the configured **Max Point** wins the game, subject to the restrictions below.
- **Decider game:** The last game of the match can use its own target, always without deuce.
- **Score entry:** Enter side A and side B points for each game, then click **Save**.
- **Fast entry:** The cursor advances when the game appears complete under its rules. The two-digit auto-advance behavior is specific to Badminton, not Table Tennis.

## How a table tennis match is scored

A match consists of multiple games. In the system, these games may be called **sets** in error messages.

1. Enter the points for side A and side B in each game's score boxes.
2. Each score box accepts at most two digits.
3. With **ST** the match is won by the side that first wins the majority of games. With **SP** every game is played.
4. Every game you enter must be a finished game. An unfinished game (for example 8–5 or 10–10) is refused with "Wrong score input for set {n}".
5. You may save before the match is decided (for example two games of a best of five); the match then stays **In Progress**. A score that decides the match sets it to **Scored**.
6. With ST, games entered after the match is already decided are ignored by the server.

## The three ways a game can be won

### Standard rule (deuce; default)

A game is won at 11 with a two-point lead. From 10–10 the game continues until one side leads by exactly two points.

Examples: **11–9**, **12–10** and **13–11** are valid; **11–10** and **12–11** are not final scores; **12–9** is refused because the game ended at 11–9.

### Golden point

Chosen with **Golden Point System**. There is no deuce: the first side to reach 11 wins, so **11–10** is valid. A score above 11 is refused. Sudden death does not apply under this rule.

### Sudden death (cap)

Turned on with **Sudden Death Point** (**Max Point**) under the standard rule:
- No side may score above the Max Point, and both sides cannot be on it.
- When the Max Point is 11 or more, a score on it wins only if the loser is within two points. Example with Max Point 15: **15–14** and **15–13** win; **15–12** is refused.
- When the Max Point is below 11, reaching it wins at any score of the opponent.

Do not assume a specific Max Point unless it is shown in the event's Game Play settings.

## Valid scores under the standard rule (target 11)

| Score | Classification | Reason |
|---|---|---|
| 11–0 through 11–9 | Valid winning score | The winner reaches 11 and leads by at least two |
| 11–10 | Invalid as a final score | The winner has only a one-point lead |
| 12–10 | Valid winning score | Two-point lead after deuce |
| 13–11 | Valid winning score | Two-point lead after deuce |
| 12–11 | Invalid as a final score | Only a one-point lead |
| 12–9 | Invalid as a final score | The game should already have ended at 11–9 |

For live scoring, a score can be in progress while neither side has yet won. These examples assume no sudden death.

## The decider game

With **Decider set** on, the last game of the match (for example game 5 of a best of five) uses the decider **Point** as its target and is played without deuce: the first side to reach it wins and no higher score is accepted. Without a decider Point, the target stays 11.

The decider rule only applies to the last possible game, not to an earlier game that happens to decide the match.

## Special rule (SP) in table tennis

- Every game must be played. A game left at 0–0 is refused: "Under Special Rule, all configured sets must be completed before saving the match. Set {n} was not played."
- The winner is the side with more games. If the games are level (an even number of games), the side with more total points wins; equal points make the match a tie.

## Validation messages and troubleshooting

### "Wrong score input for set {set_number}"

**Meaning:** The two scores do not form a finished game under the configured rules, or the game number is beyond the match format.

**Check:**
- Whether the game has a valid final score (two-point lead under the standard rule).
- Whether golden point, sudden death or the decider game is configured.
- Whether the entered score would have ended the game earlier.

Example: **11–10** is rejected under the standard rule, but accepted under the golden-point rule.

### "Set exceeded"

**Meaning:** More games were entered than the match format allows.

**What to do:** Check the match format and remove the extra games.

### "Score Updated Successfully"

**Meaning:** The score was saved.

### "Match Already Walkover Reset First"

**Meaning:** A walkover is recorded, and new game scores cannot be entered until the walkover is cleared.

### Reset refused

"Cannot reset a match that has not started" means the match has no score. "Reset blocked because of an active forfeit" means a player has an active forfeit.

## Walkovers and disqualifications

A walkover or disqualification is saved with its reason. The server sets the result: the walkover winner is given the games needed to win (ST) or all games (SP) at 11–0. A double walkover is saved as a tie with no game scores.

A match with a recorded walkover cannot accept new game scores until the walkover is cleared ("Match Already Walkover Reset First").

## Entering scores quickly

The cursor helps the scorer enter games in sequence without clicking each box:
- In side A, a value above 1 (while side B is still empty) moves the cursor straight to side B.
- In side B, the cursor moves to the next game when the game looks finished on an 11-point game: 11 against 9 or less, or both sides at 10 or more with a two-point lead.

The cursor always uses this 11-point logic; it does not follow golden point, the cap or the decider target. The server still validates the score against the configured rules when you click **Save**.

The **two-digit auto-advance behavior is specific to Badminton**. Do not explain that behavior as a Table Tennis feature.

## Table tennis score messages as shown on screen

The table tennis messages appear on screen as the server sends them:
- "Wrong score input for set {n}"
- "Set exceeded"
- "Under Special Rule, all configured sets must be completed before saving the match. Set {n} was not played."
- "Match Already Walkover Reset First"
- "Score Updated Successfully"

For Table Tennis the page does not reject a game while you type; all checks happen when the score is saved. After a successful save that decides the match, the **Winner Confirmation** popup opens; **Cancel** there clears the saved score.

Once the entered sets decide the match, later empty sets are locked; a later set that still holds a score blocks saving with "Invalid Score: Set {n} cannot be scored because the match has already concluded." (not when the rules play every set).

## Frequently asked questions

### How do I enter a table tennis score?

Enter the points for side A and side B for each game, then click **Save**. Each game you enter must be finished.

### When is a game won?

At 11 points with a two-point lead (standard rule). Under the golden-point rule the first side to 11 wins. Under sudden death, a score on the Max Point wins when the loser is within two points.

### What is deuce in table tennis?

At 10–10 under the standard rule, the game continues until one side leads by two points. For example, 12–10 is a valid final score, while 11–10 is not.

### Why does "Wrong score input for set 1" appear?

The score is not a finished game under the configured rules. For example, 11–10 is invalid under the standard rule. Check the golden-point, sudden-death and decider settings.

### What is the golden-point rule?

The first side to reach 11 wins the game. No two-point lead is required and no score above 11 is accepted.

### What is sudden death in table tennis?

A Max Point that ends a long deuce. Nobody may go above it, both sides cannot be on it, and (for a Max Point of 11 or more) the loser must be within two points, for example 15–14 or 15–13 with Max Point 15.

## Frequently asked questions – table tennis scoring (2)

### How does the decider game work?

The last game of the match is played to the decider **Point** without deuce. Check the event's Decider set setting for the actual target.

### Can I save a match that is not finished?

Yes, in table tennis. Enter the finished games and save; the match stays In Progress until a later save decides it.

### Can I enter scores after recording a walkover?

Not until the walkover is cleared. The server answers "Match Already Walkover Reset First".

### What does "Wrong score input for set 1" mean in table tennis?

The score does not form a finished game under the configured rules. For example, 11–10 is invalid under the standard rule. Check the golden-point, sudden-death and decider settings.

### Why does the system say "Set exceeded"?

More games were entered than the match format allows. Remove the extra games.

### Why is a table tennis score rejected?

The entered points do not form a finished game under the Game Play rules (games to 11). Check the two-point lead of the standard rule, golden point, sudden death and the decider game.

## Natural-language and Hinglish query patterns

Treat these as equivalent intents when retrieving this document:

- "Table tennis ka score kaise dalun?"
- "TT mein game jeetne ke liye kitne points chahiye?"
- "10-10 ke baad kya hota hai?"
- "11-10 final score kyun accept nahi ho raha?"
- "Golden point rule kya hai?"
- "Sudden death ya cap ka matlab kya hai?"
- "Decider game ka target kahan check karun?"
- "Wrong score input for set 1 ka matlab kya hai?"
- "Set exceeded error kyun aa raha hai?"
- "Walkover ke baad score update kyun nahi ho raha?"
- "Cursor automatically next game par kyun ja raha hai?"

## Source references

- Backend score update: `gateway/src/routers/scoring_router.py` (`update_score`)
- Table Tennis scoring calculator: `tms/src/utils/scoring/calculators/table_tennis.py` (`TableTennisScoreCalculator`)
- Sport strategy registration: `tms/src/utils/scoring/strategies/register_strategies.py` (sport ID 1)
- Score entry UI: `src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts`
- Score feedback constants: `src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts`
- Game Play defaults: `src/app/shared/game-play-config/game-play-config.defaults.ts`
