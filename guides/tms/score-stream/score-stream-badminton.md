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
  - What does "Match Data Not Reset" mean?
backend_sources:
  - gateway/src/routers/scoring_router.py (update_score)
  - tms/src/utils/scoring/calculators/badminton.py (BadmintonScoreCalculator)
  - tms/src/utils/scoring/strategies/register_strategies.py (sport 4)
source_files:
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts
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

This guide applies to events whose sport is **Badminton (sport ID 4)**. It documents the scoring behavior described by the badminton calculator and the score-entry interface.

The server validates a score when it is saved. If the interface appears to accept an entry but saving fails, use the server validation message and the configured Game Play rules to diagnose the rejection.

This document covers badminton game scoring, standard and golden rules, the sudden-death cap, decider-game settings, fast score entry, validation messages, walkovers, and disqualifications. It does not describe every tab or control on the Scoring and Streaming page.

## Quick answers

- **Default game target:** 21 points.
- **Standard rule:** A game is won at 21 or later with a two-point lead, subject to any configured cap.
- **Golden rule:** No deuce; the first side to reach 21 wins, so 21–20 is valid.
- **Cap:** A configured maximum/death-point score can end a game, but the winner must be within the cap's two-point lead condition.
- **Decider:** The last game can use its own decider points and the golden rule, with no deuce.
- **Fast entry:** For badminton, the cursor advances after two digits are entered in a score box.
- **Walkover/disqualification:** Save the reason and let the server set the result; game scores are not needed.

## How a badminton match is scored

A match consists of multiple games. In the system, games may be labelled as **sets** in validation messages.

1. Enter the points for side A and side B for each game.
2. Each score box accepts at most two digits.
3. The match is won by the side that wins the majority of games.
4. Stop entering games once the match winner is determined; later games are not entered.

The default target for a game is 21 points. The actual result must satisfy the configured rule for that game.

## The two game rules

### Standard rule (deuce; default)

A side wins at 21 only if it leads by two points. At 20–20, play continues until one side has a two-point lead.

Examples:
- **21–19:** valid winning score.
- **21–20:** not a valid final score under the standard rule.
- **22–20:** valid winning score.
- **23–21:** valid winning score.

If a side has already won at an earlier score, a later score is not valid as that game's final result. For example, **22–19** is rejected because the game would already have ended at 21–19.

### Golden rule (simple)

There is no deuce. The first side to reach 21 wins the game outright.

For example, **21–20 is valid** under the golden rule.

## The cap (sudden death)

A game can have a configured cap, also described as death points. For example, the cap may be set to 30.

At the cap, the winner must satisfy the configured two-point lead condition:
- **30–29:** valid.
- **30–28:** valid.
- **30–27:** invalid.
- **30–30:** invalid.

Without a cap, the standard two-point-lead rule continues to apply.

Do not assume that every event uses a cap or that the cap is always 30; use the event's configured Game Play settings.

## The decider game

The final game of a match can have its own **decider points** and use the **golden rule**, meaning no deuce. Enter the decider score in the same score-entry interface as other games.

Use the configured decider settings when explaining the target score. Do not assume a specific decider-point value unless it is available in the event's settings.

## Valid and rejected scores: standard rule, 21 points, no cap

| Score | Result | Reason |
|---|---|---|
| 21–0 through 21–19 | Valid winning score | The winner reaches 21 and leads by at least two |
| 21–20 | Rejected as final score | Only a one-point lead |
| 21–21 | Rejected as final score | No winner |
| 22–20 | Valid winning score | Two-point lead after deuce |
| 23–21 | Valid winning score | Two-point lead after deuce |
| 22–19 | Rejected as final score | The game should already have ended at 21–19 |

Under the golden rule, **21–20 is a valid winning score**.

These examples assume the standard target of 21 and no cap. A configured golden rule, cap, or decider setting can change which result is accepted.

## Fast score entry

Badminton uses a sport-specific cursor behavior:

1. Enter two digits for side A; the cursor moves to side B.
2. Enter two digits for side B; the cursor moves to the next game's score.
3. Continue entering scores without clicking each box.

This two-digit auto-advance behavior is specific to badminton in the documented interface. Other sports may advance the cursor according to different rules.

If the cursor moves before you expect it to, check whether the current box has received two digits.

## Validation messages and troubleshooting

### "Wrong score input for set {set_number}"

**Meaning:** The score for the named game/set is not a valid result under the configured badminton rules.

**Check:**
- Whether the game has a valid winning score.
- Whether the standard rule requires a two-point lead.
- Whether the golden rule is configured for the game.
- Whether the configured cap or decider points affect the result.
- Whether the score would have ended the game earlier.

Example: 21–20 is rejected under the standard rule but accepted under the golden rule.

### "Set exceeded"

**Meaning:** More games/sets were entered than the match allows.

**What to do:** Check the match format and remove scores for games beyond the allowed number or beyond the point where the match winner is determined.

### "Wrong Data Input"

**Meaning:** The submitted score data is invalid.

**What to do:** Check that the score fields contain valid numeric score input and that the values satisfy the configured game rules. The message alone does not identify the exact field or rule that failed.

### All-games-required validation

The system can reject a save if every required game has not been entered. The documented validation message does not yet have English text, so the interface may display a raw translation key instead of a readable sentence.

### "Match Already Walkover Reset First"

**Meaning:** The match has a recorded walkover and cannot accept new game scores until the walkover is reset.

**What to do:** Reset the walkover first, then enter scores if the match is meant to be played.

### "Match Data Not Reset"

**Meaning:** A match reset operation is blocked.

The source material does not specify every condition that blocks a reset. Check the match state and applicable permissions/configuration; do not infer a specific cause from this message alone.

### "Score Updated"

**Meaning:** The score was saved successfully.

## Walkovers and disqualifications

A walkover or disqualification is saved with its reason, and the server sets the result. Game-by-game scores are not needed for that result.

- Team matches do not offer the **Double Walk Over** option.
- A match with a recorded walkover cannot accept new game scores until the walkover is reset.
- If a score entry is rejected because of an existing walkover, look for **"Match Already Walkover Reset First"**.

Do not recommend entering placeholder game scores for a walkover or disqualification when the documented workflow is to save the reason and let the server set the result.

## Frequently asked questions

### How do I enter a badminton score?

Enter side A and side B points for each game, then select **Update**. In badminton, the cursor advances automatically after two digits in a box.

### When is a badminton game won?

By default, the game is won at 21 points with a two-point lead. Under the golden rule, the first side to reach 21 wins without deuce. A configured cap or decider setting can change the applicable end condition.

### Why is 21–20 not accepted?

Under the standard rule, the winner must lead by two points, so 21–20 is not final; play would continue to 22–20 or another valid two-point margin. Under the golden rule, 21–20 is accepted.

### What is the cap in badminton scoring?

The cap is the configured sudden-death/death-point limit. At the cap, the result must satisfy the documented two-point lead condition. Do not assume the cap value if it is not shown in the event settings.

### What is the difference between the standard and golden rules?

- **Standard:** Deuce applies; a two-point lead is required.
- **Golden:** No deuce; the first side to reach the target wins, making 21–20 valid at a target of 21.

### How does the decider game work?

The last game can use separate decider points and the golden rule, with no deuce. Check the configured decider points rather than assuming a fixed value.

### Why does the cursor move on after two digits?

That is the documented fast-entry behavior for badminton: two digits move the cursor from side A to side B, and two digits in side B move it to the next game.

### Can I enter scores after recording a walkover?

Not until the walkover is reset. The server returns **"Match Already Walkover Reset First"** if new game scores are submitted while the walkover remains recorded.

### Why am I seeing "Wrong score input for set"?

The score for that game is not a valid result under the configured badminton rules. Check the winning score, the two-point lead of the standard rule, the golden rule, and the cap or decider points. For example, 21–20 is rejected under the standard rule but accepted under the golden rule.

### Why does the system say "Set exceeded"?

More games were entered than the match allows. Remove the scores of games beyond the allowed number, or after the match winner was decided.

### What does "Match Data Not Reset" mean?

The reset of the match is blocked. Check the match state and your permissions; the message alone does not say which condition blocked it.

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
- "Match Data Not Reset ka kya matlab hai?"

## Source references

- Backend score update: `gateway/src/routers/scoring_router.py` (`update_score`)
- Badminton scoring calculator: `tms/src/utils/scoring/calculators/badminton.py` (`BadmintonScoreCalculator`)
- Sport strategy registration: `tms/src/utils/scoring/strategies/register_strategies.py` (sport ID 4)
- Score entry UI: `src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts`
- Score feedback constants: `src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts`
- Game Play defaults: `src/app/shared/game-play-config/game-play-config.defaults.ts`
