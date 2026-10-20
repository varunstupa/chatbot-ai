---
doc_id: tms.score-stream.padel-tennis
title: Scoring and Streaming for Padel and Tennis – sets, games, tie-breaks, super tie-break and game points
routes:
  - tms/score-stream/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
sports: [padel, tennis]
aliases:
  - tennis score
  - tennis scoring
  - padel score
  - padel scoring
  - tie break score
  - tie break entry
  - super tie break
  - decider tie break
  - game points
  - advantage score
  - deuce tennis
  - sets to win
  - play every set
  - padel best of three
  - invalid tennis set
  - invalid padel set
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I enter a tennis score?
  - How do I enter a padel score?
  - How is a tennis set won?
  - How does the tie-break work in padel and tennis?
  - What is the super tie-break?
  - What does "Advantage (50) is only valid when the opponent is at 40" mean?
  - What is the difference between ST and SP in padel and tennis?
  - Why does the scorer see "Tie-break required in set 1"?
  - Why is the super tie-break rejected?
  - Why does the match say "Match Not Concluded Insufficient Sets"?
  - Why is an advantage score rejected?
  - Why does the cursor move to the next game or tie-break boxes?
backend_sources:
  - gateway/src/routers/scoring_router.py (update_score)
  - tms/src/utils/scoring/calculators/tennis.py (TennisScoreCalculator)
  - tms/src/utils/scoring/calculators/padel.py (PadelScoreCalculator, extends the tennis calculator)
  - tms/src/utils/scoring/strategies/register_strategies.py (sport 2 and sport 3)
source_files:
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts
  - src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts
  - src/app/shared/padel-score-navigation/padel-score-navigation.engine.ts
  - src/app/shared/game-play-config/game-play-config.defaults.ts
---

# Scoring and Streaming for Padel and Tennis

## Scope and source of truth

This guide applies to **Padel (sport ID 2)** and **Tennis (sport ID 3)**. The Padel calculator extends the Tennis calculator, so the documented rules are shared unless a Padel-specific rule is changed in the implementation.

The server validates scores when they are saved. Use the server's validation response as the source of truth when a score is rejected. This guide covers match/set formats, game points, advantage, normal sets, tie-breaks, super tie-breaks, decider tie-breaks, score entry, and walkovers.

## Quick reference

- **Match:** Made up of sets.
- **Normal set:** Six games with a two-game lead, or a tie-break at 6–6 when tie-breaks are enabled.
- **Tie-break:** Normally played to 7 points with a two-point margin.
- **Super tie-break:** A tie-break to 10 points with a two-point margin that replaces the last set when the format supports it.
- **Game points:** 0, 15, 30, 40, and 50; 50 represents advantage (AD).
- **ST (Sets to win):** The match ends once one side has won the required majority of sets.
- **SP (Play every set):** Every set is played.
- **Padel set count:** Determined by the rule set count in Game Play settings, three by default.

## Match structure and set format

A match consists of **sets**, and each set consists of **games**. A set is played to six games by default, subject to the two-game margin and tie-break configuration.

### ST — Sets to win

The match is decided when one side has won the majority of sets, such as in a best-of-three or best-of-five format. Once the match is decided, another set must not be entered.

### SP — Play every set

Every configured set is played. The match winner is the side that has won more sets.

### Padel set count

For Padel, the number of sets is taken from the **rule set count** in Game Play settings, which is three by default. The Padel score submission sends the number of sets from that configured count; extra sets are dropped and missing sets are filled with zero.

Do not assume the set count is always three if the event's Game Play settings are available.

## Game points and advantage

For live game scoring, the accepted point values are:

- `0`
- `15`
- `30`
- `40`
- `50`, representing **advantage (AD)**

The server rejects game-point values outside this list with a message similar to:

`Invalid game point {game_point}: must be 0, 15, 30, 40, or 50 (AD)`

### Advantage validation

Advantage (50) is only valid when the opponent is at 40 (deuce).

- If one side has 50, the opponent must be at 40.
- Both sides cannot have advantage at the same time.

Relevant validation messages:
- `Advantage (50) is only valid when the opponent is at 40 (deuce)`
- `Both players cannot have advantage simultaneously`

If advantage is rejected, check both sides' current game-point values. Do not treat 50 as an ordinary point count; it is the system's representation of advantage.

## Winning a normal set

### Tie-breaks enabled

With tie-breaks enabled:
- Scores from **6–0 through 6–4** can win the set.
- **7–5** is a valid set result.
- **6–5** is not a final set result.
- At **6–6**, the set requires a tie-break.
- **7–6** is not the final tie-break set score by itself; the tie-break points must be entered in the tie-break boxes.

A tie-break is normally played to **7 points** with a **two-point margin**:
- **7–5:** valid tie-break result.
- **7–6:** not a valid final tie-break result.
- **8–6:** valid tie-break result.

### Tie-breaks disabled

With tie-breaks disabled, the set continues past six games until one side leads by two games. Examples include:
- **6–4**
- **7–5**
- **8–6**

Use the event's configured tie-break setting when explaining why a set was accepted or rejected.

## Tie-break score entry and errors

When a set reaches 6–6 and tie-breaks are enabled, enter the tie-break points in that set's two tie-break score boxes.

| Validation message | Meaning |
|---|---|
| `Tie-break required in set {set_number}` | The set requires a tie-break score, but none was entered. |
| `Invalid tie-break score in set {set_number}` | The tie-break score is not a valid ending score. |
| `Invalid tie-break margin in set {set_number}` | The winner does not have the required margin. |
| `Invalid tie-break overshoot in set {set_number}` | The score continued past the permitted end point. |
| `Tie-break winner does not match set winner in set {set_number}` | The side that won the tie-break does not match the side recorded as the set winner. |

If a tie-break error appears, check that the set score is 6–6, that tie-break points were entered in the correct boxes, that the score has a valid two-point margin, and that the tie-break winner matches the set winner.

## Super tie-break and decider tie-break

### Super tie-break

Where the match format supports it, a super tie-break replaces the last set. It is played to **10 points with a two-point margin**.

Related validation messages include:
- `Invalid super tie-break score in set {set_number}`
- `Invalid super tie-break margin in set {set_number}`
- `Invalid super tie-break overshoot in set {set_number}`
- `Invalid super tie-break score in last set {set_number}`

The super tie-break is only allowed when the sets before the last set are level. The source material says this rule's message does not yet have English text, so the interface may show a raw translation key.

If a super tie-break is rejected, check:
1. Whether the configured format uses a super tie-break.
2. Whether it is being entered in place of the last set.
3. Whether the sets before the last set are level.
4. Whether the tie-break score reaches the target with a two-point margin and does not overshoot the permitted end point.

### Decider tie-break

A decider tie-break is the last set's tie-break when the decider set uses different points.

Related validation messages:
- `Invalid decider set score`
- `Invalid decider set margin`
- `Invalid decider set overshoot`
- `Invalid decider set game score`

The messages may include the relevant set number. The source material does not specify the decider point target, so do not invent one; use the event's configured decider settings.

## Other score validation messages

| Message | Meaning and recommended check |
|---|---|
| `Extra set {set_number} provided after match already decided` | A set was entered after the match had already been decided. Check ST/SP and the number of sets entered. |
| `Match Not Concluded Insufficient Sets` | The entered sets do not yet decide the match. Check whether the required sets have been entered and whether the selected match format expects more sets. |
| `Wrong score input for set {set_number}` | The set score is invalid under the configured rules. Check the set result, tie-break requirements, and relevant format settings. |
| `Invalid normal set score in set {set_number}` | The normal set score is not a valid end of set. Check the two-game margin and tie-break setting. |
| `Match Already Walkover Reset First` | The match has a recorded walkover; reset it before changing set scores. |

## Entering scores and cursor navigation

- **Finished match score:** Enter the games won by each side in each set. If a set reaches a tie-break, enter the tie-break points in the tie-break boxes.
- **Live scoring:** Use the game-point entry for points such as 0, 15, 30, 40, and advantage (50).
- **Padel navigation:** The cursor follows the Padel score-navigation rules, moving after a game is complete to the next game or to the tie-break boxes.
- **Padel set submission:** The submitted number of sets follows the configured rule set count. Extra sets are dropped and missing sets are filled with zero.
- **Team matches:** The Double Walk Over option is not available.

The source material specifically describes cursor movement using the Padel navigation rules. Do not assume identical cursor behavior for Tennis unless confirmed by the implementation.

## Walkovers and disqualifications

A walkover or disqualification is saved with its reason. A walkover must be reset before set scores can be changed; otherwise the server may return:

`Match Already Walkover Reset First`

Team matches do not offer the Double Walk Over option.

## Frequently asked questions

### How do I enter a tennis score?

Enter the games won by each side for every set. If a set reaches 6–6 and tie-breaks are enabled, enter the tie-break points in the tie-break boxes. Select **Update** to save the score.

### How do I enter a Padel score?

Enter set scores and tie-break points as required by the configured format. The number of sets submitted is determined by the Padel rule set count in Game Play settings.

### How is a set won?

With tie-breaks enabled, a set can end at 6–0 through 6–4 or at 7–5. At 6–6, a tie-break is required. With tie-breaks disabled, play continues until one side leads by two games.

### What does "Tie-break required in set 1" mean?

The set reached a score that requires a tie-break, but the tie-break score was not supplied. Enter the tie-break points in the tie-break boxes for that set.

### What is a super tie-break?

A super tie-break is a single tie-break to 10 points with a two-point margin that replaces the last set when the configured format supports it.

### Why is advantage rejected?

The value 50 represents advantage. It is valid only when the opponent is at 40, and both sides cannot have advantage simultaneously.

### What is the difference between ST and SP?

- **ST (Sets to win):** The match ends when one side has won the majority of sets.
- **SP (Play every set):** Every configured set is played, and the winner is the side with more sets won.

### Why does the system say "Match Not Concluded Insufficient Sets"?

The entered sets do not yet determine the match winner. Check the selected format and whether all required sets have been entered.

## Natural-language and Hinglish query patterns

Treat these as equivalent intents when retrieving this document:

- "Tennis ka score kaise enter karun?"
- "Padel ka score kaise dalte hain?"
- "Set jeetne ke liye kitne games chahiye?"
- "6-6 ke baad tie-break score kahan dalna hai?"
- "Super tie-break kya hota hai?"
- "Advantage 50 reject kyun ho raha hai?"
- "ST aur SP mein kya difference hai?"
- "Tie-break required in set 1 ka matlab kya hai?"
- "Match Not Concluded Insufficient Sets kyun aa raha hai?"
- "Super tie-break accept kyun nahi ho raha?"
- "Walkover ke baad set score edit kyun nahi ho raha?"
- "Cursor next game ya tie-break box par kyun ja raha hai?"

## Answering guidance for the TMS assistant

1. Identify the sport (Padel or Tennis) and whether the user is entering live game points or a completed match score.
2. Determine which rule is relevant: ST/SP format, normal set, tie-break, super tie-break, decider tie-break, advantage, or walkover.
3. Explain the rule in plain language and quote the exact validation message when useful.
4. Ask for the entered set/game score and relevant Game Play settings when the cause cannot be determined from the message alone.
5. If a setting is unknown, state the documented default and explain that event configuration may differ.
6. Do not invent decider targets, configured set counts, or format options that are not present in the source.
7. Do not assume Tennis uses the same cursor navigation behavior as Padel; the provided source explicitly names Padel navigation.
8. Treat the server's validation result as authoritative for whether the submitted score was accepted.

## Source references

- Backend score update: `gateway/src/routers/scoring_router.py` (`update_score`)
- Tennis scoring calculator: `tms/src/utils/scoring/calculators/tennis.py` (`TennisScoreCalculator`)
- Padel scoring calculator: `tms/src/utils/scoring/calculators/padel.py` (`PadelScoreCalculator`, extends the Tennis calculator)
- Sport strategy registration: `tms/src/utils/scoring/strategies/register_strategies.py` (sport IDs 2 and 3)
- Score entry UI: `src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts`
- Score feedback constants: `src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts`
- Padel score navigation: `src/app/shared/padel-score-navigation/padel-score-navigation.engine.ts`
- Game Play defaults: `src/app/shared/game-play-config/game-play-config.defaults.ts`
