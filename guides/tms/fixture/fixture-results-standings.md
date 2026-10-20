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
---
# Results, standings, tie details, playing order and point system

This guide covers the parts of the fixtures page that sit around the results: the tie details of a group, the playing order of team matches, and the point system that decides the standings. The score entry itself is in the scoring guide; the match lists are in the group results guide.

## Tie details

- **Tie details** (in the group results header) shows how a tie is decided.
- The overlay lists the players or teams of the tie. A forfeited player is marked "Forfeited Player".

## Playing order (team matches)

- The playing order is the order of the games in a team match: which players of each team play which game.
- Open the **playing order** dialog from the stage.
- Each row is one game. Each side of a game has fields: a text box for a player's name, or a dropdown to pick a player from the team.
- For a single game (singles) there is one player per side; for doubles there are two per side.
- Set the order before the team matches are played.
- Close with the close button.

## Point system

- The **point system** panel sets the points for winning, losing and drawing a match, and the tie-breakers.
- It opens as a side panel. Its settings are the Game Play configuration, documented in the Game Play guides (Table Tennis, Badminton, Padel and Tennis).
- See the Game Play guides for the scoring rules.

## Standings

- The standings order the players or teams of a group (or knockout stage) by points, then by the tie-breakers set in the rule settings.
- A tie-breaker such as **Head-to-Head** compares only the matches between the tied players or teams.
- A forfeited player is listed with the forfeit mark.

## Messages

- The playing order and the point system show the message of the server when a save fails; if none, a generic error appears.
- Rule settings saved: "Rule Settings Updated" (see the Game Play guides).

## Permissions

- Changing the point system uses the rule settings permission (see the Game Play guides).

## Frequently asked questions about results and standings

**How do I see the tie details of a team?** Click **Tie details** in the group header.

**How do I set the playing order of a team?** Open the playing order dialog, choose the player for each side of each game, then close it.

**Where is the point system set?** Open the point system panel from the stage; the rules are the Game Play configuration.

**How are the standings ordered?** By points, then by the tie-breakers in the rule settings, such as head-to-head.

**Why are the team names empty in the playing order?** The teams have no players yet, or the playing order was not saved for this format.
