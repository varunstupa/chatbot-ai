---
doc_id: tms.ranking.publication
title: Ranking and rating publication – validate, publish, the scheduled publication run, deductions, restore and the leaderboard snapshot
routes:
  - tms/ranking/:param1/:param2/:event_id
aliases:
  - publication
  - publish ranking
  - publish rating
  - validate ranking list
  - validate rating list
  - publication run
  - publication pipeline
  - scheduled publication
  - manual publication trigger
  - point deduction publication age
  - publication history
  - restore leaderboard
  - leaderboard snapshot
  - why is my list not published
  - publication status
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What are the states of a ranking or rating list?
  - Why is my ranking list not live after I clicked Proceed?
  - What is the difference between validating and publishing?
  - When does the publication run happen?
  - How do I trigger publication now?
  - What does the publication run do in order?
  - Why does a publication run show failed?
  - How do I restore an old rating leaderboard?
backend_sources:
  - tms repository, branch rnr_staging: src/router/ranking_router.py (publish route, publication-pipeline trigger)
  - tms repository, branch rnr_staging: src/router/rating_router.py (publish, validate, trigger-rating-publication, publication-pipeline runs, restore)
  - tms repository, branch rnr_staging: src/services/rating_service.py (validate_rating_list, publish_rating_list, _publish_list_via_rebase, process_and_publish_validated_lists)
  - tms repository, branch rnr_staging: src/services/ranking_publication_pipeline.py (RankingPublicationPipeline)
  - tms repository, branch rnr_staging: src/tasks.py (publish_validated_rankings_task)
  - tms repository, branch rnr_staging: src/crud/rating_list_crud.py (get_all_validated_lists)
  - tms repository, branch rnr_staging: src/crud/ranking_crud.py (get_all_validated_lists_for_context_bulk)
source_files:
  - src/app/modules/tms/ranking-allocation/stages/stages.component.html
  - src/app/modules/tms/ranking-allocation/award-and-standing/award-and-standing.component.html
---
# Ranking and rating publication

A list goes through three states: **calculated** (or **edited** after a change) → **validated** → **published**. Publishing makes the list the live one that the public standings and player pages read. A published list is never changed in place; a new calculation creates a new list.

## Ranking lists

- **Submit for publication** (the Proceed button, the publish route of the ranking router) validates the list. The reply is "submitted for publication" (the message key RANKING_LIST_SUBMITTED_FOR_PUBLICATION; its English text is empty in the translation file, so the screen may show an empty message). Errors: "not found" (404) for a missing list, "validation error" (409) when the list cannot be published, and a generic publication error (500).
- A validated list is **not** published at once. It waits for a publication run.
- The **publication run** (the publish task) promotes it. It runs on the schedule of each season and category, and it can be started now with the trigger route ("Publication pipeline triggered" with a task id). The trigger is for one tenant and processes all active seasons and categories at once.
- The run holds a lock per tenant for 30 minutes and extends it for each season. If the lock is lost during the run, the run stops so that two runs never publish at the same time.

## What one publication run does

For each tenant, then each active season:

1. **Global settings snapshot** (once per tenant): the settings draft is published as a snapshot.
2. **Pass 1 – context snapshots**: for each category with a pending settings draft, the draft is published as a snapshot. This does not need validated lists.
3. **Pass 2 – promote**: for each category, the validated lists are processed oldest first, so the latest list is the one that stays published. Each list gets its point deductions (publication-age bands, recorded once per list) and then becomes PUBLISHED with the snapshot id.
4. **Pass 3 – deductions on published lists**: the same deductions are applied to lists that are already published. Running this more than once a day does not deduct twice.

- A list that fails is logged and skipped; the other lists go on.
- A run writes a pipeline log row when at least one list was promoted, a snapshot was published, or the run failed for the tenant. A run with nothing to do writes no row.
- The run also has a **scheduled** mode (only the contexts that are due, as the schedule decides) and a **manual** mode (everything, ignoring the schedule).

## Rating lists

- **Validate**: a calculated or edited rating list becomes validated. Players in the list who have no alternate rating record get one with 0 (and a history row). Only calculated or edited lists can be validated; other states are refused with "Only 'calculated' or 'edited' lists can be validated".
- **Publish** (the manual publish route): only a **validated** list can be published; otherwise the publish is refused ("Cannot publish list ... from status ..."). Publishing:
  1. locks the list row;
  2. rebuilds each player's entries from the list's history;
  3. copies the new rating, the status, the deviation, the volatility, the last match date and the match count to the live rating of each player;
  4. marks the list PUBLISHED with the publication date, and writes an admin audit row;
  5. builds a new leaderboard snapshot.
- The server replies with the message key RATING_LIST_PUBLISHED; the screen shows its own success text ("Rating List published successfully").
- **Publish all validated** is the batch publish used by the rating publication task. It publishes every validated list of the tenant, oldest first, then builds one leaderboard snapshot for the run. Lists that fail are skipped.
- The trigger route for rating publication runs the rating publication task for one tenant ("Rating publication task triggered").
- A publish that is already done for a list is refused by its status; a list can only be published once from VALIDATED.

## Restore

- **Restore leaderboard** creates a new published leaderboard list copied from a historical list. It is a temporary hold: the next real publication recomputes the board and may or may not keep the restored order. The reason is required and is stored with the pipeline run.
- Ranking also has a restore for a historical ranking list and for an audit run.

## Pipeline runs

- The runs list for a tenant (rating) shows each run with its trigger type (scheduled, manual or post-validation), its status (running, success or failed), the number of lists published and the failure reason when it failed.

## Permissions

- Validating, publishing, triggering a run and restoring need the ranking or rating feature in edit mode through the gateway. The trigger routes of the ranking-rating service themselves do not check the login (see the Ranking API guide).

## Frequently asked questions

**Why is my ranking list not live after I clicked Proceed?** Proceed only validates the list. It goes live in the next publication run for its season and category, or after a manual trigger.

**What is the difference between validating and publishing?** Validating marks the list as ready. Publishing makes it the live list. For rating, the publish step is separate and manual; for ranking, the publication run does it.

**How do I publish now?** Trigger the publication pipeline for the tenant (ranking) or the rating publication task (rating) from the admin tools.

**What does the run do first?** It publishes the settings snapshots, then promotes the validated lists oldest first, then applies the deductions on published lists.

**How do I restore an old leaderboard?** Use the restore action on the history screen with a reason. It creates a new published list from the old one.
**How do I publish a ranking list?** Open the list on the Ranking Management page, click **Publish report**, read the confirmation, then click **Proceed**. This validates the list. The list goes live when the publication run promotes it, on its schedule or after a manual trigger.
