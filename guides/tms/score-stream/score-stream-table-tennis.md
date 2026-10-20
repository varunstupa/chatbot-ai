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
  - src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts
  - src/app/shared/game-play-config/game-play-config.defaults.ts
---

# Scoring and Streaming for Table Tennis

## Scope and source of truth

This guide applies to **Table Tennis (sport ID 1)**. It explains table tennis score entry, game-winning rules, deuce, golden point, sudden death, decider settings, and common validation messages.

The server checks the score when it is saved. If a score is rejected, use the validation message and the event's configured Game Play rules to investigate. In the system, a game may be referred to as a **set** in validation messages.

## Quick reference

- **Default target:** 11 points per game.
- **Standard rule (deuce):** A side must reach the target and lead by two points.
- **Golden point (simple rule):** The first side to reach the target wins; no two-point lead is needed.
- **Sudden death (cap):** Reaching the configured death point wins immediately, even without a two-point lead, subject to the documented restrictions.
- **Decider game:** The last game can use its own target and the golden rule.
- **Score entry:** Enter side A and side B points for each game, then select **Update**.
- **Fast entry:** The cursor advances when the game appears complete under its rules. The two-digit auto-advance behavior is specific to Badminton, not Table Tennis.

## How a table tennis match is scored

A match consists of multiple games. In the system, these games may be called **sets** in error messages.

1. Enter the points for side A and side B in each game's score boxes.
2. Each score box accepts at most two digits.
3. The match is won by the side that wins the majority of games.
4. Once the match winner is decided, do not enter later games.

The default game target is 11 points. A game's accepted final score depends on the applicable Game Play rule.

## The three ways a game can be won

### Standard rule (deuce; default)

A game is won at the target with a two-point lead. At 10–10, the game continues until one side leads by two points.

Examples:
- **11–9:** valid winning score.
- **11–10:** not a valid final score.
- **12–10:** valid winning score.
- **13–11:** valid winning score.

### Golden point (simple rule)

There is no deuce. The first side to reach the configured target wins the game outright. The Game Play setting for this rule is the **rule point**.

For a target of 11, this means a score such as **11–10** can be accepted under the golden-point rule.

### Sudden death (cap)

When a death point is configured, reaching that point wins the game immediately, even without a two-point lead.

The documented restrictions are:
- The opposing side cannot be on the same death-point score.
- No score can go above the configured death point.

Do not assume a specific death-point value unless it is available in the event's Game Play settings.

## Valid scores under the standard rule (target 11)

| Score | Classification | Reason |
|---|---|---|
| 11–0 through 11–9 | Valid winning score | The winner reaches 11 and leads by at least two |
| 11–10 | Invalid as a final score | The winner has only a one-point lead |
| 12–10 | Valid winning score | Two-point lead after deuce |
| 13–11 | Valid winning score | Two-point lead after deuce |
| 12–11 | Invalid as a final score | Only a one-point lead |
| 12–9 | Invalid as a final score | The game should already have ended at 11–9 |

For live scoring, a score can be in progress while neither side has yet won. The final score must follow the selected rule. These examples assume a target of 11 and the standard rule.

## The decider game

The last game of the match can use its own target, configured as **Decider set** points, and use the golden rule with no deuce.

Enter the decider game in the same way as other games, but apply the decider settings for that game. Do not assume a particular decider target if the configured value is not available.

## Validation messages and troubleshooting

### "Wrong score input for set {set_number}"

**Meaning:** The two scores do not form a valid result for that game under the configured rules.

**Check:**
- Whether the game has a valid final score.
- Whether the standard rule requires a two-point lead.
- Whether the golden-point rule or sudden-death cap is configured.
- Whether the decider game uses a different target.
- Whether the entered score would have ended the game earlier.

Example: **11–10** is rejected as a final score under the standard rule, but may be accepted under the golden-point rule.

### "Set exceeded"

**Meaning:** More games/sets were entered than the match allows.

**What to do:** Check the match format and remove scores for games beyond the allowed number or after the match winner has already been determined.

### "Score Updated"

**Meaning:** The score was saved successfully.

### "Match Already Walkover Reset First"

**Meaning:** A walkover is recorded, and new game scores cannot be entered until the walkover is reset.

**What to do:** Reset the walkover first if the match is meant to be played and scored.

### "Match Data Not Reset"

**Meaning:** A match reset operation is blocked.

The source material does not specify every condition that blocks a reset. Check the match state and applicable configuration; do not assume a specific cause from this message alone.

## Walkovers and disqualifications

A walkover or disqualification is saved with its reason. The server sets the match result, so game-by-game scores are not required for that result.

A match with a recorded walkover cannot accept new game scores until the walkover is reset. If the system returns **"Match Already Walkover Reset First"**, check whether the walkover still needs to be reset.

## Entering scores quickly

The cursor moves on when the game appears complete under the configured rules, allowing the scorer to enter games in sequence without clicking each box.

The **two-digit auto-advance behavior is specific to Badminton** in the documented interface. Do not explain that behavior as a Table Tennis feature.

## Messages (table tennis)

- **"Wrong score input for set {set_number}"** — the game score is invalid under the configured rules.
- **"Set exceeded"** — more games were entered than the match allows.
- **"Score Updated"** — the score was saved.
- **"Match Already Walkover Reset First"** — the walkover must be reset before new game scores can be entered.
- **"Match Data Not Reset"** — the match reset operation is blocked; the exact cause is not specified here.

## Frequently asked questions

### How do I enter a table tennis score?

Enter the points for side A and side B for each game, then select **Update**. Enter only the games needed to determine the match result.

### When is a game won?

By default, a game is won at 11 points with a two-point lead. Under the golden-point rule, the first side to reach the target wins outright. Under sudden death, reaching the configured death point wins immediately, subject to the documented restrictions.

### What is deuce in table tennis?

At 10–10 under the standard rule, the game continues until one side leads by two points. For example, 12–10 is a valid final score, while 11–10 is not.

### Why does "Wrong score input for set 1" appear?

The score does not form a valid game result under the configured rules. For example, 11–10 is invalid as a final score under the standard rule. Continue the game if it is still in progress, or check the golden-point, sudden-death, and decider settings.

### What is the golden-point rule?

The first side to reach the configured target wins the game. No two-point lead is required.

### What is sudden death in table tennis?

Sudden death means reaching the configured death-point score wins immediately, even without a two-point lead. The opposing side cannot be on the same death-point score, and the score cannot go above the configured death point.

### How does the decider game work?

The last game can use its own configured target and the golden-point rule, with no deuce. Check the event's Decider set points setting for the actual target.

### Can I enter scores after recording a walkover?

Not until the walkover is reset. The server rejects new game scores while the walkover remains recorded.

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

## Answering guidance for the TMS assistant

1. Identify whether the user is asking about standard scoring, golden point, sudden death, the decider game, fast entry, or a validation message.
2. Explain the applicable rule in plain language before discussing the error message.
3. When diagnosing a rejected score, use the entered score and the event's configured Game Play settings if available.
4. If the rule configuration is unknown, explain the default target and standard rule, and clearly state that event settings may differ.
5. Do not invent a death-point value, decider target, match format, or reset restriction not specified by the source.
6. Clarify that the backend may call a game a "set" in its validation messages.
7. Do not attribute Badminton's two-digit auto-advance behavior to Table Tennis.
8. Treat the server's validation result as authoritative for whether a submitted score was accepted.

## Source references

- Backend score update: `gateway/src/routers/scoring_router.py` (`update_score`)
- Table Tennis scoring calculator: `tms/src/utils/scoring/calculators/table_tennis.py` (`TableTennisScoreCalculator`)
- Sport strategy registration: `tms/src/utils/scoring/strategies/register_strategies.py` (sport ID 1)
- Score entry UI: `src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts`
- Score feedback constants: `src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts`
- Game Play defaults: `src/app/shared/game-play-config/game-play-config.defaults.ts`
