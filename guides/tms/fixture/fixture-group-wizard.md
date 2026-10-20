---
doc_id: tms.fixture.group-wizard
title: Group stage creation wizard – sections, participants and qualifiers
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - group creation wizard
  - group creation configuration
  - stage 2 configuration
  - stage 3 configuration
  - stage winners
  - separation criteria
  - primary group size
  - secondary group size
  - custom group distribution
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I create groups for a group stage?
  - What are Primary Group Size and Secondary Group Size?
  - How do I choose who qualifies from the group stage?
  - How do I add a second stage?
  - What does Separation Criteria do?
  - What does "Do you want to create a fixture with Elite/Excluded players" mean?
  - How do I create custom groups?
backend_sources:
  - gateway/src/routers/fixture_router.py (draft_group_fixture, generate_fixtures; feature FIXTURE_ACCESS, Edit)
  - gateway/src/routers/stage_router.py (set_stage_configuration, apply_to_all_stages; feature EDIT_STAGE, Edit)
  - tms/src/service/group_service.py (create_group, upsert_group_participants)
  - tms/src/service/fixture_service.py (draft_group_fixture)
source_files:
  - src/app/modules/tms/fixture-configuration/groups-stage-view/creation-wizard/groups-stage-creation-wizard.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/creation-wizard/bodies/group-creation-body/groups-stage-wizard-group-creation-body.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/creation-wizard/bodies/stage2-config-body/groups-stage-wizard-stage2-config-body.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/creation-wizard/bodies/stage3-config-body/groups-stage-wizard-stage3-config-body.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/creation-wizard/bodies/participant-selection-body/groups-stage-wizard-participant-selection-body.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/creation-wizard/bodies/separation-criteria-body/groups-stage-wizard-separation-criteria-body.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/creation-wizard/save-bar/groups-stage-wizard-save-bar.component.html
---
# Group stage creation wizard

The group creation wizard builds a group stage step by step. Each step is a panel that opens in turn, and each panel has a **Save** button (or **Skip**) at its foot. The wizard can be used for the first group stage, and for a second or third stage that takes qualifiers from the stage before.

## The panels, in order

1. **Stage Participants** (first panel) – choose the participants of the stage: **Add Participants** opens the participant list (see the group popups guide), **Participant Selection** and **Select Players** pick them, **Elite Participants** and **Excluded Participants** are kept out of the groups when chosen (see below).
2. **Group Creation Configuration** – the group sizes and the number of groups (see below).
3. **Separation Criteria** – keep participants from the same entity apart (see below).
4. **Playing Format** – "Select the playing order you want to implement". Pick the format from the list.
5. **Stage 2 configuration** and **Stage 3 configuration** – shown when the category has a second or third stage. Their panels are named **Stage 1 Qualifier** / **Stage 2 Qualifier** for the participants who qualify from the previous stage.
6. **Stage Winners** – "You can select the number of winners you want to include in this stage". Choose the winners from each group.

Each panel's **Save** saves that panel only; the page then opens the next one. **Skip** moves on without saving that panel (only where it is offered).

## Group Creation Configuration

- **Primary Group Size** and **Secondary Group Size** – the sizes of the groups. A secondary size must differ by exactly one from the primary size. "Secondary group size … must differ from primary … by exactly 1" otherwise.
- **Total Participants** – the number of players in the stage. For a sample fixture you type it in ("Custom input your total participants").
- **Suggested Group** – the groups the system suggests for the total ("Based on your inputs, following groups were made").
- **Randomize Groups** – "The system will randomly distribute the players according to the logic".
- **Custom Group** – "Create groups based on your preferred group size, or you can create custom groups". Each custom row has **Group Range** or **No. of such groups** and a group strength. The "Remaining" count shows participants not yet placed; **Save** is available when none remain.
- **Logic Selection** – the logic to build the groups: circular, Berger or custom. **View** shows the match order of the logic; **Edit** changes the custom logic (see the group popups guide).

## Elite and excluded participants

- **Use Elite Participants** – "Elite participants are the top-ranked players designated by you". They are kept as a separate group of players, as chosen in the wizard.
- **Use Excluded Participants** – "Excluded participants are those who are not included in any stage".
- When a multi-stage fixture has elite or excluded players, the wizard asks: "Do you want to create a fixture with Elite/Excluded players or Without Elite/Excluded players?" Choose **With Elite/Excluded players** or **Without Elite/Excluded players**.

## Separation Criteria

- Choose at most **2** options: "Select a maximum of 2 options based on your preference of separation".
- The criteria keep participants from the same entity as far apart as possible, so they meet as late as possible.
- A selected criterion opens its details below the option.

## Stage winners and qualifiers

- **Select Winner**, **Specify Winners**: "You can select winners or losers from a group range".
- **No. of Winners** / **No. of Best Finishers**: how many of each group's top players go on.
- **When not selected, all players from the selected position across groups qualify.** Use the restriction only to keep the best performers.
- **Selection Criteria** (points or rank) is the basis for choosing winners in a slot.
- **Based on your selection, the following players will qualify** lists the result before saving.
- **Winners**: the custom selection of winners across groups.

## Save bar and template stages

- **Save** saves the wizard.
- **Apply to all** (when the second stage is a template) copies the same settings to every stage.
- **Delete All Stage** deletes every stage of a template (the confirmation "Delete All Stages?" asks first).

## Messages in the wizard

- "Please correct errors in your selections." – a field is invalid; fix it and save again.
- "Group size … is not available. Please contact admin or create templates for these group sizes." – no template offers these sizes.
- "Not enough remaining participants to increase No Of Such Groups!" – add participants or reduce the number of groups.
- "Please Add Benched Participants Inside Groups" – benched players must be placed before saving.

## Frequently asked questions about the group wizard

**How do I create groups for a group stage?** Work through the panels: choose participants, set Primary and Secondary Group Size, choose the separation criteria and playing format, then Save each panel.

**What are Primary Group Size and Secondary Group Size?** The sizes of the groups. The secondary size must differ from the primary by exactly one.

**How do I choose who qualifies from the group stage?** Use **Stage Winners**: set **No. of Winners** per group. Players qualify from the chosen positions.

**How do I add a second stage?** Save the first stage; the **Stage 2 configuration** panel then opens for the qualifiers.

**What does Separation Criteria do?** It keeps players from the same club or association apart, choosing at most two options.

**What does "Do you want to create a fixture with Elite/Excluded players" mean?** Elite or excluded players exist in this stage. Choose whether the fixture includes them.

**How do I create custom groups?** Choose **Custom Group** and add rows with the group range and the number of groups until **Remaining** shows 0.
