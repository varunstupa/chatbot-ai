---
doc_id: tms.ranking.api
title: Backend logic of the Ranking and Rating APIs – the ranking-rating service, gateway routes, the landing list and publishing
routes:
  - tms/ranking/:param1/:param2/:event_id
aliases:
  - ranking api
  - ranking backend
  - rating api
  - rating backend
  - ranking routes
  - rating routes
  - ranking list api
  - ranking publish api
  - combined ranking and rating api
  - award standing config api
  - event category config api
  - ranking permissions
  - which service computes ranking
  - ranking-rating service
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - Which service calculates the ranking points?
  - What does the backend return for the Ranking Management list?
  - Which permission is needed to publish a ranking list?
  - What does the award and standing config call save?
  - Which ranking routes need a login?
  - What happens when a ranking compute fails?
backend_sources:
  - gateway/src/routers/ranking_router.py
  - gateway/src/routers/ranking_router_v2.py
  - gateway/src/routers/world_ranking_router.py
  - gateway/src/routers/combined_report_router.py
  - gateway/src/routers/ranking_config_router.py
  - gateway/src/routers/rating_config_router.py
  - gateway/src/routers/award_standing_config_router.py
  - gateway/src/routers/category_settings_router.py
  - tms repository, branch rnr_staging: src/main.py (mounted routers)
  - tms repository, branch rnr_staging: src/router/section_router.py (GET /section/v1/by-event)
  - tms repository, branch rnr_staging: src/services/section_service.py and src/crud/section_crud.py
source_files:
  - src/app/core/services/ranking-rating/point-allocation/ranking-management.service.ts
  - src/app/core/services/ranking-rating/award-and-standing/award-and-standing.service.ts
  - src/app/core/constants/api-constant.ts
---
# Backend logic – Ranking and Rating APIs

The ranking, rating, combined and award-standing calls from the admin screens go through the **gateway**, which checks the login and the feature permission and then forwards the call to the **ranking-rating service** (set by the `RANKING_RATING_SERVICE_URL` setting of the gateway).

The ranking-rating service is a separate FastAPI application in the **tms repository, branch `rnr_staging`**. It is not the same code as the TMS application on the `staging` branch. Its routers are mounted under `/v1/rankings`, `/v2/rankings`, `/v1/ratings`, `/config`, `/categories`, `/tournaments`, `/v1/elo-ratings`, `/v1/combined`, `/v1/world-rankings`, `/category_settings`, `/v1/leaderboard`, `/v1/rounding-config` and `/section`. The engines, plugins and publication runs are described in the ranking engine and publication guides.

## Login and permissions

- The gateway checks the login on most routes and checks the feature permission on the write routes. Reads need the feature in read mode; writes need the feature in edit mode.
- The ranking-rating service itself does not check the login or the permission on its routes. It relies on the gateway being the only way in. Some trigger routes say in their own description that they need no login, because they are for internal or admin use.

## The landing list (GET section/v1/by-event)

- Served by the same service (section router, mounted under `/section`). The Ranking Management page uses it.
- The event is linked to its season. An event without a season link gives an empty list.
- The list is the event's categories that belong to the season. Filters: category names, category levels and status. Status "inactive" also matches categories whose configuration status is not set.
- Each row has the category level, the participant type, the configuration type and status, and the number of participants. Sub categories are listed under their parent.
- Paging: the response has the total number of pages and the rows per page (10 by default).

## Gateway routes by area

- **Ranking lists and compute** (ranking router): the lists, a list's detail, compute and its status, the adjustment of a participant's total, the list status, publish, refinalize, the adjustments file and pausing a participant. Writes need the Ranking feature in edit mode.
- **Publication** (ranking router): the publication runs (read), the manual trigger (edit), and the rollback of a run.
- **Standings and reports** (ranking router and ranking router v2): the standings replica (also from a snapshot), the standings export, the ranking changes report and its export, the timeline and a participant's event leaderboard.
- **Audit and history** (ranking router): the ranking history, a player's history, the history restore (edit), the audit runs and a run's player breakdown.
- **World ranking** (world ranking router): the category ranking (read and update, edit), the template, the import (direct and from a file), the import history, apply and discard, the error report and the download. All writes need edit.
- **Combined ranking and rating** (combined report router): the combined lists, the latest list for an event and category (with or without the status filter), the report and its export, the event categories of the combined view, and the publish (login).
## Gateway routes – configuration, rating and awards

- **Configuration** (ranking config router): the tenant system settings (read the Ranking feature; write needs edit), the ranking settings, the countries, the ranking configuration of a category per season (read; write needs edit), the minimal settings of an event category, the event category config (add, delete and bulk write need edit), and the events of a season.
- **Rating configuration** (rating config router): the rating settings, the point exchange, the tenant defaults (player management, inactivity, advance), the tenant filters, the linked and unlinked categories and events (link and unlink), the tournament weight plugin, and the event category points.
- **Award and standing configuration** (award standing config router): read, save and delete the configuration of an event category (login). The page's bulk save uses the event category config bulk route (edit).
- **Category settings** (category settings router): read and update the settings of a category.

## Behaviour on errors

- The ranking compute gate returns "category not in ranking system" (400) when the category has no ranking configuration, and also when an unexpected error happens while the gate is checked.
- Publish, trigger and validation routes return a message key that the gateway translates. The English text of a message can be empty or missing in the translation file; in that case the screen shows the raw key or an empty message.

## Where the publish steps are

- Publishing has two steps: a list is validated first, then published. The steps, the scheduled publication run and the rating publish are described in the ranking publication guide.

## Calls that show on the screen

- The award and standing popup saves the ranking points till a position and the number of positions to calculate with the award standing configuration route (read, save and delete per event and category).
- The allocation page saves the award and standing configuration of the selected categories with one bulk request to the event category config route (edit).
