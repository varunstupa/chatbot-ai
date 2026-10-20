---
doc_id: tms.leaderboard.api
title: Backend logic of the Leaderboard APIs – categories and stages, team and player standings, final standing, groups, matches, winner logic and the gateway rules
routes:
  - tms/leaderboard/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
  - tms/leaderboard/:participant_id/:category_id/:event_id
aliases:
  - leaderboard api
  - leaderboard backend
  - leadership points api
  - leaderboard ranking api
  - leaderboard winner logic api
  - standings api
  - group participants api
  - leaderboard permissions
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - Which API loads the Team Leaderboard?
  - Which API loads the Player Leaderboard?
  - How is the final standing worked out on the server?
  - Which API saves the winner logic and which permission does it need?
  - What does the leaderboard return when the category has no rounds?
  - How are players with equal points ranked?
  - Why do all squad players appear on the player leaderboard?
backend_sources:
  - gateway/src/routers/leadership_points_router.py (group-participants, leaderboard)
  - gateway/src/routers/match_router.py (leaderboard-ranking, winner logic, matches)
  - gateway/src/routers/group_router.py (get_groups, get_group_matches)
  - gateway/src/routers/fixture_router.py (get_knockout_matches)
  - tms repository, branch staging: src/router/leadership_points_router.py (group-participants, leaderboard, recalculate)
  - tms repository, branch staging: src/service/leadership_points_service.py (squad roster, points aggregation)
  - tms repository, branch staging: src/router/match_router.py (leaderboard-ranking, winner logic routes)
  - tms repository, branch staging: src/service/match_service.py (get_event_category_leaderboard, resolve_leaderboard_settings)
  - tms repository, branch staging: src/utils/winner_logic_defaults.py
  - tms repository, branch staging: src/common/enums.py (ComparisonMethod)
source_files:
  - src/app/modules/tms/leaderboard/leaderboard.component.ts
  - src/app/core/constants/api-constant.ts
  - src/app/core/services/common-service/common-service.service.ts
  - src/app/core/services/fixture-service/fixture.service.ts
  - src/app/core/services/event-service/event.service.ts
---
# Backend logic of the Leaderboard APIs

The Leaderboard screen calls the **gateway**. The gateway forwards the team and player standings to the TMS leadership points routes, and the final standing and the winner logic to the TMS match routes. Groups, bracket and matches come from the TMS group, fixture and match routes.

## Calls the screen makes

| Screen action | Method and path | Gateway route and rule |
|---|---|---|
| Category tabs | GET `event/v1/get_participant_types_and_categories` | Events router. The page keeps the team categories only. |
| Stage tabs | GET `stage/v1/get_stages` | Stage router. Asks for the rule settings. |
| Stage team table | GET `v1/leadership-points/group-participants/by-event-category/{event_category_id}` | Leadership points router; login only. |
| Final standing (ALL) | GET `match/v1/leaderboard-ranking` | Match router; login only. |
| Player Leaderboard | GET `v1/leadership-points/leaderboard/{event_category_id}` | Leadership points router; login only. |
| Stage participants | GET `stage/v1/get_stage_participants` | Stage router; sorted by standing. |
| All groups | GET `group/v1/get_groups` | Group router. |
| All matches and All Rounds | GET `group/v1/get_group_matches` | Group router. |
| Bracket | GET `fixture/v1/get_knockout_matches` | Fixture router. |
| Compare with Other Teams | GET `match/v1/matches` | Match router. Sub matches and both participants loaded. |
| Match Details | GET `playing_order/v1/get_team_playing_order_with_matches` | Playing order router. |
| View Details (members) | GET `register/v1/get_event_participants` | Registration router. |

## Winner logic calls

| Screen action | Method and path | Gateway route and rule |
|---|---|---|
| Winner logic open | GET `match/v1/get_leaderboard_winner_logic` | Match router; login only. |
| Winner logic Update | PUT `match/v1/update_leaderboard_winner_logic` | Match router; Display Settings, edit. |


## Team and player standings

- The stage team table and the player table read the leadership points of the category. Each leadership record holds the match, the participant or team, the points, the winner flag, the tag and the match type.
- The team table is grouped by team participant with the best group rank across the groups. With a stage the rank is the group rank in that stage. Without a stage the rank is worked out from the total points of all groups.
- The player table adds up the points per participant. Players with equal total points share a position.
- When no match type filter is given, the squad of every team in the fixture is added at zero, so a player with no points still appears.
- Both routes page by page. The page number starts at 1, and the record offset is worked out from it.

## Final standing (ALL)

- The server takes the group stage rounds of the category. If there are none, it returns success with the "no rounds found" message and an empty list, plus the comparison method.
- Otherwise it loads the matches of those rounds, with sub matches for team categories and with the golden matches.
- The rows are ordered by best rank, then by name. The search filters team names, and also team rows that have a player with a matching name.
- The search runs before paging, so the total count is the count after the search. Each page is the offset of (page - 1) times the limit.
- The reply carries the participants, the total count, the golden-available flag (true when any team has golden matches won) and the comparison method.

## How the final standing is ranked

- The participants are first grouped into buckets by total group points, highest first. Each bucket takes the next rank, and the next bucket starts after the bucket's size (1, 1, 3 and so on).
- **Head-to-Head**: the teams in a bucket are ordered by the enabled criteria, using the records between the tied teams. Teams still level are then compared on their overall records with the same criteria.
- **Compare with All**: there are no buckets. Each team is compared with the whole field using its overall record. Teams the criteria cannot separate share a rank.
- Points are not used as a tie-break inside a bucket; they only form the buckets.
- Criteria are applied in their saved order. Match, Sub Match, Game and Score use the won count, the won/loss ratio or the win-loss difference, as chosen. Game counts sets won and Score counts points won.

## Winner logic storage

- The winner logic is stored per event and category, and the rule is saved under the "LEADERBOARD_WINNER_LOGIC" configuration.
- **Save** writes the criteria and the comparison method. Only the values sent are written; the rest of the stored data is kept.
- **Read** fills in any missing part from the default ladder: Points (won), Match (won/loss), Sub Match (off, with won/loss), Game (won/loss) and Score (won/loss). The comparison method comes from the event type when it is not set: leagues use Compare with All, other events Head-to-Head.
- A migration froze the older categories to Head-to-Head when they had group results, so their standing does not change.

## Permissions and errors

- Reading needs a login, but no feature permission: the leadership points, the final standing and the winner logic read use the login check only. The groups route checks the token itself and returns 401 without it. Group matches and the bracket use the login check only.
- Saving the winner logic needs Display Settings in edit mode.
- A missing category returns 404; a server error returns 500 with its text.
- Standings with no rows return 200 with an empty list, so the table shows "Leaderboard data is not available".

## Things the screen sends or shows that are worth knowing

- The save request for the winner logic always sends the status value "string".
- The default criteria in the screen start with Sub Match on. The server default ladder starts with Sub Match off. The screen shows the saved values once they load.
- The only write from this screen is **Update** in the Winner Logic sidebar. The recalculate, publish, swap and generate-standing calls exist in the component, but no control on this page calls them.

## Frequently asked questions

**Which API loads the Team Leaderboard?** The stage team table reads the group participants route. The ALL view reads the leaderboard-ranking route.

**Which API loads the Player Leaderboard?** The leadership points leaderboard route, grouped by participant.

**How is the final standing worked out?** From the group stage matches of the category, ranked by points and then by the winner logic criteria in order.

**What does the leaderboard return with no rounds?** Success with the "no rounds found" message and an empty list.

**How are equal points ranked?** Equal totals share a position; ties are broken by the enabled winner logic criteria for the final standing.

**Why do squad players show with zero points?** The squad of every fixture team is added at zero when no match type filter is given.

**Which permission saves the winner logic?** Display Settings in edit mode.
