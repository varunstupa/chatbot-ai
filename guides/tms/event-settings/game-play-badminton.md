---
doc_id: tms.event-settings.game-play.badminton
title: Game Play settings – Badminton
routes:
  - tms/event-settings/game-play/:event_id
aliases:
  - badminton
  - game level rules
  - points to win per game
  - black card
  - side change
tenants: all
exclude_tenants: []
sports: [badminton]
overrides: null
suggested_questions:
  - How many points are needed to win a badminton game?
  - When do players change sides in the deciding game?
  - What is the Black Card setting?
backend_sources:
  - tms/src/service/rule_setting_service.py (update_rule_settings_v2)
source_files:
  - src/app/shared/game-play-config-badminton/game-play-config-badminton.component.html
  - src/app/shared/game-play-config-badminton/game-play-config-badminton.component.ts
  - src/app/shared/game-play-config/game-play-config.component.ts
  - src/app/shared/game-play-config/game-play-config.component.html
---
# Game Play settings for Badminton

Badminton organisations see the Table Tennis and Badminton sections (games per match, Scoring Configuration, Decider set, intervals, challenges) plus the cards below.

## Badminton: Game Level Rules (points to win a game)

In **Result Management**, the **Game Level Rules** card – "Game rules for deuce, sudden death and game caps":
- **Points to win per game** – "Set a limit on number of points per game". Enter the **Game Limit** **per Game**.
- Allowed range: 11 to 30 points ("Allowed Range: 11-30 points").
- The hint "Allowed Range: 11-30 points" under the field turns red while the value is outside 11–30.
- Clicking **Update** on the **Result Management** tab with an empty value or a value outside 11–30 shows "Allowed Range: 11-30 points" and nothing is saved.
- Example: 21 for standard badminton games, 15 or 11 for shorter formats.
- When **Points to win per game** is not set, scores are checked against 21 points. The 11–30 range is checked only in the admin app.

## Badminton: Serving Rules

In **Scoring Management**, **Serving Rules**:
- **Side Change in Deciding Game** – "Change sides at midpoint of deciding game". Enter **Set Mid-point**, the score at which players change ends in the last game (1–99; a typed value outside this range is corrected to 1 or 99). Example: 11 in a game to 21.
- **Allow Different Starting Server Each Game** – the first server can change from game to game.
- **Switch ends after every game** – players change ends after each game.

## Badminton: Black Card

In **Cards Configuration**:
- **Black Card** toggle – "The umpire holds the power to disqualify based on their judgment."
- **Max Penalty Points** – "Reaching a certain threshold of penalty points which lead to disqualification". Enter **Penalty Points** (0–9).
- **Reason for Disqualification** – shown only when **Penalty Points** is above 0. Tick the reasons; **Add Custom** adds your own: type it in **Type Reason...** and click **Save** (greyed out while the box is empty). Custom reasons can be deleted; the reasons supplied by the system cannot.
- Black Card settings are saved with the other **Scoring Management** settings when you click **Update** on that tab.

## Badminton: Set Change Intervals

In **Interval Configuration**, Badminton sets each break between games separately:
- Tick **Set Change Intervals** – "Enable timeouts between sets, like after the first and second games".
- For each **Interval** ("Interval between Set 1 & Set 2", "Set 2 & Set 3", …) enter **Set Timer** in seconds (1–999; a typed value outside this range is corrected to 1 or 999).
- The number of intervals follows the number of games per match.

## Frequently asked questions: Badminton game play

**How many points are needed to win a badminton game?** The **Game Limit** in Game Level Rules, between 11 and 30.

**Why can I not save with 35 points per game?** The allowed range is 11–30 points.

**Where do I set a sudden-death max point for Badminton?** The Game Level Rules card has no sudden-death field. Use **Sudden Death Point** (**Max Point**) under **Standard Point System** in **Scoring Configuration**.

**When do players change sides in the last game?** At the **Set Mid-point** score, if **Side Change in Deciding Game** is set.

**Can each game start with a different server?** Yes, tick **Allow Different Starting Server Each Game**.

**What is a black card?** A disqualification card; set the penalty-point threshold and reasons in **Black Card**.

**How do I set a 120-second break between games 1 and 2?** Tick **Set Change Intervals** and enter 120 in **Set Timer** for Interval 1.

**What is the Black Card setting?** In **Cards Configuration**, turn on **Black Card** to let the umpire disqualify a player. Set **Max Penalty Points** (0–9), the penalty points that lead to disqualification, and tick the **Reason for Disqualification** options; **Add Custom** adds your own reason.
