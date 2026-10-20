---
doc_id: tms.ranking.engines
title: How ranking and rating points are calculated – the Elo rating engine, the rating batch, normalization, the ranking pipeline and rank assignment
routes:
  - tms/ranking/:param1/:param2/:event_id
aliases:
  - elo rating
  - elo formula
  - how rating changes
  - rating calculation
  - rating k factor
  - provisional k factor
  - draw bonus rating
  - rating normalization
  - end of season normalization
  - ranking calculation
  - how ranking points are calculated
  - ranking rank assignment
  - tie breaker ranking
  - protected players ranking
  - ineligible players ranking
  - league points bonus
  - match outcome bonus points
  - ranking rounding
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How is the Elo change for a match calculated?
  - What is the K factor for a new player?
  - How is a draw treated in the rating?
  - When is a rating normalized?
  - How are ranking points added up?
  - How are players with the same points ranked?
  - Where do the league bonus points come from?
  - How are protected players ranked?
backend_sources:
  - tms repository, branch rnr_staging: src/rating/engines/elo.py (BaseEloEngine, calculate_elo_change)
  - tms repository, branch rnr_staging: src/rating/base_rating_engine.py (plugin phases)
  - tms repository, branch rnr_staging: src/rating/singles/singles_rating_engine.py
  - tms repository, branch rnr_staging: src/services/rating_service.py (calculate_ratings_for_matches, _apply_normalization_waterfall)
  - tms repository, branch rnr_staging: src/plugins/rating_match_outcome_points_plugin/rating_match_outcome_points_plugin.py
  - tms repository, branch rnr_staging: src/ranking/base_ranking_engine.py (pipeline, finalize, rank assignment)
  - tms repository, branch rnr_staging: src/ranking/singles/singles_ranking_engine.py
  - tms repository, branch rnr_staging: src/services/ranking_service.py (_convert_tms_matches_to_engine_format)
  - tms repository, branch rnr_staging: src/plugins/ranking_protection_plugin/ranking_protection_plugin.py
source_files:
  - src/app/modules/tms/ranking-allocation/edit-sidebar/edit-sidebar.component.html
  - src/app/modules/tms/ranking-allocation/stages/stages.component.html
---
# How ranking and rating points are calculated

This guide explains the calculation behind the Ranking and Rating pages. The engines run in the ranking-rating service (see the Ranking API guide). Two families of calculation exist: **rating** (Elo, a number that moves with every result) and **ranking** (points added up from the results, then ordered).

## Elo rating for one match

- A new player starts at a rating of 1500 unless a seed rating is set. The rating deviation and volatility default to 350 and 0.06.
- The expected score of a player is `1 / (1 + 10^((opponent - player) / 400))`. The difference between the two ratings is limited to ±800 before this is used.
- The change of a player is `K × (actual score − expected score)`. The actual score is 1 for a win, 0.5 for a draw and 0 for a loss.
- **K factor**: a player with fewer matches than the provisional threshold uses the provisional K factor; everyone else uses the normal K factor. Each side uses its own K, so the two changes of one match are not always equal and opposite.
- **Draw bonus**: in a draw, if the opponent is higher rated by more than the draw margin, the lower-rated player gets the configured bonus points added to the change.
- Changes are rounded to two decimals. A player's new rating is the rating at the start plus the sum of the changes in the run. Each match also stores the running rating after that match.

## Provisional and special matches

- The change of each side is passed through the provisional policy, which looks at whether the opponent is temporary or eligible. A special outcome (for example a walkover) that already has a change uses that change instead of the Elo formula.
- Every match of a batch uses the ratings from before the batch, so the order of the matches inside a batch does not change the result.

## Plugin phases

The rating plugins run in this order:

1. PRE_CALC plugins (before the engine).
2. The Elo engine.
3. BASE_POINTS, then CONTEXT_ADJUSTMENT (the match outcome bonus points), then MULTIPLIER (the tournament weight), then TEMPORAL, FILTERING, FINALIZATION and OTHER.

The bonus points of a match are added after the MULTIPLIER phase, so the tournament weight is applied to them.

## Match outcome bonus points (league points)

- A rule per outcome: **Win**, **Lost** (a loss), **Tie** (a draw) and **Participant** (given for playing, whatever the result).
- For a match that is not an unfinished special outcome the outcome points are added. An unfinished special outcome gets only the Participant points.
- The points are stored as a league-points component of the player, weighted by the tournament weight.

## Rating batch (how a rating run is organised)

- The run starts from the latest official rating list (the seed) and a draft list for the event.
- The requested matches are fetched. For a league event the run uses the matches it is given. For a team category only singles sub-matches that have a winner are rated. Held matches and matches already in a list are left out unless a recalculation is forced.
- The matches are grouped by season, category, event and stage. Each group is one batch with its own settings.
- The players of the batch are read from the master entity map. The engine runs on the batch, then the results are saved as one new snapshot list.
- A country eligibility filter keeps players outside the selected countries out of the snapshot; they still take part in the calculation as opponents.
- A batch that raises an error is logged and skipped, and the run continues with the other batches.

## Normalization

- Normalization is an end-of-season adjustment. Players are grouped by gender and placed in rating classes from the class boundaries.
- If a class has more players than its target count, the players with the lowest original ratings move to the next lower class. The lowest class is not limited, because there is no lower class to move players to. The cascade runs from the top class down.
- Inside each final class, ratings are stretched linearly onto the class band: the lowest rating maps to the band minimum and the highest to the band maximum. A class where everyone has the same rating gets the middle of its band.
- Each change is stored as a normalization adjustment on the player.

## Ranking points

- The ranking engine has three variants: singles, doubles and teams. All three use the same steps.
1. **Initialise** each player.
2. **Prepare the matches**: each match gives a result (win, loss or draw) to each side; a match with no winner is recorded as a draw. The opponent's rank, membership and world rank, the games won, head-to-head wins, walkover and forfeit flags and the last match date are stored.
3. **Run the plugin pipeline** in the configured order. The prioritized-events plugin is handled before the pipeline.
4. **Finalise**: the total of each player is the sum of the point components plus any U21 transfer points, rounded with the rounding rule of the category (nearest, 0 decimals if no rule is set).

## Eligibility, protection and rank assignment

- A player who is not eligible for ranking gets no rank. Ineligible players are listed last, by points.
- A protected player (a ranking freeze with a start and end date) is ranked after all unprotected eligible players, in name order.
- Unprotected eligible players are sorted by total points, highest first.
- **Without a tie-breaker**: players with the same points share a rank, and the next rank skips the number of tied players (1, 1, 3).
- **With a tie-breaker plugin** that has criteria: players with the same points are ordered by the criteria, and each player gets a different rank in order (1, 2, 3).

## Frequently asked questions

**How is the Elo rating change for a match calculated?** Each player's change is K multiplied by the actual score minus the expected score. The actual score is 1 for a win, 0.5 for a draw and 0 for a loss. The expected score is 1 divided by 1 plus 10 raised to the power of (opponent rating minus player rating) divided by 400. The K factor is the provisional value for a player with few matches, and the normal value otherwise. In a draw the lower-rated player can receive the draw bonus points on top.
