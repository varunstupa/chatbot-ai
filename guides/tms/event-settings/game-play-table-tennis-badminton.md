---
doc_id: tms.event-settings.game-play.table-tennis-badminton
title: Game Play settings – Table Tennis and Badminton
routes:
  - tms/event-settings/game-play/:event_id
aliases:
  - table tennis scoring
  - badminton scoring
  - sudden death
  - decider set
  - golden point
  - games per match
tenants: all
exclude_tenants: []
sports: [table_tennis, badminton]
overrides: null
suggested_questions:
  - How many games are played in a match?
  - What is a Sudden Death Point?
  - What is the difference between Standard and Golden Point System?
  - What does the Decider set option do?
  - How does the Challenge System work?
backend_sources:
  - tms/src/service/rule_setting_service.py (update_rule_settings_v2)
source_files:
  - src/app/shared/game-play-config/game-play-config.component.html
  - src/app/shared/game-play-config/game-play-config.component.ts
  - src/app/shared/game-play-config/game-play-config.defaults.ts
---
# Game Play settings for Table Tennis and Badminton

This guide covers the Game Play page sections that Table Tennis and Badminton organisations see. Match results, standings, cards, disqualification and timeouts are in the general Game Play guide. Badminton has a few extra cards described in the Badminton guide.

## Table Tennis and Badminton: games per match

Under **Match Configuration** choose the rule, then **Select Number of Games per Match**:
- **ST – Standard Rule**: "In standard games, a match consists of an odd number of games, such as 1, 3, 5, 7, or 9. To win the match, a player/team must achieve the maximum number of game wins." Choices: 1, 3, 5, 7, 9. Example: best of 5 means the first to win 3 games wins the match.
- **SP – Special Rule**: "In special games, a match consists of any number of games, ranging from 1 to 9. Regardless of wins or losses, both players/teams are required to play all the games in the match." Choices: 1 to 9.

## Table Tennis and Badminton: how a game is won (Scoring Configuration)

**Scoring Configuration** decides what happens at a tied score near the end of a game. Choose one:

- **Standard Point System** – normal deuce: at a tie near the end of the game (10-10 in Table Tennis), play continues until one side leads by 2 points.
  - Optional **Sudden Death Point** – "Fixed point that automatically decides the winner after a prolonged deuce". Enter **Max Point**: the first side to reach this score wins the game, even without a 2-point lead. Example: Max Point 15 – at 14-14 the next point wins.
- **Golden Point System** – "To win a game, Player A or Player B must score at least 11 points If the score is 10-10, the first player to reach 11 points wins". There is no deuce: at 10-10 the next point wins.

For Badminton the points needed to win a game are set in **Game Level Rules** (Badminton guide).

## Table Tennis and Badminton: Decider set

- **Decider set** toggle – "The decisive game is won by the first player to accumulate the requisite number of points."
- When on, set:
  - **Point** – the points needed to win the deciding (last) game, which can differ from normal games.
  - **Serve** – the serving option used in the deciding game.
- Example: games to 11, but **Decider set** with Point 7: the final game of the match is played to 7.

## Table Tennis and Badminton: card rules (ITTF Rule Card Management)

Under **Cards Configuration** in Scoring Management:
- **ITTF Rule Card Management** – "Select the Official ITTF card logic". When on, choose:
  - **Penalty Points Enabled** – "Card results in a penalty point to the opponent".
  - **Penalty Points Disabled** – "Card results in a warning without a penalty point".
- Yellow card, red card and disqualification settings are described in the general Game Play guide.

## Table Tennis and Badminton: Interval Configuration

Tick an interval to use it and set its **Set Duration** in seconds:
- **Start Game** – "Enable practice time before the start of the game" (1–999 sec).
- **Mid Interval** – "Enable the mid-set interval when the leading score reaches mean point set" (1–999 sec).
- **Set Change Intervals** – "Enable timeouts between sets, like after the first and second games" (1–999 sec). Badminton sets these per interval instead (Badminton guide).
- **Service Timer** – "Display reverse timer that automatically resets after each point is awarded" (1–99 sec).
- **Rally Timer** – "A timer that measures the duration of each rally (from the serve to the point being awarded)".

## Table Tennis and Badminton: Challenge System and Expedite

Under **Advanced Settings**:
- **Challenge System** – "Allows players/teams to contest specific umpire decisions". Set the **Number of challenges**:
  - **Individual Events (Singles/Doubles)** – **Limit** per match.
  - **Team Events** – per match in a team event, or one allowance across all their matches.
  - "Reduce timeout after unsuccessful challenge" – a lost challenge costs a timeout.
- **Enable Expedite** – "Allow umpires to trigger expedite system to limit the duration of matches".
  - **Manual Trigger** – "Allow umpires to manually trigger the expedite system".
  - **Time Trigger** – "Minutes of play after which the expedite system is automatically triggered" (**Set Duration**).
  - **Minimum Points** – "The expedite system will not be introduced if a game has reached a minimum number of points" (**Min Points**).

## Frequently asked questions: Table Tennis and Badminton scoring

**How many games are played in a match?** The number chosen in **Select Number of Games per Match**. With ST the match ends when one side wins the majority; with SP all games are played.

**What happens at 10-10 in Table Tennis?** With **Standard Point System** play continues until a 2-point lead (or until **Max Point** if Sudden Death Point is on). With **Golden Point System** the next point wins.

**What is a Sudden Death Point?** A Max Point at which the game ends even without a 2-point lead.

**Can the last game be shorter?** Yes. Turn on **Decider set** and enter its **Point**.

**Does a card give the opponent a point?** Only if **ITTF Rule Card Management** is on with **Penalty Points Enabled**.

**How do I add a practice time before a game?** Tick **Start Game** in Interval Configuration and set its duration.

**What is expedite?** A system that limits match length; it can be triggered by the umpire or automatically after the Time Trigger.
