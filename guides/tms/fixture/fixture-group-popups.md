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
  - src/app/modules/tms/fixture-configuration/fixture-popups/players-selected/players-selected.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/previous-stage-players/previous-stage-players.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/excluded-stage2-players/excluded-stage2-players.component.html
---
# Group stage popups

These popups open from the group draft and the group wizard. Each one has a close icon (the round X at the top).

## Participant Selection (add participants to a group)

- Title: **Participant Selection For** (the group name).
- **Search participants** filters the list by name.
- Opened with the **+** icon of an expanded group in the draft. It lists the benched players.
- Columns: **Flag**, **Back No.** (singles), **Participant**, **Member Association** and **Participant Club** (when the category uses them) and **Points**. Tick the players you want; each ticked row shows "Selection order N", the order in which they are placed.
- The count line shows "{count} Selected".
- **Add** places the selected players in the group. It is greyed out until at least one player is ticked.
- Bulk selection can be blocked for some players; a blocked tick cannot be changed.

## Benched participants popup

- Title **Benched participants**. Opened with **Benched participants** in the draft groups card. It shows the players not placed in any group yet; it is view only.
- Columns: **Flag**, **Back No.** (singles), **License ID** (not for teams), **Seeding**, **Participant**, **Member Association**, **Club** and **Points**.
- Search with **Search participants**. To place benched players, use the **+** icon of a group.

## Selected Participant popup

- Title **Selected Participant**, with **Total Participants**. Shows the players chosen for the stage in tabs. Columns: **Seeding** (when display seeding is on), **Club**, **Member Association**, **Points**.
- **Search** filters them; **Cancel Search** clears the search.

## Previous stage players popup

- Choose the stage under **Select Stage**; the **Players** list shows **Participant name** and **Participants Points** ("No records found" when empty).
- Tick the players to add to the current stage, then click **Add to Stage**.

## Stage Winners players popup (stage 2)

- Title **Stage Winners**. Lists the players of the stage (**Seeding** when display seeding is on, **Participant name**, **Club**) with **Search** to filter.
- Tick players, then click **Add to Stage**. In view-only mode the ticks cannot be changed.
- The seed column shows "-" when a player has no seed.

## Elite and excluded players (participant selection dialog)

- Title: **Participant Selection**. Two tabs: **Elite Participant** and **Exclude participant**.
- Each tab lists the players with **Seeding** (when display seeding is on), **Club**, **Member Association** and **Points**, and a **Search** box (**Cancel Search** clears it).
- Tick a player to make them elite (top-ranked, designated by you) or to exclude them from the stage. A disabled tick cannot be changed.
- **Total Participants** shows the count. **Save** keeps the choice; **Close** closes without saving.

## Swap player popup (in a group)

- Opened with the swap icon of a player in the draft groups. Title **Select A Participant To Swap**, with **Swapping With** and the player you started from. **Search participants** filters the list.
- Columns: **Flag**, **Back no.** (singles), **Group**, **Group Position**, **Participant**, **Member Association**, **Club**, **Points**. An empty slot shows **BYE**.
- Choose one player (radio). **Swap** exchanges the two players. It is greyed out until one player is chosen.
- Swap is not offered for team categories, nor once every match of the stage is completed.

## Rename group popup

- Opened with the pencil icon of an expanded group. Title **Rename Round**.
- Asks: "What would you like to rename "Group …" to?" with **New Name** (at most **3** characters).
- **Update** renames the group in the draft; **Close** cancels.

## Preference Preview popup

- Title: **Preference Preview**. Shows how the groups will be built before saving: **Selected Participants**, **Total Participants**, **Group Creation Configuration** (**No. Of Groups**, the group sizes), **Separation Criteria**, **Playing Format**, and the scoring note "Point Based - Highest Point Team" where it applies.
- **No. Of Groups** shows each group size as "N of M". **Playing Format** appears only when a playing format applies.
- Opened with **Preference** in the final groups bar. It is read only. **Close** closes the preview.

## Group stage round-robin logic popups (circular, Berger, custom)

- Opened with **View** or **Edit** under **Logic Selection** in the group wizard. Each shows the match order per group in tabs; each row is a **Match** with two **Participant** places.
- **Circular Logic**: with **Edit** you can change the two participants of each match from the lists. **Reset** rebuilds the default order; **Save** keeps your order. Opened with **View**, it is read only and has **Done**.
- **Berger Logics**: read only; **Done** closes it.
- **Custom Logic**: shows **Group Size** and, when templates exist, **Select Template** ("Select a template"; the standard one is tagged **Default**). **Save** keeps the choice.
- **Close** closes any of them.

## Customize Fixtures popup (seed filters)

- Title: **Customize Fixtures**. "Wish to organize the Participants in Unplaced list? Select rounds other than Unplaced list that you wish to include." and "We would like to know for which round would you like to customize?"
- Tick the rounds (or **Select All**), then click **Next** to continue to the customise screen.

## Group stage popups: messages

- Add players to a group: the server's message is shown; if the group cannot take them, the group size rules apply (see the group wizard guide).
- Swap: "Please select a valid participant to swap." when no valid player is chosen.

## Group stage popups: permissions

- Changing groups, swapping and renaming needs **Edit** on **Fixture Access**. Without it the server answers "Access Denied".

## Frequently asked questions about the group popups

**How do I add a participant to a group?** Open the participant selection, tick the players, then **Add**.

**How do I see the benched participants?** Open **View benched participants**; those are the players not yet placed in a group.

**How do I swap two participants in groups?** Click the swap icon next to a player in the draft groups, choose the second player, then **Swap**.

**How do I rename a group?** Expand the group, click its pencil icon, type a new name of up to 3 characters, then **Update**.

**What does the Preference Preview show?** How the groups will be built, before anything is saved.

**How do I mark a player as elite or excluded?** Open the elite and excluded dialog, choose the tab, and tick the player.

**What is circular, Berger or custom logic?** The order in which the matches of each group are played. Berger is a fixed order; Circular can be edited; Custom uses templates set up by the admin for the group size.

**How do I customize the fixtures?** Open **Customize Fixtures**, tick the rounds to include, and click **Next**.

**How do I assign players to groups?** Open **Participant Selection** for the group, tick the players (**Search participants** filters the list), then click **Add** to place them in the group. Use **Swap** to move a player to another group.
