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

## Benched participants (knockout)

- Lists the **benched** players: those not yet placed in a bracket position.
- Search with **Search participants**.
- Columns: **Seeding**, **Member Association**, **Participant Club** and the player.
- Tick players to place them. **Add** places the ticked players in the bracket. Bulk ticking can be blocked for some players.
- A placement that breaks the bracket rules is refused with a BYE message (see the knockout guide).

## Swapping With (knockout swap)

- Title: **Swapping With**: pick the player to swap with the chosen one.
- **Search participants** filters the list.
- Choose one player (tick). **BYE** marks a placeholder.
- **Swap** exchanges the two players; it is greyed out until one is chosen.
- The popup has two modes (tabs), one for swapping players between matches and one for swapping positions.
- Messages:
  - "Participants swapped successfully." – the swap worked.
  - "Unable to swap participants." – the swap was refused.
  - "Please select a valid participant to swap." – no valid player chosen.
  - "Invalid swap: cannot have a BYE vs BYE match." and "Invalid swap: cannot place a BYE with another BYE in same match pair." – the bracket rules block the swap.
  - "Swap is not available for this participant type." – swap is not offered for this participant type.

## Player list

- Title: the list of the participants of the stage.
- **Search participants** filters the list.
- Table columns: **S.No**, the player, **M.A.** (member association) and the other organisation columns as set in Settings.
- Close with the close button.

## Permissions

- Benching, placing and swapping need **Edit** on **Edit Stage** (for stage changes) or **Fixture Access** (for the draft). Without it the server answers "Access Denied".

## Frequently asked questions about the knockout popups

**How do I add a benched player into the knockout bracket?** Open the benched participants popup, tick the players, then **Add**.

**How do I swap two players in the knockout bracket?** Open the swap popup, choose the other player, then **Swap**.

**What does "Swapping With" show?** The players you can swap the chosen player with.

**Why can I not swap two byes?** A bye cannot meet another bye in one match. See the knockout guide.

**How do I see the list of players of the stage?** Open the player list popup and search with **Search participants**.
