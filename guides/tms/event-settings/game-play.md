---
doc_id: tms.event-settings.game-play
title: Game Play settings page
routes:
  - tms/event-settings/game-play/:event_id
aliases:
  - game play
  - gameplay
  - game play settings
  - scoring settings
  - rule settings
  - point system
  - match rules
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the difference between Result Management and Scoring Management?
  - How many points does a team get for a win?
  - Do event game play settings change categories that already have their own settings?
  - How do I set the number of timeouts per match?
backend_sources:
  - gateway/src/routers/rule_setting_router.py (update_rule_settings, get_rule_settings)
  - tms/src/service/rule_setting_service.py (update_rule_settings_v2, _update_event_level_rule_settings_v2, _find_configs)
source_files:
  - src/app/shared/game-play-config/game-play-config.component.ts
  - src/app/shared/game-play-config/game-play-config.component.html
  - src/app/shared/constants/sport-id.enum.ts
---
# Game Play settings page – user guide

This guide describes the **Game Play** step of an event in the Stupa Event Management System (admin panel). Here the organiser sets the rules used to play, score and rank the matches of the event. Some sections depend on the organisation's sport (Table Tennis, Badminton, Padel or Tennis); those are described in the sport guides for this page.

## Where to find it

Open **Event** from the sidebar, then click **Game Play** in the row of setup steps at the top of the page.

## Game Play page: where it is and what it is for

- Page address: `/tms/event-settings/game-play/<event id>`, for example `/tms/event-settings/game-play/1358`.
- It is the **Game Play** step in the row of event setup steps. The step is only shown for organisations that use it.
- Two tabs:
  - **Result Management** – how matches are decided and how results become standings: points for a win, the match format, the scoring system and ranking rules.
  - **Scoring Management** – how the umpire scores live: serving, cards, disqualification, intervals, timeouts, challenges.
- Each tab is saved separately with its **Update** button at the bottom. Switching tabs reloads the saved values of that tab, so click **Update** before switching.
- The sport is fixed for the organisation, so the page only shows the settings that apply to it.

## Where the values come from and what an event setting changes

Game play settings exist on four levels. The most specific one that exists is used:
1. a **stage** with stage-wise settings (set on the Fixtures screen),
2. a **category** (set on the Fixtures screen for that category),
3. the **event** (this page),
4. the **organisation** defaults (**Game-Play Configuration** in the admin manage menu, `/admin/manage/game-play-config/0`).

What this means:
- When the event has no own settings yet, this page shows the organisation defaults. Clicking **Update** saves them as the event's own settings.
- Event settings apply to every category of the event that has **no own settings**. A category or stage configured on the Fixtures screen keeps its own values.
- Saving here never overwrites category or stage settings.
- The message "Rule Settings Updated" confirms the save.
- Exception: for **Padel and Tennis**, **Scoring Management** is currently not saved on this page (see the Padel and Tennis guide). Result Management saves normally for every sport.

## Result Management: Point System Configuration

Shown for Table Tennis, Padel and Badminton organisations (not for Tennis).

Turn on the toggle to give standing points per match result. Enter the points for: **Win**, **Lost**, **Tie**, **Win After Tie (Golden Match)**, **Walk Over**, **Not Played**, **Injured** and **Others**. Values are whole numbers up to 2 digits.

These points are added up for the group standings (for example 2 for a win, 1 for a loss).

**Enable Set Point System** – "Each set winner will receive the below configured point for the team (Walkover and Not Played will be defined as 0 points)". Enter points for **Single**, **Doubles** and **Golden Match**, each 1 to 99.
- **Advance Set Point System** (only with the Standard rule, **ST**) – "extend matches until the required winning lead is reached": **Minimum Lead** (pts, 1–99) and **No. of consecutive matches to be played**.
- **Target Point System** – a target number of points to win (**Pts**, 1–99).

Invalid values block the save with "Please enter valid values for …" naming the fields (for example Single, Doubles, Golden Match, Minimum Lead).

## Result Management: Match Configuration (ST or SP)

Choose how many games or sets a match has:
- **ST – Standard Rule**: an odd number of games/sets (1, 3, 5, 7 or 9). The match ends as soon as one side has won the majority.
- **SP – Special Rule**: any number from 1 to 9, and **all** games/sets are played regardless of who is leading.

Table Tennis and Badminton choose the number of games with **Select Number of Games per Match**; Padel and Tennis choose the number of sets in **Match Format Configuration** (see the sport guide).

Team options such as **Enable Match Point System**, **Advance Match Point System**, **Golden Game Configuration**, **Apply Rounds On** and **Individual Point Configuration** are not on this event page. They appear when a Teams category is configured on the Fixtures screen.

## Result Management: Winner Comparison and Winner Basis

Shown for Table Tennis, Padel and Badminton organisations.

- **Winner Comparison** – how tied players or teams in a group are compared:
  - **Head-to-Head** – only the matches between the tied players count.
  - **Compare with All** – results against everyone in the group count.
- **Winner Basis (For Final Position)** – the order of tie-break criteria used for final positions (for example Points, Match, Game, Score). Tick the criteria to use; for each one choose how it is counted:
  - **Won** – number won,
  - **Win/Loss Ratio** – won divided by lost,
  - **Win-Loss** – won minus lost (League events).
- The first criterion decides; the next one is used only when it is still tied.

## Scoring Management: Game Settings and Visual Management

- **T-shirt colour selection (Teams)** – "Prompt the umpire to record t-shirt colors". If off, the default colours are black and grey.
- **Representation Type** – what viewers see next to players during the event:
  - **Display country flags of players** (FLAG),
  - **Official logo of the registration entity** (LOGO),
  - **Abbreviation of registration entity** (CLUB).

## Scoring Management: Cards and Disqualification

**Cards Configuration**:
- **Yellow Card** – "The Umpire has the authority to issue a yellow card at their discretion".
  - **Max Card Limit** (0–9) per player or team.
  - "Automatically add points to the opponent after multiple yellow cards".
  - "Convert second yellow cards into a red card".
- **Red Card** – **Max Card Limit** (0–9) and "Automatically add points to the opponent".

**Disqualification** – "The umpire holds the power to disqualify based on their judgment."
- **Penalty Points** (0–9) – reaching this number of penalty points leads to disqualification.
- When it is above 0, tick the **Reason for Disqualification** options. **Add Custom** adds your own reason (type it and click **Save**); custom reasons can be deleted.

## Scoring Management: Timeouts Configuration

- **Umpire Timeouts** – "Umpires have the authority to call a timeout during play if they believe it is necessary to address a situation".
- **Player Timeouts** – "Player timeouts are enabled for the tournament". Then set **Number of Timeouts**:
  - **Individual Events (Singles/Doubles)** – timeouts per match (0–9).
  - **Team Events** – either "Allotted timeouts for each match in a team event" (per match) or "Allotted timeouts across all their matches in a team event" (one allowance for the whole team match). Only the chosen field can be filled.

Padel and Tennis have extra timeout options (medical timeouts, minimum time between timeouts, tiebreak timeouts); see the Padel and Tennis guide.

## Game Play page: messages and permissions

- "Rule Settings Updated" – saved.
- "updated_successfully" (Padel and Tennis, Scoring Management only) – despite the wording, the scoring settings were **not** saved for the event; see the Padel and Tennis guide.
- "Please enter valid values for …" – a number is missing or out of range; the named fields must be fixed before saving.
- "This setting is applied to all rounds. You cannot update it once the match status is In Progress or Scored. …" – shown when a locked setting is changed for a stage that already has matches in progress or scored (on the Fixtures screen). Reset the match to change it.
- "Access Denied" – saving needs **Edit** permission on **Edit Game Play Settings**.
- "Unauthorized Access" – your session expired. Sign in again.

## Frequently asked questions about the Game Play page

**What is the difference between Result Management and Scoring Management?** Result Management decides how matches are won and ranked; Scoring Management sets the live scoring tools (cards, timeouts, intervals, serving).

**How many points does a team get for a win?** The value in **Win** under Point System Configuration, set by your organisation or changed here for this event.

**Do event settings change categories that already have their own settings?** No. They apply only to categories without own settings.

**Where do the values on this page come from?** From the event's saved settings, or from the organisation's Game-Play Configuration when the event has none.

**What is the difference between ST and SP?** ST ends the match when one side wins the majority of an odd number of games/sets; SP always plays all games/sets.

**Why do I not see team point options?** They are set per Teams category on the Fixtures screen, not on this event page.

**What does Head-to-Head mean?** Only matches between the tied players or teams are compared.

**How do I limit yellow cards?** Set **Max Card Limit** under Yellow Card in Cards Configuration.

**Why did my changes disappear when I switched tabs?** Each tab is saved separately; click **Update** before switching.

**How do I set the number of timeouts per match?** In **Timeouts Configuration**, turn on **Player Timeouts** and set **Number of Timeouts**: per match (0–9) for singles and doubles, and for team events either per match or one allowance across all their matches.
