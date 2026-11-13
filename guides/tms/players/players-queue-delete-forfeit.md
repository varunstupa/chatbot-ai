---
doc_id: tms.players.queue-delete-forfeit
title: Players page – queue, delete, forfeit and unpaid players
routes:
  - tms/players/:event_id
aliases:
  - delete player
  - remove player
  - remove participant
  - remove player from category
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
  - What happens when I remove a player from a category?
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
  - src/app/modules/tms/queue-and-deleted-players/queue-deleted-players.component.ts
  - src/app/shared/forfeit-common-dialog/forfeit-common-dialog.component.html
  - src/app/modules/tms/players/unpaid-players-dialog/unpaid-players-dialog.component.ts
  - src/app/modules/tms/players/unpaid-players-dialog/unpaid-players-dialog.component.html
  - src/app/modules/tms/players/players.component.html
---
# Players page – queue, delete, forfeit and unpaid players

This guide explains how to remove participants from a category on the **Players** page, move them to the queue, forfeit them, and bring unpaid players into the list.

## Deleting players: Delete and Delete & Refund

- One participant: ⋮ in the **Action** column → **Delete** ("no refund") or **Delete & Refund** (in league events: the delete icons on the row).
- Several: tick them; the selection bar shows **Delete** ("no refund") and **Delete & Refund**.
- In tournaments a confirmation opens first (see below). In league events the row icons delete at once, without it.
- The participant then moves to the **Deleted** list. **Delete** removes the participant without a refund. **Delete & Refund** also refunds the registration fee.
- As an organiser you are not bound by the deregistration rules (deadlines) that apply to players.
- "Participant In Stage Cannot Delete" – a participant is already in a stage of the draw and cannot be deleted. If any of the ticked participants is in a stage, none of them is deleted. Use **Forfeit** instead.
- Success: "Participants Updated Successfully".

## Delete confirmation on the Players page

- **Delete**: title "Delete N without refund" – "Removes the entries. The entry fee is kept." – "Removed from category & draws", "No refund issued".
- **Delete & Refund**: title "Delete N with refund" – "Removes the entries and returns the entry fee." – "Removed from category & draws", "Entry fee refunded to player", "Can't be changed back to Deleted".
- The names of the entries are listed (the first three, then "+N more").
- Click **Delete** or **Delete & refund** to confirm, or **Cancel** (or Escape) to keep them.

## The Deleted list and restoring deleted players

- With nothing ticked, click **Deleted** to open the deleted list of the category.
- Columns: **S.No**, **Player** (Player 1 / Player 2 for pairs, **Team Name** and player counts for teams), **Member Association**, **Club**, **Registration Entry Date**, **Status**. (The player type column is shown in the Queue list only.)
- **Status** shows **Delete** (deleted without refund) or **Delete With Refund (amount)** with the refunded amount.
- The header has **Edit** (change statuses, see below), **Export** and a close button.
- **To restore**: ⋮ on the row → **Add to List**. The entry returns to the player list. Restoring works one entry at a time (the Deleted list has no **Add to List** button for several entries).
- "Participant Already Exists In Category" when restoring – the person is already registered in the category again.
- **Export** opens the export panel for the deleted participants of this category (see the import and export guide).

## Deleted list: changing Deleted to Delete With Refund

1. In the Deleted list click **Edit** (greyed out when the list is empty). An "Editing status" chip and the note "You can change Deleted to Delete With Refund. Entries already marked Delete With Refund are locked and can't go back to Deleted." appear; row tick boxes are hidden.
2. Switch the toggle of each **Deleted** entry to **Delete With Refund** ("Refund will be issued on save"). Entries already refunded show a lock: "Locked – can't revert to Deleted".
3. The footer counts the changes ("N entries will change to Delete With Refund", or "No changes yet – switch a Deleted entry to Delete With Refund."). **Save Changes** is greyed out until there is a change; **Cancel** leaves edit mode.
4. **Save Changes** asks "Refund N entries?" – "They'll move from Deleted to Delete With Refund. This can't be undone." Click **Confirm refund** (or **Go back**). Success: "N entries refunded".

## Moving players to the queue

- Tick participants and click **Add to Queue**. They leave the player list and appear in the queue (the **Queue** button shows the count).
- A participant already in a stage of the draw, or in the middle of a transfer, is not moved. The others still move: "Some participants were moved to the queue and others were skipped".
- When none can be moved the message gives the reason: "This participant is already in a stage and cannot be moved to the queue", "This participant is part of an ongoing transfer and cannot be moved to the queue", or (mixed reasons) "None of the selected participants could be moved to the queue".
- Moving to the queue removes the participant's seed. It does not come back when the participant returns to the list; seed again.
- To bring them back: **Queue** → tick them → **Add to List**, or ⋮ on a row → **Add to List**.
- The **Queue** window (**List of Queued Teams**) shows **S.No**, **Player**, organisation columns, the citizen type, **Registration Entry Date** and **Action**.

## Forfeit and Undo Forfeit

1. ⋮ on the row → **Forfeit**.
2. The window **Forfeit Player ?** says "You are about to Forfeit this Player-" (or Team) with the name and "The following changes will happen: Once you confirm the action, all the upcoming matches should automatically be scored and the opponent gets the win."
3. Click **Yes, Confirm** (or **Cancel** to keep the participant). The row then shows a red mark and "(forfeited)".

To reverse it: ⋮ → **Undo Forfeit**. "Once you confirm the Undo action, all the previous match data scored will be restored."

In league events use the **F** icon in the **Action** column instead of ⋮.

## What the server does on Forfeit and Undo Forfeit

- Forfeit marks the participant as forfeited and scores their pending matches as walkovers: the opponent wins. Only matches that already have a real opponent are scored now. In knockout draws, a later match of the forfeited participant is scored as a walkover when its opponent becomes known.
- The participant stays in the draw and in the list; it is not deleted.
- Messages: "Forfeit applied successfully", "Forfeit undone successfully".
- "Match Walkover Not Updated" – a match could not be scored; nothing is forfeited. "Match Data Not Reset" – undo failed. Try again.
- "Participant Not Found" – the entry was deleted meanwhile.
- **Undo Forfeit** is refused once later matches depend on the walkover: "Cannot undo forfeit in this knockout stage" or "Cannot undo forfeit in this group stage" (a later round of that draw has been scored), "Cannot undo forfeit: a subsequent stage is affected" (the opponent has already played in a later stage).

## Unpaid Players

- **Unpaid Players** opens the list of participants registered but not yet paid: **Sr.No**, **Player Name**, **Back No.**, **Seeding**, **Association**, **Club**, **Payment Status** (Unpaid), **Action**.
- Tick players (or **Select all**) and click **Add to List**, or use the row's add button. **Add to List** stays greyed out until at least one player is ticked. The players are marked paid and move to the category list; the server's message confirms it.
- Only players whose order is already paid (online or cash) can be added; players without a paid order stay on the list. The order itself is not changed.
- When none of the ticked players has a paid order: "Please complete the payment before adding the participant to the Main List." (an online payment is still open), "Entry payment is pending. Please update the payment status to Paid before adding the participant to the Main List." (an offline order is not marked paid yet), or "Order Not Found" (no order at all).
- Search with **Search**. "No record found" means nobody is unpaid.

## Frequently asked questions about queue, delete and forfeit

**How do I delete a player?** ⋮ → **Delete**, or tick players and click **Delete**.

**What happens when I remove a player from a category?** Removing a player is **Delete** (or **Delete & Refund**) on the **Players** page. Only that participant leaves the category's player list, after a confirmation (league row icons: at once); the category and its other players are not affected. The participant moves to the **Deleted** list: **Delete** keeps the registration fee, **Delete & Refund** refunds it. You can restore them later with **Deleted** → ⋮ → **Add to List**. A participant already in a stage of the draw cannot be deleted ("Participant In Stage Cannot Delete"); **Forfeit** them instead, which scores their pending matches as wins for the opponents. To take a player out of the list without deleting them, use **Add to Queue**.

**What is the difference between Delete and Delete & Refund?** **Delete & Refund** also refunds the fee; **Delete** does not.

**Is there a confirmation before deleting?** Yes in tournaments: a confirmation shows what will happen and the names; click **Delete** or **Delete & refund** to confirm. The delete icons of league events delete at once.

## Frequently asked questions about deleting and refunding later

**Can I refund a player I deleted without refund?** Yes. Open **Deleted** → **Edit**, switch the entry to **Delete With Refund**, **Save Changes** → **Confirm refund**. A refunded entry cannot go back to **Deleted**.

**Why can I not delete a player?** They are already in a stage of the draw ("Participant In Stage Cannot Delete"). Forfeit them instead.

## Frequently asked questions about the queue and the Deleted list

**How do I move a player to the queue?** Tick them and click **Add to Queue**.

**How do I bring a queued player back?** **Queue** → tick → **Add to List**.

**How do I restore a deleted player?** **Deleted** → ⋮ on the player's row → **Add to List**.

**What does "Delete With Refund" in the Deleted list mean?** The entry was deleted with **Delete & Refund**; the amount shows what was refunded.

**How do I forfeit a player?** ⋮ → **Forfeit** → confirm. Their upcoming matches are scored as wins for the opponents.

**What happens to matches when I forfeit a player?** Their pending matches that already have an opponent are scored as walkovers – the opponent wins. In knockout draws later matches are scored the same way once the opponent is known. The player stays in the draw. **Undo Forfeit** restores the previous match data.

**How do I add an unpaid player to the list?** **Unpaid Players** → tick → **Add to List**. It only works when the player's order is paid.
