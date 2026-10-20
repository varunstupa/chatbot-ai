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
---
# Players page – transfer, recreate, merge and sub categories

This guide explains how to move participants between categories on the **Players** page and how to split a category into sub categories (sub divisions in leagues).

## Transfer, Recreate and Merge: what each does

- **Transfer** – moves the ticked participants to another category. They leave the current category. The previous category fee is refunded and a new fee applies in the new category.
- **Recreate** – "Player will remain in the current category and also be added to the selected category." You can pick several target categories. No refund is processed for the current category.
- **Merge** – moves all participants of the current category to another category; the current category is then removed.
- Participants can only go to a category of the same type: "Participants can only be transferred, merged, or recreated into a category of the same type (Singles to Singles, Doubles to Doubles, Team to Team)."

## How to transfer or recreate participants

1. Tick the participants and click **Transfer** or **Recreate** (for **Merge** no ticking is needed).
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
- "Transfer accepted" – the transfer is being processed in the background; the list updates shortly.
- "Participant Already Exists In Category" – a participant is already registered in the target category.
- "Please select participants to move" – nothing is ticked.
- "Select participants of the same type. Singles cannot be moved together with Doubles or Team entries."

## Creating sub categories

1. Select the category and click **Sub Category** (**Sub Division** in leagues).
2. The panel shows the category and **Total Registered Participants**. Enter **No. of Sub Category** and **Max Participants Per Sub Category**.
3. Choose the **Bifurcation Criteria**: **Random**, **Ranking/Rating** or **Points**.
4. Check the **Bifurcation Calculation**. "Distribution Error" means the numbers do not fit; **Optimal Solution** suggests numbers that do. You can change the participants per sub category.
5. Tick "To proceed further, please check the box to confirm this bifurcation."
6. For each sub category enter **Sub Category Name** (required), **Abbreviation** and **Color**. Drag to reorder.
7. Click **Add**.

- Unticking the confirmation box, or editing the bifurcation (pencil) after confirming, asks "Are You Sure?" – "This will reset all sub-division data." Click **Yes, confirm** to start the details again or **Cancel** to keep them.
- In leagues the same form says **Division** / **Sub Division** instead of Category / Sub Category.

## When the Sub Category button is available

- **Sub Category** becomes active only after the category's registration has ended and only when the category has no sub categories yet. Hover over it to see why ("Create sub-division for this category" when it is available): "Sub-division creation will be available in N day(s)" (or hours, minutes), "Cannot create sub-division: This category already has sub-categories", "Sub-division creation is not available for this category".
- Once sub categories exist the button opens them for editing (names, abbreviation, colour; the numbers can no longer be changed).
- **Reset Sub Category** (next to the category title) deletes all sub categories of the category. "Cannot Delete Category, Fixtures Already Generated" means a sub category already has a draw; it cannot be removed.

## Frequently asked questions about transfer and sub categories

**How do I move a player to another category?** Tick the player, click **Transfer**, choose the category and payment mode, submit and **Proceed**.

**What is the difference between Transfer and Recreate?** Transfer moves the player out of the current category (with refund); Recreate keeps them in the current category and adds them to another one (no refund).

**How do I merge two categories?** Select the category to merge from, click **Merge**, choose the target category and **Proceed**.

**Is the fee refunded when I transfer a player?** Yes, the previous category fee is refunded and a new order is created for the new category.

**Why "Transfer accepted" and nothing changed?** The transfer runs in the background; refresh after a moment.

**How do I split a category into sub categories?** **Sub Category** → numbers, criteria, confirm, names → **Add**.

**Why is the Sub Category button greyed out?** Registration of the category has not ended yet, or it already has sub categories.

**How do I remove sub categories?** Click **Reset Sub Category**.
