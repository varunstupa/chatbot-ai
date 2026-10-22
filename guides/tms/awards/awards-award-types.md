---
doc_id: tms.awards.award-types
title: Best Player and Order of Merit awards – creating an award, points, weightage and tie-breakers
routes:
  - tms/awards/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - best player award
  - create best player award
  - order of merit award
  - create order of merit
  - award points allocation
  - position points
  - position limit
  - tie breaker criteria
  - weightage
  - win loss ratio award
  - apply to all awards
  - award weightage over 100
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I create a Best Player award?
  - How do I set the points for each position?
  - What is the Order of Merit weightage?
  - Why does the award say "Total % exceeds 100"?
  - What are the tie breaker criteria?
  - What does Apply to all do in an award?
  - How is the Order of Merit points calculated?
backend_sources:
  - gateway/src/routers/award_router.py (awards/v1 global and event awards)
  - tms/src/router/award_router.py
  - tms/src/service/award_service.py (upsert_event_award, _validate_weightage_per_category, sync_awards)
  - tms/src/service/award_calculators.py (BestPlayerCalculator, OrderOfMeritCalculator, OOM_METHOD_STRATEGIES)
  - tms/src/schema/award_schema.py (AwardUpsert, OrderOfMeritScoring, ResultPoints, CategoryScoring)
  - tms/src/common/award_constants.py (AwardType, OoMCalculationMethod)
source_files:
  - src/app/modules/tms/award-standings/best-player/components/best-player-create-award-sidebar/best-player-create-award-sidebar.component.html
  - src/app/modules/tms/award-standings/best-player/components/best-player-point-allocation-step/best-player-point-allocation-step.component.html
  - src/app/modules/tms/award-standings/order-of-merit/components/order-of-merit-create-award-sidebar/order-of-merit-create-award-sidebar.component.html
  - src/app/modules/tms/award-standings/order-of-merit/components/order-of-merit-points-weightage-step/order-of-merit-points-weightage-step.component.html
  - src/app/modules/tms/award-standings/shared/utils/order-of-merit-global-award.mapper.util.ts
---
# Best Player and Order of Merit awards

Two award types exist. **Best Player** gives points for the position a player finishes in. **Order of Merit** gives points for each win, loss or participation, and combines them with weightages. Both are created from the **Create Award** button on the Awards and Standings page (see the awards guide), in a side panel.

## Creating an award

- The panel title is "Create Award", "Edit Award" or "View Award" (view is read only).
- The steps are **Basic Details** and **Points Allocation** (Best Player) or **Point Allocation** (Order of Merit). With the single page layout both appear on one screen.
- **Back** and **Next** move between steps. **Next** stays greyed out until the basic details are complete.
- **Save** (or **Update** when editing) saves the award. **Cancel** and **Close** leave without saving.

## Basic Details

- **Award Name** – "Set name for your award". The name must be unique in the event; a duplicate is refused: "Award name '{name}' already exists in this event".
- **Select Category** – "Select the categories to be awarded inside this award". Pick one or more categories with the multi-select; each chosen category is shown as a chip with a cross to remove it.
- **Apply to all** – a toggle that applies one set of points to all the selected categories.

## Best Player: points for each position

- **Set position Limit** – "Add till which position you wish to award". Type the last position that receives points; the minimum is shown as the first position.
- **Set points for each position** – "Set points allotted to the player for each position based on your limit set above." One box per position; the points are whole numbers of zero or more.
- A position with no points gets zero points.
- **Tie Breaker Criteria** – "Set the tie breaker criteria for resolving equal points across categories." For each category choose one of **Won**, **Win-Loss** or **Win/Loss Ratio**. The choice is saved with the award and is used after total points to rank players with equal points (see the operations API guide, awards-api-operations, for the ranking rule).

## Order of Merit: points and weightage

- **Set points for each category win** – "Set points allotted to the player for each position and the weightage in total calculation."
- The grid has the three outcomes of a player in a category (win, loss and participation). Each outcome has, for each format (points and weightage), the boxes **points** and **Wt.** (weightage, in %).
- The weightages of each outcome of a category must total at most 100. A total above 100 shows "Total % exceeds 100. Please input a valid entry", and **Save** is greyed out until it is fixed. The server refuses a total above 100 as well (400, "Weightage for category '{category_name}' exceeds 100 percent").
- The points and weightages are whole numbers of zero or more; a weightage is at most 100.
- The Order of Merit tie breaker criteria are chosen in the same way as Best Player (Won, Win-Loss, Win/Loss Ratio).

## How Best Player standings are worked out

- Each player's position in a category gives the points from the position table of the award.
- If the category has its own position table, that table is used; otherwise the shared position table is used.
- A player without a position in a category gets zero points.

## How Order of Merit standings are worked out

- The points of a category are worked out from the player's wins, losses and participation (matches played). The screen sends the weightage method, and the server uses it:
  - **Weightage** – wins × win points × win weight %, plus losses × loss points × loss weight %, plus participation points × participation weight % if the player played at least one match.
- The server also knows these methods, which the screen does not offer: win points (wins × win points), win ratio (wins ÷ matches played × win points), win and loss (wins × win points + losses × loss points), and win minus loss ((wins − losses) × win points).
- A category with no points set gives zero points.

## Global and event awards

- An award can be created for the event (event award) or synced from a federation (global) award (see Sync Awards on the awards guide).
- A synced award keeps the points of the global award; it is copied to the event when synced.
- A global award type that is disabled at the federation level cannot be added: "This award type is disabled at federation level".

## Messages

- "Award name '{name}' already exists in this event" – change the name.
- "Total % exceeds 100. Please input a valid entry" – reduce the weightages of the category.
- "This award type is disabled at federation level" – the type is off for the federation.
- "Award not found" – the award was removed; reload the page.
- "Invalid award_type" – the type is not Best Player or Order of Merit.
- "None of the award's categories exist in this event" – no category of the award is in the event; the server message for this has no English text yet.

## Frequently asked questions

**How do I create a Best Player award?** Click **Create Award** on the Best Player tab, name it, select the categories, set the position limit and the points of each position, then click **Save**.

**How do I set the points for each position?** Set the limit, then type the points in each position box.

**What does the weightage mean?** The share of each outcome (win, loss or participation) in the total points of a category. The weightages of a category must total no more than 100 percent.

**Why can I not save the Order of Merit award?** A category total is above 100 percent. Lower the weightages until the warning goes.

**What are the tie breaker criteria?** The criterion chosen for each category to decide between players with equal points: Won, Win-Loss, or Win/Loss Ratio.

**What does Apply to all do?** It applies one set of points to all the selected categories.

**What is the Order of Merit weightage?** Each outcome of a player in a category (win, loss and participation) has points and a weightage (**Wt.**, in %). The points are worked out as wins × win points × win weight %, plus losses × loss points × loss weight %, plus participation points × participation weight % when the player played at least one match. The weightages of one category must total at most 100.

**Why does the award say "Total % exceeds 100"?** The weightages of one category's outcomes (win, loss and participation) add up to more than 100. Lower them until the total is 100 or less; **Save** stays greyed out until then.

**How is the Order of Merit points calculated?** For each category: wins × win points × win weight %, plus losses × loss points × loss weight %, plus participation points × participation weight % if the player played at least one match. A category with no points set gives zero points.
