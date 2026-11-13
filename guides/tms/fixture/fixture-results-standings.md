---
doc_id: tms.fixture.results-standings
title: Results, standings, tie details, playing order and point system
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - tie details
  - tie details overlay
  - playing order popup
  - team playing order
  - point system
  - standings
  - results and standings
  - head to head
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I see the tie details of a team?
  - How do I set the playing order of a team?
  - Where is the point system set?
  - How are the standings ordered?
  - Why are the team names empty in the playing order?
backend_sources:
  - gateway/src/routers/playing_order_router.py (get_team_playing_order, get_team_playing_order_with_matches)
  - gateway/src/routers/rule_setting_router.py (get_rule_settings, update_rule_settings)
  - gateway/src/routers/group_router.py (get_group_matches)
source_files:
  - src/app/modules/tms/fixture-configuration/fixture-popups/tie-details-overlay/tie-details-overlay.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/playing-order/playing-order.component.html
  - src/app/shared/point-system/point-system.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/matches-standings/groups-stage-matches-standings.component.html
  - src/app/modules/tms/fixture-configuration/knockout-creation-wizard/bodies/playing-format-body/knockout-wizard-playing-format-body.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/creation-wizard/bodies/playing-format-body/groups-stage-wizard-playing-format-body.component.html
  - src/assets/i18n/en.json
---
# Results, standings, tie details, playing order and point system

This guide covers the parts of the fixtures page that sit around the results: the tie details of a group, the playing order of team matches, and the point system that decides the standings. The score entry itself is in the scoring guide; the match lists are in the group results guide.

## Tie details

- **Tie Details** shows the players or teams of a group that are level on points, and how they compare head to head.
- Open it with the info icon next to the "{{count}} Participants" figure in the group header. The icon appears only while the group is expanded and the group has participants level on points.
- The overlay header shows **Tie Details** and the group number (**Group 1**, **Group 2** ...).
- Each set of tied participants is listed separately ("{{count}} Participants"), with the columns **Participant**, **Match W/L**, **Game W/L**, **Score W/L**, **Points** and **Position**. The W/L figures count only the matches between the tied participants.
- A forfeited participant is shown in red with a warning icon (tooltip "Forfeit Player") and "(forfeited)" after the name.
- Click outside the overlay to close it. If loading fails, the server message is shown.

## Playing order (team matches)

- The playing order is the order of the games in a team match: which players of each team play which game.
- It is chosen in the stage creation wizard of a team event (playing format step): each playing order format has a radio button, and **View** next to it opens the playing order dialog.
- The dialog is titled with the format's name. Each row is one game, marked **S** (singles, one **Player Name** per side) or **D** (doubles, "Player Name / Player Name" per side).
- Each side shows either a fixed position label (read-only box) or a dropdown of the allowed positions. The dialog is a preview only; nothing is saved from it.
- Close it with the close icon at the top right.
- Scores of team matches cannot be entered until a playing order is set: "Please set playing order in preference for update score for team matches."

## Point system

- The point system is set in **Game Settings**, which opens the **Fixture Settings** side panel. It sets the points for winning, losing and drawing a match, and for a group stage the Winner Comparison and Winner Basis tie-breakers (see the Game Settings guide for the Fixtures screen).
- Its other settings are the Game Play configuration, documented in the Game Play guides (Table Tennis, Badminton, Padel and Tennis).
- See the Game Play guides for the scoring rules.

## Standings

- The standings order the players or teams of a group (or knockout stage) by points, then by the Winner Comparison and Winner Basis tie-breakers set in **Game Settings**.
- A tie-breaker such as **Head-to-Head** compares only the matches between the tied players or teams.
- A forfeited player is listed with the forfeit mark.

## Messages

- The playing order and the point system show the message of the server when a save fails; if none, a generic error appears.
- Rule settings saved: "Rule Settings Updated". When a match is already in progress or scored, the rule set is kept and only the other settings change (see the Game Play guides).

## Permissions

- Changing the point system uses the rule settings permission (see the Game Play guides).

## Frequently asked questions about results and standings

**How do I see the tie details of a team?** Click **Tie details** in the group header.

**How do I set the playing order of a team?** Choose the playing order format with its radio button in the stage creation wizard (playing format step). **View** shows the games of that format; the players of each game are then set in the lineup of the team match in the score dialog.

**Why can't I see the Tie Details icon?** Expand the group first. The icon appears only when some participants of the group are level on points.

**Where is the point system set?** Click **Game Settings** on the fixtures page; it opens the **Fixture Settings** panel with the Game Play configuration.

**How are the standings ordered?** By points, then by the tie-breakers in the rule settings, such as head-to-head.

**Why are the team names empty in the playing order?** The teams have no players yet, or the playing order was not saved for this format.
