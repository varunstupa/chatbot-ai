---
doc_id: tms.fixture.group-popups
title: Group stage popups – add, bench, swap, exclude, preview and round-robin logic
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - participant selection for group
  - add participants to group
  - view benched participants
  - bench participant
  - swap participant in group
  - rename group
  - preference preview
  - elite participant selection
  - exclude participant
  - seed filters
  - customize fixtures
  - circular logic
  - berger logic
  - custom logic
  - previous stage players
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I add a participant to a group?
  - How do I see the benched participants?
  - How do I swap two participants in groups?
  - How do I rename a group?
  - What does the Preference Preview show?
  - How do I mark a player as elite or excluded?
  - What is circular, Berger or custom logic?
  - How do I customize the fixtures?
backend_sources:
  - gateway/src/routers/group_router.py (upsert_group_participants, get_group_participants, get_dummy_group_matches)
  - gateway/src/routers/stage_router.py (bench_stage_participant, unbench_stage_participant, swap_stage_participants)
  - gateway/src/routers/fixture_router.py (draft_group_fixture; feature FIXTURE_ACCESS, Edit)
  - gateway/src/routers/registration_router.py (manage_elite_excluded_players)
source_files:
  - src/app/modules/tms/fixture-configuration/fixture-popups/add-group-participants/add-group-participants.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/view-benched-participants/view-benched-participants.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/swap-player/swap-player.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/rename-group/rename-group.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/customise-seed-filters/customise-seed-filters.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/circular-logic/circular-logic.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/berger-logic/berger-logic.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/custom-logic/custom-logic.component.html
  - src/app/modules/tms/fixture-configuration/preference-preview-dialog/preference-preview-dialog.component.html
  - src/app/modules/tms/fixture-configuration/elite-exclude-participants-dialog/elite-exclude-participants-dialog.component.html
---
# Group stage popups

These popups open from the group draft and the group wizard. Each one has a close icon (the round X at the top).

## Participant Selection (add participants to a group)

- Title: **Participant Selection For** (the group name).
- **Search participants** filters the list by name.
- The list shows **Member Association** and the player's details. Tick the players you want.
- The count line shows "{count} Selected".
- **Add** places the selected players in the group. It is greyed out until at least one player is ticked.
- Bulk selection can be blocked for some players; a blocked tick cannot be changed.

## View benched participants

- Shows the **benched** players: those not placed in any group yet.
- Columns include **Seeding** and **Member Association**.
- Search with **Search participants**. Benched players are placed through the participant selection popup.

## Players selected

- Shows the players chosen for the stage in tabs (one tab per group or list). **Search** filters them; **Cancel Search** clears the search.

## Previous stage players

- Lists the players who qualify from the previous stage. Tick the players to add to the current stage, then confirm with the button at the foot of the dialog.

## Excluded players for stage 2

- Lists the players of the stage with **Search** to filter.
- Tick players to exclude them from the next stage, then confirm with the button at the foot of the dialog. A view-only mode blocks changes.
- The seed column shows "-" when a player has no seed.

## Elite and excluded players (participant selection dialog)

- Title: **Participant Selection**. Two tabs: **Elite Participant** and **Exclude participant**.
- Each tab lists the players with **Seeding**, **Club**, **Member Association** and **Points**, and a **Search** box.
- Tick a player to make them elite (top-ranked, designated by you) or to exclude them from the stage. A disabled tick cannot be changed.
- **Total Participants** shows the count.

## Swap player (in a group)

- Title: swap a participant with another one. **Search participants** filters the list.
- Choose one player (radio); the columns show **Member Association** and the **BYE** placeholder.
- **Swap** exchanges the two players. It is greyed out until one player is chosen.

## Rename group

- Asks: "What would you like to rename "Group …" to?" with **New Name** (at most **3** characters).
- **Save** renames the group in the draft; the close icon cancels.

## Preference Preview

- Title: **Preference Preview**. Shows how the groups will be built before saving: **Selected Participants**, **Total Participants**, **Group Creation Configuration** (**No. Of Groups**, the group sizes), **Separation Criteria**, **Playing Format**, and the scoring note "Point Based - Highest Point Team" where it applies.
- **Close** closes the preview.

## Round-robin logic popups (circular, Berger, custom)

- **Circular logic**, **Berger logic** and **Custom Logic** show the match order of each group in tabs, one tab per group. Each tab lists the matches in order.
- **Circular logic**: a button saves the order of the matches (**Set Matches Order**), and another regenerates the list.
- **Berger logic**: the tabs show the match order of each group.
- **Custom Logic**: choose a template with **Select a template** (**Default** is the standard one). Each match row is labelled "Match {number}" with its two participants; **Save** keeps the custom order.

## Customize Fixtures (seed filters)

- Title: **Customize Fixtures**. Tick the seeds (or **Select all** with the header tick) to include in the fixture.
- **Save** (set customise) applies the selection.

## Messages

- Add players to a group: the server's message is shown; if the group cannot take them, the group size rules apply (see the group wizard guide).
- Swap: "Please select a valid participant to swap." when no valid player is chosen.

## Permissions

- Changing groups, swapping and renaming needs **Edit** on **Fixture Access**. Without it the server answers "Access Denied".

## Frequently asked questions about the group popups

**How do I add a participant to a group?** Open the participant selection, tick the players, then **Add**.

**How do I see the benched participants?** Open **View benched participants**; those are the players not yet placed in a group.

**How do I swap two participants in groups?** Open **Swap**, choose the second player, then **Swap**.

**How do I rename a group?** Use the rename action, type a new name of up to 3 characters, then **Save**.

**What does the Preference Preview show?** How the groups will be built, before anything is saved.

**How do I mark a player as elite or excluded?** Open the elite and excluded dialog, choose the tab, and tick the player.

**What is circular, Berger or custom logic?** The order in which the matches of each group are played. Circular and Berger are fixed orders; custom lets you choose a template.

**How do I customize the fixtures?** Open **Customize Fixtures**, tick the seeds to include, and save.
