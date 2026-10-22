---
doc_id: tms.event-settings.game-play.padel-tennis
title: Game Play settings – Padel and Tennis
routes:
  - tms/event-settings/game-play/:event_id
aliases:
  - padel scoring
  - tennis scoring
  - tiebreak
  - tie break
  - super tie break
  - golden point
  - deuce
  - match format
tenants: all
exclude_tenants: []
sports: [padel, tennis]
overrides: null
suggested_questions:
  - How do I set best of 3 sets with a super tie-break?
  - What is the difference between Standard and Golden Point System?
  - How many games are needed to win a set?
  - How do serving rules work?
backend_sources:
  - tms/src/service/rule_setting_service.py (update_rule_settings_v2)
  - gateway/src/routers/ctms_router.py (update_sport_config; login check only)
  - gateway/src/services/ctms_service.py (exception_handler returns response.json() without checking the status code)
  - CTMS/src/router/sports.py (PUT /sport/config)
  - CTMS/src/service/sports_config.py (update_config: CONFIG_NOT_FOUND when config_id does not exist)
source_files:
  - src/app/shared/game-play-config/game-play-config.component.html
  - src/app/shared/game-play-config/game-play-config.component.ts
  - src/app/shared/game-play-config/game-play-config.defaults.ts
---
# Game Play settings for Padel and Tennis

This guide covers the Game Play page sections that Padel and Tennis organisations see. Cards, disqualification and basic timeouts are in the general Game Play guide. Tennis organisations do not see Point System Configuration or Winner Comparison on this page.

## Padel and Tennis: Match Configuration (ST or SP)

- **ST – Standard Rule**: "In standard games, a match consists of an odd number of sets, such as 1, 3, 5, 7, or 9 To win the match, a player/team must achieve the maximum number of game wins." Example: best of 3 sets – the first to win 2 sets wins.
- **SP – Special Rule**: "In special games, a match consists of any number of sets, ranging from 1 to 9 Regardless of wins or losses, both players/teams are required to play all the games in the match".
- The number of sets is chosen in **Match Format Configuration**.

## Padel and Tennis: how a game is won at deuce (Scoring Configuration)

A game is counted 15, 30, 40, game. **Scoring Configuration** decides what happens at **40-40 (deuce)**:
- **Standard Point System** – "At 40-40 (deuce), players must win two consecutive points following the sequence 40-AD (advantage), 40-GO (game)." Advantage scoring: win the next point for advantage, then one more to win the game; losing a point at advantage goes back to deuce.
- **Golden Point System** – "Applies where the next point won at 40-40 immediately ends the game without requiring two consecutive points." The next point after deuce wins the game (common in padel).

## Match Format Configuration: sets and games

**Match Format Configuration** – "Configure match format settings such as match type, number of sets, and set-specific rules."
- **Match Type** tabs: **Single**, **Doubles**, **Mix-Doubles**, **Team**. Each match type has its own format. Pick a tab, set it, then pick the next tab; all are saved together with **Update**.
- **Number Of Sets per Match** – "Total number of sets to be played in a match" (**Sets**).
- **Games to win per set** – "Number of games to win a set" (**No. of Games**). Example: 6 for a normal set, 4 for a short set.

## Match Format Configuration: tie-break, decider and super tie-break

- **Enable Tiebreak** – "Check to activate tiebreak at defined score."
  - **Tie-Break Points** – "Number of points to be scored to win a tie-breaker" (**Pts to Win**), for example 7.
- **Additional Tie Break Configuration** (toggle), then choose one:
  - **Decider set Tie break** – "Enable this option to set custom tie-break points for the decider set when they differ from the standard tie-break points." Enter **Pts to Win** (for example 10).
  - **Super Tie break** – "Enable this option to use a Super Tie-Breaker set instead of the standard game-based set format." The deciding set is replaced by one tie-break to **Pts to Win** (for example 10).
- **Win by Margin** – "Point Difference require to win a tie break" (**Min Lead**), usually 2. Example: tie-break to 7 with Min Lead 2 – at 6-6 play continues until one side leads by 2.

## Padel and Tennis: example formats

- **Best of 3 sets, sets to 6, tie-break at 6-6 to 7**: ST, Sets 3, No. of Games 6, Enable Tiebreak on, Pts to Win 7, Min Lead 2.
- **Best of 3 with a super tie-break instead of the third set**: as above, plus Additional Tie Break Configuration on, **Super Tie break**, Pts to Win 10.
- **Golden point at deuce (padel style)**: choose **Golden Point System** in Scoring Configuration.
- **One short set**: Sets 1, No. of Games 4.

## Padel and Tennis: Scoring Management is not saved on the event page

Known problem. On the event's Game Play page, clicking **Update** on the **Scoring Management** tab (serving rules, intervals, timeouts, challenges, cards, disqualification) does **not** save anything for Padel and Tennis:
- The message "updated_successfully" appears, but the save was refused by the server ("CONFIG_NOT_FOUND", not shown on screen).
- The edited values stay on screen until you reload the page or toggle tabs; then the previous values return.
- The event keeps using its earlier scoring settings, or the organisation defaults if it never had its own.

What to do:
- **Result Management** (match format, sets, games, tie-break, deuce rule, points) saves normally on this page with "Rule Settings Updated".
- To change Scoring Management for Padel or Tennis, use **Game-Play Configuration** in the admin manage menu (`/admin/manage/game-play-config/1`). Note that this changes the defaults for the whole organisation, not just one event.
- Report the problem to support if one event needs different scoring settings.

## Padel and Tennis: Serving Rules

In **Scoring Management**, **Serving Rules**:
- **First Server Selection** – **Manual** or **Auto**.
- **Serve Order** – **Manual** or **Auto**.
- **Serve Change Frequency** – **Every** n **Game**: how often the serve passes to the other side.
- "Toggle ends after every odd-numbered game." – players change ends after games 1, 3, 5, ….
- "Enable standard serve rotation during tiebreaks." – the usual tie-break serving order (one serve, then two each).

## Padel and Tennis: intervals and timeouts

**Interval Configuration** – tick each interval type to use it and set its **Set Duration** in seconds. A separate **Tiebreak** group holds the tie-break intervals. "Disable Timeout in Final Set" – "If on, final set continues without tiebreak."

**Timeouts Configuration** extras (besides umpire and player timeouts):
- "Allow unused timeouts to carry over to next match".
- **Minimum time between timeouts** – **Duration (secs)**.
- **Medical Timeouts** – "Allow players to take a medical timeout for injury or illness, with a configurable duration and limit per match" (**Mins**).
- **Tiebreak** – **Allow Timeout in Tiebreak** with **Set Timer** (sec); **Disable Timeout in Final Set**.

## Padel and Tennis: challenges (Advanced Settings)

- **Number of challenges** – **Individual Events (Singles/Pairs)**: the number of challenges and whether they are counted **Per Match** or **Per Set**.
  - "Extra challenge in tie-break" – extra challenges per tie-break.
  - "Extra challenge in Super tie-break" – extra challenges per super tie-break.
- **Team Events** – "Allotted challenge for each match in a team event" or "Allotted challenge across all their matches in a team event", with the same extra tie-break options.
- "Reduce timeout after unsuccessful challenge".
- "Reset appeals every 12 games after 6–6 in Advantage Set".

## Frequently asked questions: Padel and Tennis scoring

**What happens at 40-40?** With **Standard Point System** advantage scoring (two points in a row); with **Golden Point System** the next point wins the game.

**How do I play best of 3 sets?** Choose ST and set **Number Of Sets per Match** to 3.

**How do I replace the third set with a super tie-break?** Turn on **Additional Tie Break Configuration**, choose **Super Tie break** and set **Pts to Win** (for example 10).

**How many games win a set?** The value in **Games to win per set**, for example 6.

**When is the tie-break played?** At the score set by the games per set (for example 6-6); it is played to **Tie-Break Points** with a **Min Lead**.

**Can doubles and singles have different formats?** Yes. Each **Match Type** tab (Single, Doubles, Mix-Doubles, Team) has its own format.

**How are challenges counted?** Per match or per set, as chosen for Individual Events; team events per match or across all matches.

**Why do I not see Point System Configuration (Tennis)?** It is not shown for Tennis organisations on this page.

**I clicked Update on Scoring Management and saw "updated_successfully", but my changes are gone.** For Padel and Tennis, Scoring Management is currently not saved on the event page. Change it in Game-Play Configuration (organisation-wide) or contact support.

**Is the Padel or Tennis match format saved?** Yes. Result Management saves normally ("Rule Settings Updated").

**How do I set best of 3 sets with a super tie-break?** Choose **ST** and set **Number Of Sets per Match** to 3. Then turn on **Additional Tie Break Configuration**, choose **Super Tie break** and set **Pts to Win** (for example 10).

**What is the difference between Standard and Golden Point System?** At 40-40 (deuce), **Standard Point System** uses advantage scoring: a player must win two points in a row. With **Golden Point System** the next point wins the game.

**How do serving rules work?** In **Scoring Management** → **Serving Rules**, choose **First Server Selection** and **Serve Order** (Manual or Auto) and set **Serve Change Frequency** (every n games). Options also let players change ends after every odd-numbered game and use the standard serve rotation in tie-breaks.
