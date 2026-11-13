---
doc_id: tms.players.transfer-subcategory
title: Players page – transfer, recreate, merge and sub categories
routes:
  - tms/players/:event_id
aliases:
  - transfer players
  - recreate players
  - merge players
  - merge categories
  - sub category
  - sub categories
  - sub division
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I move a player to another category?
  - What is the difference between Transfer and Recreate?
  - How do I merge two categories?
  - How do I split a category into sub categories?
  - Why is the Sub Category button greyed out?
  - Is the fee refunded when I transfer a player?
backend_sources:
  - gateway/src/routers/registration_router.py (participant transfer: move, duplicate, merge)
  - tms/src/service/transfer strategies (legacy and choreographed move/duplicate)
  - tournament config create_event_categories (sub categories)
source_files:
  - src/app/modules/tms/players/players.component.ts
  - src/app/modules/tms/players/participant-category-action-dialog/participant-category-action-dialog.component.ts
  - src/app/shared/division-creation/division-creation.component.html
  - src/app/modules/tms/players/players.component.html
---
# Players page – transfer, recreate, merge and sub categories

This guide explains how to move participants between categories on the **Players** page and how to split a category into sub categories (sub divisions in leagues).

## Transfer, Recreate and Merge: what each does

- **Transfer** – moves the ticked participants to another category. They leave the current category. The previous category fee is refunded and a new fee applies in the new category.
- **Recreate** – "Player will remain in the current category and also be added to the selected category." You can pick several target categories. No refund is processed for the current category.
- **Merge** – moves all participants of the current category to another category (the server receives only the two categories, not the ticked players); the current category is then removed. A category whose draw already has matches cannot be merged.
- Participants can only go to a category of the same type: "Participants can only be transferred, merged, or recreated into a category of the same type (Singles to Singles, Doubles to Doubles, Team to Team)."

## How to transfer or recreate participants

1. Tick the participants; the selection bar shows **Transfer**, **Recreate** and **Merge**. **Merge** needs at least 2 ticked participants ("Select at least 2 players"), although it still moves the whole category. With nothing ticked these buttons only show "Select players first".
2. In the side panel choose whether the target is a **Category** or a **Sub Category**.
3. Choose the **Payment Mode**: **Cash** or **Online** (Online only when the event takes online payment).
4. Choose the target category (and sub category). "Please select a Category first to see Sub Category options"; "No Sub Categories available for the selected Category".
5. Click the submit button. The confirmation **Transfer Players**, **Recreate Players** or **Merge Players** opens.

## The confirmation window and fees

The window shows **From Category** (or **Current Category**) and **To Category** (or **Another Category**) and the **Fee Adjustment Summary**:
- "Previous category fee will be refunded" (Transfer, Merge) or "No refund will be processed for the current category" (Recreate).
- "A new fee is applicable for the selected category and new order will be created".
- **Payment Method :** Cash or Online. With Online: "Payment link will be Generated and player added to unpaid list of" the target category.

Click **Proceed** to continue or **Cancel**. Moving between sub categories of the same category creates no new order and no refund.

## Transfer messages

- "Participants Moved Successfully", "Participants Duplicated Successfully", "Categories Merged Successfully".
- "Transfer accepted" – the transfer is being processed in the background; the list updates shortly. This is the usual answer when a payment mode is chosen.
- "Sibling-subcategory move completed" – a move between two sub categories of the same category, done at once without a new order or refund.
- "Participant Already Exists In Category" – a participant is already registered in the target category (for Recreate: in any of the chosen targets). Nothing is moved.
- "Cannot merge source event_category … match rows exist (bracket already drawn)." – the current category already has a draw with matches; it cannot be merged.
- "No active participants found for the given ids" – the ticked participants were deleted or moved meanwhile.
- "Please select participants to move" – nothing is ticked.
- "Select participants of the same type. Singles cannot be moved together with Doubles or Team entries."

## Creating sub categories

1. Select the category and click **Sub Category** (**Sub Division** in leagues).
2. The panel **Add Sub Category** (**Add Sub Division** in leagues) shows the category and **Total Registered Participants**. Enter **No. of Sub Category** and **Max Participants Per Sub Category** (both required). The second box stays greyed out with "Please enter Number of Sub Categories first" until the first is filled.
3. Choose the **Bifurcation Criteria**: **Random**, **Ranking/Rating** or **Points**.
4. Check the **Bifurcation Calculation**. "Distribution Error" means the numbers do not fit; **Optimal Solution** suggests numbers that do. You can change the participants per sub category.
5. Tick "To proceed further, please check the box to confirm this bifurcation."
6. For each sub category enter **Sub Category Name** (required), **Abbreviation** and **Color**. Drag to reorder.
7. Click **Add**.

- Unticking the confirmation box, or editing the bifurcation (pencil) after confirming, asks "Are You Sure?" – "This will reset all sub-division data." Click **Yes, confirm** to start the details again or **Cancel** to keep them.
- In leagues the same form says **Division** / **Sub Division** instead of Category / Sub Category.

## When the Sub Category button is available

- **Sub Category** is greyed out until all of these are true: a category is selected, the category has a registration end date, that date and time have passed, and the category has no sub categories yet. A category without a registration end date can never be split here. Hovering shows only the button name, not the reason.
- Once sub categories exist (also while a sub category tab is selected), the button is replaced by an edit **Sub Category** button (pencil icon). It opens the panel **Update Sub Category** (**Update Sub Division** in leagues) for names, abbreviation and colour; the numbers can no longer be changed.
- **Reset Sub Category** (next to the category title) deletes all sub categories of the category; their players go back to the main category. Registered players do not block it, only stages: "Please delete all stages before resetting subcategories." means a sub category has a stage (even a draft draw). Delete those stages first.

## Frequently asked questions about transfer and sub categories

**How do I move a player to another category?** Tick the player, click **Transfer**, choose the category and payment mode, submit and **Proceed**.

**What is the difference between Transfer and Recreate?** Transfer moves the player out of the current category (with refund); Recreate keeps them in the current category and adds them to another one (no refund).

**How do I merge two categories?** Select the category to merge from, tick at least 2 participants, click **Merge**, choose the target category and **Proceed**. All participants of the category are moved, not only the ticked ones.

**Is the fee refunded when I transfer a player?** Yes, the previous category fee is refunded and a new order is created for the new category.

**Why "Transfer accepted" and nothing changed?** The transfer runs in the background; refresh after a moment.

**How do I split a category into sub categories?** **Sub Category** → numbers, criteria, confirm, names → **Add**.

**Why is the Sub Category button greyed out?** No category is selected, the category has no registration end date, its registration end date has not passed yet, or it already has sub categories (then an edit **Sub Category** button is shown instead).

**How do I remove sub categories?** Click **Reset Sub Category**.
