---
doc_id: tms.ranking
title: Ranking and Rating management page – the category list, filters, modes and how to open a category
routes:
  - tms/ranking/:param1/:param2/:event_id
aliases:
  - ranking
  - ranking page
  - ranking management
  - rating management
  - rankings and ratings
  - ranking points
  - rating points
  - points allocation
  - ranking category list
  - add ranking point
  - edit ranking point
  - configuration type
  - ranking and rating
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Ranking page for?
  - What is the difference between Ranking, Rating and Ranking and Rating?
  - How do I add ranking points to a category?
  - How do I filter the categories on the Ranking page?
  - What does the Configuration Type column mean?
  - Why is the Ranking page empty?
  - What do the Status values mean?
backend_sources:
  - tms/src/router/section_router.py (GET v1/by-event)
  - tms/src/service/section_service.py (get_categories_by_event)
  - tms/src/crud/section_crud.py (fetch_event_categories_with_details)
  - gateway/src/routers/ranking_config_router.py (tenant system settings, ranking settings)
  - gateway/src/routers/ranking_router.py
  - gateway/src/routers/combined_report_router.py
source_files:
  - src/app/modules/tms/ranking-point/ranking-point.component.html
  - src/app/modules/tms/ranking-point/ranking-point.component.ts
  - src/app/core/services/ranking-rating/ranking-point-navigation.service.ts
  - src/app/core/utils/ranking-point-rows.util.ts
  - src/app/shared/no-event-selected/no-event-selected.component.ts
  - src/app/core/services/ranking-rating/point-allocation/ranking-management.service.ts
  - src/app/core/services/season-config/season-config.service.ts
  - src/app/modules/tms/tms.module.ts
---
# Ranking and Rating management page

The **Ranking Management** page (route `tms/ranking/:param1/:param2/:event_id`) lists the categories of an event that take part in the player rankings or ratings, and starts the point allocation of each. The page title changes with the system in use: **Ranking Management** for ranking, **Rating Management** for rating, and **Rankings and Ratings Management** when both are used (or when no system is set).

The example `tms/ranking/0/-1/1358` sets the first parameter to 0, the second to -1 and the event to 1358. The page reads the event from the browser session (the same event as the rest of the admin), and the parameters are not used for the list. With no event selected the page shows the "No record found" state with the text "Create Event to begin with Rankings." and a **Go to Event** button, and makes no event calls.

## Ranking page – where to find it
Open **Rankings** from the sidebar. It shows only when your organisation has rankings turned on. The sidebar label is **Ratings** for the rating system and **Rankings and Ratings** when both are used.

## Ranking page – which system it shows
- The page asks the season settings which system the tenant uses:
  - **Ranking** – points-based ranking. Labels and actions say "ranking points".
  - **Rating** – Elo-style rating. Labels and actions say "rating points".
  - **RankingAndRating** – both. The page shows the combined view.
- The chosen system is remembered for the other ranking pages in the same browser.
- If the settings say neither, the page shows no list and the title is the generic "Rankings and Ratings Management".

## Ranking page – header
- The title is one of "Ranking Management", "Rating Management" or "Rankings and Ratings Management" (see above).
- **Points Allocation** is the only tab. It is selected by default.
- There is no separate create button on this page: a category's allocation is opened from its row (see "Ranking page – what a row opens").

## Ranking page – filters
- **Category Name** – a dropdown with check boxes. Tick one or more category names.
- **Category Level** – check boxes for the category levels (the level names are shown in display form).
- **Status** – check boxes for the configuration status. "inactive" covers categories with no status set.
- The filter labels show the selected values. Clicking outside a dropdown closes it.
- Changing a filter reloads the list from the first page. Each tick closes the dropdown; open it again to tick another value. Tick a value again to remove it.
- The options are built from the event's categories (up to 100). If they cannot be loaded, "Failed to fetch filter options. Please try again." is shown.
- When both systems are used, the options come with the list itself.

## Ranking page – the list
- Columns: **Category Name**, **Sub Category** (shown when the event has sub categories), **Participant Type**, **Category Level**, **No. of participants**, **Configuration Type** (ranking and combined only), **Status** and **Action**.
- Each row has an action button. The tooltip is one of:
  - "Add ranking point" or "Edit ranking point" (ranking), or
  - "Add rating point" or "Edit rating point" (rating),
  depending on whether the category already has an active configuration.
- Clicking a row (or its action) opens the category in the allocation flow (see the allocation guide).
- The action icon is a pencil ("Edit Ranking Point" / "Edit Rating Point") for an active category and a plus ("Add Ranking Point" / "Add Rating Point") otherwise.
- "No data available" when the list is empty.

## Ranking page – paging
- Shown only when the list has rows. It shows the first row number, the page size dropdown and the total, for example "1 - [10] of 42". The page size is 10, 25 or 50; changing it goes back to page 1.
- First, previous, up to three page numbers, next and last. The buttons are greyed out at the ends.

## Ranking page – status and configuration values
- The **Status** of a category is its configuration status (active or inactive). A category that has not been set up is inactive.
- The **Configuration Type** is **Stages** (points by stage reached) or **Awards & Standing** (points by final position). A category with no type chosen shows "-".
- Status and level are shown with a capital first letter ("Active", "Inactive").

## Ranking page – what a row opens
Clicking a row opens the allocation page that fits the category:

- **Rating**: always the stages page.
- **Ranking**: no configuration type yet, or inactive → the allocation page with the **Stages** and **Award and Standing** cards (an inactive team category opens the stages page instead). Active with Awards & Standing → the award and standing page; active with Stages → the stages page.
- **Rankings and Ratings**: team categories always open the award and standing page. Others follow the ranking rules above.
- For ranking, nothing opens when the event has no season. The allocation pages show a back arrow that returns to this page.

## Ranking page – messages
- "No data available" – the list is empty.
- If the ranking list cannot be loaded, the list is left empty without a message. The server refuses the list of an event that is not linked to a season ("Event Must Be Linked To Season"), so the page stays empty.
- "Failed to fetch filter options. Please try again." – the filter options could not be loaded.
- "Failed to fetch rating data. Please try again." – the rating list could not be loaded.
- The allocation pages show their own messages (see the allocation guide).

## Ranking page – permissions
- The list is read with the login of the user. Changing points needs the ranking permission (Edit). The server refuses changes without it.

## Frequently asked questions: Ranking page

**What is the Ranking page for?** Choosing the categories of an event that feed the player rankings or ratings, and opening each one to set its points.

**What is the difference between ranking, rating and both?** Ranking gives points by stage or by final position. Rating uses an Elo-style rating that changes with each match result. The page shows the system the tenant uses.

**How do I add ranking points to a category?** Click the row or its plus icon ("Add Ranking Point"). The allocation of the category opens.

**Why is the Ranking page empty?** Either no event is selected (open the event first), the event is not linked to a season, the season settings have neither system switched on, the event's categories are not in the season, or no category matches the filters.

## Frequently asked questions: Ranking page – more questions
**What do the Status values mean?** Active means the category has a configuration in use; inactive means it has none or it is switched off.

**How do I filter the categories on the Ranking page?** Use the filters above the list: **Category Name** (tick one or more names), **Category Level** and **Status**. Changing a filter reloads the list from the first page.

**What does the Configuration Type column mean?** It shows how the category's points are allocated: **Stages** or **Awards & Standing**. A category that has not been set up shows "-" and is inactive.

**Why does clicking a category do nothing?** For ranking, the event must be linked to a season. Link the event to a season first.
