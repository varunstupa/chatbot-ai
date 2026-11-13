---
doc_id: tms.awards.order-of-merit-sidebar
title: Order of Merit create and edit sidebar – modes, categories, weightage grid, tie-breakers, apply-to-all and saving
routes:
  - tms/awards/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - order of merit sidebar
  - order of merit create award
  - order of merit weightage grid
  - weightage points grid
  - order of merit tie breaker
  - order of merit apply to all
  - order of merit view award
  - order of merit edit award
  - order of merit save
  - weightage over 100 percent
  - event award order of merit
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I create an Order of Merit award on the Awards page?
  - What does each row of the weightage grid mean?
  - Why is the Save button greyed out for Order of Merit?
  - What is the difference between view and edit for a published Order of Merit award?
  - How are the tie breakers used to rank Order of Merit players?
  - What does Apply to all do in the Order of Merit sidebar?
  - Is a new Order of Merit award published straight away?
backend_sources:
  - gateway/src/routers/awards_router.py (awards/v1 event and global awards)
  - tms/src/router/award_router.py
  - tms/src/service/award_service.py (upsert_event_award, _validate_weightage_per_category, _apply_tie_breakers)
  - tms/src/service/award_calculators.py (OrderOfMeritCalculator, OOM_METHOD_STRATEGIES)
  - tms/src/schema/award_schema.py (OrderOfMeritScoring, CategoryScoring, ResultPoints, TieBreaker)
source_files:
  - src/app/modules/tms/award-standings/best-player/components/best-player-tms-positions-view/best-player-tms-positions-view.component.html
  - src/app/modules/tms/award-standings/order-of-merit/components/order-of-merit-create-award-sidebar/order-of-merit-create-award-sidebar.component.html
  - src/app/modules/tms/award-standings/order-of-merit/components/order-of-merit-create-award-sidebar/order-of-merit-create-award-sidebar.component.ts
  - src/app/modules/tms/award-standings/order-of-merit/components/order-of-merit-points-weightage-step/order-of-merit-points-weightage-step.component.html
  - src/app/modules/tms/award-standings/order-of-merit/services/order-of-merit-config.service.ts
  - src/app/modules/tms/award-standings/order-of-merit/constants/order-of-merit.constants.ts
  - src/app/modules/tms/award-standings/shared/utils/order-of-merit-global-award.mapper.util.ts
  - src/app/modules/tms/award-standings/shared/utils/awards-tie-breaker.mapper.util.ts
---
# Order of Merit create and edit sidebar

This guide explains the Order of Merit side panel in depth: which mode it opens in, how the categories are chosen, how each cell of the weightage grid is used, how tie-breakers and apply-to-all work, and what happens on save. The screen labels and the basic steps are in the Best Player and Order of Merit guide (awards-award-types); the server rules are in the operations and API guides.

## Which mode the panel opens in

- **Create Award** on the Awards and Standings page opens the panel for a new **event award**: the award belongs to this event only, and it is saved **unpublished**.
- **View** on an event award opens the panel read only.
- **Edit** on an event award opens the panel with the basic details read only; only the points, the weightages and the tie-breakers can be changed.
- The federation (global) award screen uses the create and edit modes for global awards. An event award keeps the publish state it has when it is edited: a published award stays published after the edit is saved.
- Saving an edit does not change the award's positions. Click **Regenerate Positions** to apply the new points; on a published award the new positions are public at once.
- The panel title is "Create Award", "Edit Award" or "View Award".

## Basic details

- **Award Name** – required; the save button stays greyed out while it is empty.
- **Select Category** – at least one category is required. The categories are loaded from the event (and from the federation for a global award). The list is searchable (the search waits 300 ms after the last key), loads more pages as you scroll, and keeps the categories already chosen at the top.
- Each chosen category becomes a chip; the cross removes it. A removed category's points are dropped from the save.
- **Next** is greyed out until the name and at least one category are set.

## Points step: the weightage grid

- Each category has its own grid. The grid has three rows, one per outcome: **win**, **loss** and **participation**.
- Each row has one or more columns, one per match format the category uses:
  - singles (singles categories),
  - doubles (doubles and mixed doubles categories),
  - teams (team categories).
  Only the column for the category's format is editable.
- Each cell has two boxes: **points** (the points earned for that outcome, zero or more) and **Wt.** (the weightage in percent, zero to 100).
- The points are the points for each win, loss or participation. The weightage is the share of that outcome in the total of the category.
- A category may have no points set; then it adds nothing to the standing.

## Weightage validation

- The screen refuses to save when, for one outcome row, the weightages of the enabled columns add up to more than 100. The message is "Total % exceeds 100. Please input a valid entry" and Save is greyed out.
- The server adds the three weightages of a category together (win, loss and participation) and refuses a total above 100: "Weightage for category '{category_name}' must not exceed 100% (got {total_weight}%)".
- **Finding:** the screen checks each row on its own and the server checks the sum of all three rows. So a category with a win weightage of 60 and a loss weightage of 50 passes the screen and is refused by the server with "… must not exceed 100% (got 110%)". Keep the three weightages of a category to 100 in total.

## Apply to all

- The **Apply to all** toggle copies one grid to every category of the same participant type (singles, doubles or teams).
- The toggle is shown when the points step is filtered to one participant type. With the filter on all types, it is shown for the participant type of the active category.
- The toggle is kept separately for each participant type, so turning it on for singles does not change doubles or teams.
- On save the server does the copying: for each participant type with the toggle on, the grid of the first selected category of that type is copied to the other selected categories of that type.
- Apply to all is not available in view mode.

## Tie-breakers

- Each category has one tie-breaker row, with the criterion set to **win-ratio** by default.
- The criteria offered are **Won** (wins), **Win-Loss** (wins minus losses) and **Win/Loss Ratio** (wins divided by matches played).
- The tie-breaker order follows the order of the categories in the award: the first category is the first tie-breaker. Drag a row by its handle to change the order (not in view mode). A row can be hidden with its visibility (eye) button; hidden rows are not used.
- The server sorts the players by total points, then applies the visible tie-breakers in order. For each tie-breaker the server uses the player's wins (Won), wins minus losses (Win-Loss), or wins divided by matches played (Win/Loss Ratio) in that category. A player not in the category counts as zero for it.
- **Naming note:** the criterion labelled **Win/Loss Ratio** is computed as wins divided by matches played, not wins divided by losses.
- Players still equal after every tie-breaker are put in a fixed internal order, so two players never share a position.

## Save

- **Save** (or **Update** when editing) is greyed out only while a weightage row is over 100.
- With an empty name or no category chosen, clicking **Save** does nothing and shows no message. Fill in the basic details first (**Next** is greyed out until they are complete).
- An event award is saved to the event. A new award is saved unpublished. A failed save shows the server's message, or "Failed to save the award." when the server sends none.
- A new award is refused when its name is already used in the event ("Award name '{name}' already exists in this event") or the Order of Merit type is switched off for the organisation ("This award type is disabled at federation level"). Edits skip both checks.
- A global award is saved to the federation.
- Back and Next move between the basic details and the points step. On the single page layout both appear on one screen.

## Order of Merit sidebar: publishing and deleting

- On the event page the award card itself has only **View** and edit. Click the card to open the award's positions: **Generate Positions** first, then **Publish** or **Publish All**, and later **Un-publish**, each after a confirmation (see the Awards and Standings guide). The standing must be generated before it can be published.
- Deleting an event award removes it from the event (see the awards API guide). Its published standing is not removed with it and can still show publicly, so **Un-publish** the award before deleting it.

## Frequently asked questions

**How do I create an Order of Merit award on the Awards page?** Click **Create Award** on the Order of Merit tab, enter the name, pick the categories, fill the grid and tie-breakers, then click **Save**. The award is saved unpublished.

**What does a row of the grid mean?** The outcome of a player in a category: a win, a loss or a participation. Each row has points and a weightage.

**Why is Save greyed out?** A weightage row is above 100 percent. If the name or a category is missing, Save does nothing, so fill in the basic details first.

**What does Apply to all do?** It copies the grid to the other categories of the same participant type.

**Can I change the basic details of a published award?** No, in the event view and edit the basic details are read only; only the points, weightages and tie-breakers can be changed.

**How are the tie-breakers used?** After total points, the server compares the players by the visible criteria in category order.

**Why is the Save button greyed out for Order of Merit?** A weightage row of a category is above 100 percent. Lower it until the warning goes. If the name or a category is missing, **Save** does nothing, so fill in the basic details first.

## Frequently asked questions (continued)

**What is the difference between view and edit for a published Order of Merit award?** **View** opens the award read only. **Edit** keeps the basic details read only and lets you change only the points, the weightages and the tie-breakers. A published award stays published after the edit is saved.

**How are the tie breakers used to rank Order of Merit players?** Players are sorted by total points first. Players with equal points are then compared by the visible tie-breakers in category order (the first category is the first tie-breaker): **Won** (wins), **Win-Loss** (wins minus losses) or **Win/Loss Ratio** (wins divided by matches played). Hidden rows are not used.

**What does Apply to all do in the Order of Merit sidebar?** It copies one points grid to every category of the same participant type (singles, doubles or teams). It is kept separately for each participant type and is not available in view mode.

**Is a new Order of Merit award published straight away?** No. A new event award is saved unpublished. Click its card, click **Generate Positions**, then **Publish** and **Confirm**.
