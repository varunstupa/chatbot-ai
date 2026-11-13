---
doc_id: tms.fixture.knockout-popups
title: Knockout popups – benched participants, swap in bracket and player list
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - knockout benched participants
  - knockout bench player
  - knockout swap
  - swap knockout participant
  - swapping with
  - knockout player list
  - view players list
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I add a benched player into the knockout bracket?
  - How do I swap two players in the knockout bracket?
  - What does Swapping With show?
  - How do I see the list of players of the stage?
backend_sources:
  - gateway/src/routers/stage_router.py (bench_stage_participant, unbench_stage_participant, swap_stage_participants; feature EDIT_STAGE, Edit)
  - gateway/src/routers/fixture_router.py (draft_knockout_fixture; feature FIXTURE_ACCESS, Edit)
  - tms/src/service/stage_service.py (swap, bench)
source_files:
  - src/app/modules/tms/fixture-configuration/fixture-popups/knockout-benched/knockout-benched.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/knockout-swap/knockout-swap.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/view-players-list/view-players-list.component.html
---
# Knockout popups

These popups open from the knockout draft and the bracket. Each has a close icon at the top.

## Knockout benched participants popup

- Title **Benched participants**. Opened with **Participant List** (the benched count) in the knockout draft, or with the add icon on an empty bracket place.
- Lists the players not yet placed in a bracket position. Search with **Search participants**.
- Columns: **Flag**, **Seeding**, **Draw Position**, **Participant**, **Member Association**, **Participant Club** and **Points**. A forfeited player is marked.
- Tick players to place them, then click **Add**. In view-only mode the ticks are greyed out and **Add** is not shown.
- While a redraw is pending, ticking several players at once is blocked; use **Redraw** first.
- "No record found" when nobody is benched.
- A placement that breaks the bracket rules is refused with a BYE message (see the knockout guide).

## Knockout swap popup (Swapping With)

- Opened with the swap icon on a row of the knockout draft. Title **Select A Participant To Swap**, with **Swapping With** and the chosen player.
- **Search participants** filters the list.
- Choose one player (radio). **BYE** marks an empty place.
- **Swap** exchanges the two players; it is greyed out until one is chosen.
- From the **Matches** tab the swap exchanges players between matches; from the **Participant positions** tab it exchanges draw positions.
- Messages:
  - "Participants swapped successfully." – the swap worked.
  - "Unable to swap participants." – the swap was refused.
  - "Please select a valid participant to swap." – no valid player chosen.
  - "Invalid swap: cannot have a BYE vs BYE match." and "Invalid swap: cannot place a BYE with another BYE in same match pair." – the bracket rules block the swap.
  - "Swap is not available for this participant type." – swap is not offered for this participant type.

## Participants List popup

- Opened with **Participants List** in the stage address bar. Title **Participant List** (singles and mixed), **Participants' List** (doubles) or **Team List** (teams). "Loading..." shows while it loads.
- **Search participants** filters the list.
- Columns: **License ID** (not for teams), **Seeding** and **System Seeding** when display seeding is on (otherwise **Seeding**), **Participant name** / **Pair Name** / **Team Name**, **M.A.**, **Club** and **Points**.
- "No record found" when the list is empty. Close with the close icon.

## Knockout popups: permissions

- Benching, placing and swapping need **Edit** on **Edit Stage** (for stage changes) or **Fixture Access** (for the draft). Without it the server answers "Access Denied".

## Frequently asked questions about the knockout popups

**How do I add a benched player into the knockout bracket?** Click **Participant List** (the benched count) in the knockout draft, tick the players, then **Add**.

**How do I swap two players in the knockout bracket?** Click the swap icon on the player's row in the draft, choose the other player, then **Swap**.

**What does "Swapping With" show?** The players you can swap the chosen player with.

**Why can I not swap two byes?** A bye cannot meet another bye in one match. See the knockout guide.

**How do I see the list of players of the stage?** Click **Participants List** in the stage address bar and search with **Search participants**.
