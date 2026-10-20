---
doc_id: tms.players.queue-delete-forfeit
title: Players page – queue, delete, forfeit and unpaid players
routes:
  - tms/players/:event_id
aliases:
  - delete player
  - queue list
  - deleted players
  - forfeit player
  - undo forfeit
  - unpaid players
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I delete a player?
  - What is the difference between Delete and Delete & Refund?
  - How do I move a player to the queue?
  - How do I forfeit a player?
  - How do I add an unpaid player to the list?
  - Why can I not delete a player?
backend_sources:
  - gateway/src/routers/registration_router.py (update_event_participant_status, withdraw_self_registered_player, mark_participants_paid)
  - gateway/src/handlers/registration/mark_participants_paid.py
  - tms/src/service/registration_service.py (update_event_participant_status, _apply_manual_queue_moves)
source_files:
  - src/app/modules/tms/players/players.component.ts
  - src/app/modules/tms/queue-and-deleted-players/queue-deleted-players.component.html
  - src/app/shared/forfeit-common-dialog/forfeit-common-dialog.component.html
  - src/app/modules/tms/players/unpaid-players-dialog/unpaid-players-dialog.component.ts
---
# Players page – queue, delete, forfeit and unpaid players

This guide explains how to remove participants from a category on the **Players** page, move them to the queue, forfeit them, and bring unpaid players into the list.

## Deleting players: Delete and Delete & Refund

- One participant: ⋮ in the **Action** column → **Delete** or **Delete & Refund** (in league events: the delete icons on the row).
- Several: tick them and click **Delete** or **Delete & Refund** in the toolbar.
- There is no confirmation window – the participant is removed at once and moves to the **Deleted** list.
- **Delete** removes the participant without a refund. **Delete & Refund** also refunds the registration fee.
- As an organiser you are not bound by the deregistration rules (deadlines) that apply to players.
- "Participant In Stage Cannot Delete" – the participant is already in a stage of the draw and cannot be deleted. Use **Forfeit** instead.

## The Deleted list and restoring deleted players

- With nothing ticked, click **Deleted** to open the deleted list of the category.
- Columns: **S.No**, **Player** (Player 1 / Player 2 for pairs, **Team Name** and player counts for teams), **Member Association**, **Club**, the player type (**Federation-Registered Player** / **Unaffiliated Player** / **Passport-Eligible Player**, singles), **Registration Entry Date**, **Status**.
- **Status** shows **Delete** (deleted without refund) or **Delete With Refund (amount)** with the refunded amount.
- **To restore**: ⋮ on the row → **Add to List**. The entry returns to the player list. Restoring works one entry at a time (the Deleted list has no **Add to List** button for several entries).
- "Participant Already Exists In Category" when restoring – the person is already registered in the category again.
- **Export** opens the export panel for the deleted participants of this category (see the import and export guide).

## Moving players to the queue

- Tick participants and click **Add to Queue**. They leave the player list and appear in the queue (the **Queue** button shows the count).
- A participant already in a stage of the draw, or in the middle of a transfer, is not moved: "Some participants were moved to the queue and others were skipped".
- To bring them back: **Queue** → tick them → **Add to List**, or ⋮ on a row → **Add to List**.
- The **Queue** window (**List of Queued Teams**) shows **S.No**, **Player**, organisation columns, the citizen type, **Registration Entry Date** and **Action**.

## Forfeit and Undo Forfeit

1. ⋮ on the row → **Forfeit**.
2. The window **Forfeit Player ?** says "You are about to Forfeit this Player-" (or Team) with the name and "The following changes will happen: Once you confirm the action, all the upcoming matches should automatically be scored and the opponent gets the win."
3. Confirm. The row then shows a red mark and "(forfeited)".

To reverse it: ⋮ → **Undo Forfeit**. "Once you confirm the Undo action, all the previous match data scored will be restored."

In league events use the **F** icon in the **Action** column instead of ⋮.

## What the server does on Forfeit and Undo Forfeit

- Forfeit marks the participant as forfeited and scores their pending matches as walkovers: the opponent wins. Only matches that already have a real opponent are scored now. In knockout draws, a later match of the forfeited participant is scored as a walkover when its opponent becomes known.
- The participant stays in the draw and in the list; it is not deleted.
- Messages: "Forfeit applied successfully", "Forfeit undone successfully".
- "Match Walkover Not Updated" – a match could not be scored; nothing is forfeited. "Match Data Not Reset" – undo failed. Try again.
- "Participant Not Found" – the entry was deleted meanwhile.

## Unpaid Players

- **Unpaid Players** opens the list of participants registered but not yet paid: **Sr.No**, **Player Name**, **Back No.**, **Seeding**, **Association**, **Club**, **Payment Status** (Unpaid), **Action**.
- Tick players and click **Add to List**, or use the row's add button. The players are marked paid and move to the category list.
- Only players whose order is already paid (online or cash) can be added; players without a paid order stay on the list. "Order Not Found" means none of the selected players has a paid order.
- Search with **Search**. "No record found" means nobody is unpaid.

## Frequently asked questions about queue, delete and forfeit

**How do I delete a player?** ⋮ → **Delete**, or tick players and click **Delete**.

**What is the difference between Delete and Delete & Refund?** **Delete & Refund** also refunds the fee; **Delete** does not.

**Is there a confirmation before deleting?** No, the participant is deleted at once. Restore them from the **Deleted** list if needed.

**Why can I not delete a player?** They are already in a stage of the draw ("Participant In Stage Cannot Delete"). Forfeit them instead.

## Frequently asked questions about the queue and the Deleted list

**How do I move a player to the queue?** Tick them and click **Add to Queue**.

**How do I bring a queued player back?** **Queue** → tick → **Add to List**.

**How do I restore a deleted player?** **Deleted** → ⋮ on the player's row → **Add to List**.

**What does "Delete With Refund" in the Deleted list mean?** The entry was deleted with **Delete & Refund**; the amount shows what was refunded.

**How do I forfeit a player?** ⋮ → **Forfeit** → confirm. Their upcoming matches are scored as wins for the opponents.

**What happens to matches when I forfeit a player?** Their pending matches that already have an opponent are scored as walkovers – the opponent wins. In knockout draws later matches are scored the same way once the opponent is known. The player stays in the draw. **Undo Forfeit** restores the previous match data.

**How do I add an unpaid player to the list?** **Unpaid Players** → tick → **Add to List**. It only works when the player's order is paid.
