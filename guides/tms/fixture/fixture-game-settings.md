---
doc_id: tms.fixture.game-settings
title: Game Settings on the Fixtures screen – winner comparison and winner basis for group stage positions
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - game settings
  - fixture game settings
  - fixture settings
  - winner basis
  - winner basis for final position
  - group stage winner
  - group winner decided
  - group standings order
  - group position tie break
  - winner comparison
  - head to head
  - compare with all
  - win loss ratio
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is Winner Basis in Game Settings?
  - How is the winner of a group stage decided?
  - What is the difference between Won and Win/Loss Ratio?
  - Why do I not see Winner Basis in Game Settings?
backend_sources:
  - gateway/src/routers/rule_setting_router.py (get_rule_settings, update_rule_settings)
source_files:
  - src/app/shared/point-system/point-system.component.html
  - src/app/shared/point-system/point-system.component.ts
  - src/app/shared/game-play-config/game-play-config.component.html
  - src/app/shared/game-play-config/game-play-config.component.ts
  - src/app/modules/tms/fixture-configuration/fixture-configuration.component.html
---
# Game Settings on the Fixtures screen

The **Game Settings** link on the Fixtures screen opens the **Fixture Settings** side panel. It holds the game play rules of this category (or of one stage): points, match format and, for a group stage, how the final group positions are decided with **Winner Comparison** and **Winner Basis (For Final Position)**.

## Game Settings: where to find it

- Open the category on the **Fixtures** screen. The **Game Settings** link is in the stage address bar, above the draw.
- It is shown only after the matches of the stage are created (**Final Edit**).
- Click it to open the **Fixture Settings** side panel on the right.
- For league events a notice above it reads "Match Access is now available inside Game Settings › Scoring Management › Scoring Access." Close it with the X; it stays hidden for the rest of the session.
- At the top choose **Apply to all stages** or **Stage-wise**. With Stage-wise, pick the stage to configure.

## Game Settings panel: Result Management and Scoring Management

The panel has two tabs:
- **Result Management** – **Point System Configuration** (points for **Win**, **Lost**, **Tie**, **Win After Tie (Golden Match)**, walkover and not played reasons), the match and set point systems for teams, **Golden Game Configuration**, **Match Configuration**, **Scoring Configuration**, **Match Format Configuration** (sets per match, games per set, tie break, win by margin) and, for a group stage, **Winner Comparison** and **Winner Basis (For Final Position)**.
- **Scoring Management** – **Scoring Access** (who may score which matches, and when), **Serving Rules**, **Game Settings and Visual Management** (toss, T-shirt colours, representation), **Cards Configuration**, **Interval Configuration**, **Timeouts Configuration** and **Advanced Settings** (challenges, expedite).

The sections shown depend on the sport and on whether the category is singles, doubles or teams.

## How the winner of a group stage is decided

The final position of each player or team in a group is worked out like this:
1. **Points** first – the standing points from the point system (for example 2 for a win, 1 for a loss).
2. When players are level on points, the tie is broken with **Winner Comparison** and the ticked **Winner Basis** criteria, in their order: **Match**, **SubMatch**, **Game**, **Score**.
3. The first criterion that separates them decides; the next one is used only when they are still level.

Both settings are shown only when a **group stage** is selected. Knockout and position rounds are decided by the match result, so they have no Winner Basis.

Which players then move on from the groups is set separately in the stage's **Stage winners and qualifiers** (number of winners per group).

## Game Settings: Winner Comparison

- **Head-to-Head** – players level on points are compared using only the matches between them.
- **Compare with All** – players level on points are compared using their results against everyone in the group.

## Game Settings: Winner Basis (For Final Position)

Tick each criterion to use it:
- **Points** – total standing points. It has no options.
- **Match** – matches won and lost.
- **SubMatch** – sub matches won and lost (team events).
- **Game** – games (sets) won and lost.
- **Score** – points scored and conceded.

For each ticked criterion (except Points) choose how it is counted:
- **Won** – the number won. More wins ranks higher.
- **Win/Loss Ratio** – won divided by lost. A record with wins and no losses ranks above every ratio.
- **Win-Loss** – won minus lost. Only shown for **League** events.

An unticked criterion is not used to break ties.

Defaults: tournaments use **Head-to-Head** and **Win/Loss Ratio**; leagues use **Compare with All** and **Win-Loss**. All criteria start ticked.

Example: two players have 4 points each. With Head-to-Head and Match on Win/Loss Ratio, the one who won their match against the other finishes higher. If still level, Game, then Score decide.

## Game Settings: saving

- Click **Update** at the bottom of the panel. "Rule Settings Updated" confirms the save. Rounds that already have matches in progress or scored keep their old round rules.
- While **Scoring Access** is open, it saves with its own buttons and **Update** does nothing.
- Invalid values block the save: "Please enter valid values for …" lists the fields (for example the target point value must be 1 to 99). For Badminton, the points to win a set must be 11 to 30: "Allowed Range: 11-30 points".
- Changing the winner basis never changes a match result; it only changes the order of the group positions.
- "This setting is applied to all rounds. You cannot update it once the match status is In Progress or Scored. If you want to change it, please reset the match to apply the new settings." – some settings are locked once a match of the stage is in progress or scored.
- "Access Denied" – saving needs **Edit** permission on **Edit Game Play Settings**.

## Game Settings: what locks after matches start

The server checks the stage before saving:
- **Completed stage**: nothing can be saved ("Rule Settings Invalid Request").
- **Stage in progress**: saving only works with **Stage-wise** already on and kept on; otherwise "Rule Settings Invalid Request". Switching from Stage-wise back to **Apply to all stages** is refused too.
- **Stage in progress, Result Management**: the rule (ST/SP), point system, team match and set point systems, individual points, set point and scoring rule are locked. **Scoring Management**: cards, intervals, timeouts, toss, disqualification, challenges, expedite and serving are locked. Changing them shows "This setting is applied to all rounds. …".
- A round with matches in progress or scored keeps its round rules; changing them shows the same message.
- Changing the number of games or sets with **Apply to all stages** is refused with the same message when any match of the category is in progress or scored. Otherwise the existing matches are updated to the new number.
- Before the stage starts, switching Stage-wise off applies the new number of games or sets to all matches of the stage.

## Game Settings: same setting elsewhere

- The event's **Game Play** page (Event → Game Play → Result Management) has the same Winner Comparison and Winner Basis as the event default. A category saved here keeps its own values.
- The **Winner logic** button on the **Leaderboard** screen sets the leaderboard order with the same criteria.

## Frequently asked questions about Game Settings on the Fixtures screen

**What is Winner Basis in Game Settings?** The order of tie-break criteria (Points, Match, SubMatch, Game, Score) used to decide the final positions in a group when players are level on points.

**How is the winner of a group stage decided?** By standing points first. Players level on points are separated by Winner Comparison (Head-to-Head or Compare with All) and then the ticked Winner Basis criteria in order. Set them in **Game Settings** on the Fixtures screen.

**What is the use of Winner Basis in the Fixtures screen Game Settings?** It decides who finishes 1st, 2nd and so on in each group when points are equal, which also decides who qualifies from the group.

**What is the difference between Won and Win/Loss Ratio?** Won counts only wins; Win/Loss Ratio divides wins by losses, so a player with fewer matches but no losses can rank higher.

**Why do I not see Winner Basis in Game Settings?** It is shown only for a group stage. Select the group stage (or use Apply to all stages on a category with groups).

**Why is Win-Loss missing?** Win-Loss is only offered for League events; tournaments have Won and Win/Loss Ratio.

**Where is Game Settings on the Fixtures screen?** The **Game Settings** link in the stage address bar, shown once the matches of the stage are created.

**Where did Match Access go?** It is now inside **Game Settings** › **Scoring Management** › **Scoring Access**.
