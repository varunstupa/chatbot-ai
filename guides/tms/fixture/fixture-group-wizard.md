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
  - src/app/modules/tms/fixture-configuration/groups-stage-view/creation-wizard/bodies/stage-winners-body/groups-stage-wizard-stage-winners-body.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/creation-wizard/bodies/playing-format-body/groups-stage-wizard-playing-format-body.component.html
---
# Group stage creation wizard

The group creation wizard builds a group stage step by step. Each step is a panel that opens in turn, and each panel has a **Save** button (or **Skip**) at its foot. The wizard can be used for the first group stage, and for a second or third stage that takes qualifiers from the stage before.

## Group stage creation wizard: the panels, in order

The wizard is shown while the stage has no draft groups yet.

1. **Stage Winners** – only for a second or later stage. "You can select the number of winners you want to include in this stage". Has **Skip** and **Save**.
2. **Participant Selection** – "Select the participants you want to bifurcate". **Add Participants** (or **Edit participants**) opens the participant list; **Use Elite Participants** and **Use Excluded Participants** (see below). When collapsed it shows the counts of **Elite Participants**, **Stage Participants** and **Excluded Participants**.
3. **Group Creation Configuration** – group sizes and distribution (see below). Greyed out until the stage has participants (a sample fixture can open it at once).
4. **Stage 2 configuration** and **Stage 3 configuration** – only when that stage of the category was created from a template. They set how the qualifiers of the stage before go on.
5. **Separation Criteria** – keep participants from the same entity apart. Greyed out until the stage has participants. Has **Skip** and **Save**.
6. **Playing Format** – team categories only. "Select the playing order you want to implement".

Each panel's **Save** saves that panel only; the next panel then opens. **Skip** moves on without saving. When the second stage is a template, **Separation Criteria** and **Playing Format** also show **Apply to all**, which copies the setting to every stage.

## Group Creation Configuration: Suggested Group

- **Total Participants** – for a sample fixture you type it ("Custom input your total participants"); otherwise **No. of participants** is filled from the stage and cannot be changed.
- **Primary Group Size*** (required) and **Secondary Group Size** – set with the – and + buttons or by typing. The secondary size must differ from the primary by exactly one: "Secondary group size … must differ from primary … by exactly 1".
- "Based on your inputs, following groups were made" lists the groups ("Group with" N participants).
- **Number of seeds** and **No. of qualifiers** – set with – and +.
- **Distribution Criteria**: **Randomize Groups** ("The system will randomly distribute the players according to the logic") OR **Customize** ("Block values will be added, for e.g. 2,3"). The custom values box is greyed out while **Randomize Groups** is ticked.

## Group Creation Configuration: Custom Group and Logic Selection

- **Custom Group** tab: "custom group distribution logic". **Add field** adds a row with **No. of participants** (group strength) and **No. of such groups**; the bin icon removes a row. **Remaining** shows participants not yet placed. **Save** appears only when **Remaining** is 0. The tab also has **Number of seeds**, **No. of qualifiers** and **Distribution Criteria**.
- **Logic Selection** – the order of matches in a group:
  - **Berger Logic** – "Berger system is a participant placement system in groups often used to break ties in Events." **View** only.
  - **Circular Logic** – "In this method, participants are represented in a cycle. 1 is fixed at one position and others are rotated in a clockwise direction. You can edit as well this process." **View** and **Edit**.
  - **Custom Logic** – "These are custom logic provided by admin according to the group size and format (Circular or Berger)." **View** only.
- **View** and **Edit** appear on the selected logic only (see the group popups guide).
- When the stage has elite players (single stage), "Would you like to include elite participants in this stage?" offers **Use Elite Participants**.

## Group stage creation wizard: elite and excluded participants

- **Use Elite Participants** – "Elite participants are the top-ranked players designated by you". They are kept as a separate group of players, as chosen in the wizard.
- **Use Excluded Participants** – "Excluded participants are those who are not included in any stage".
- When a multi-stage fixture has elite or excluded players, the wizard asks: "Do you want to create a fixture with Elite/Excluded players or Without Elite/Excluded players?" Choose **With Elite/Excluded players** or **Without Elite/Excluded players**.

## Group stage creation wizard: Separation Criteria

- Choose at most **2** options: "Select a maximum of 2 options based on your preference of separation".
- "The separation criteria ensures that participants from the same entity or organization are placed as far apart as possible in the tournament bracket, minimizing the chance of early round encounters between them."
- Collapsed, the panel reads "Distribute your participants, pairs, teams according to the entity separation preferences".
- A selected criterion opens its details below the option.

## Group stage creation wizard: Stage Winners and qualifiers

- The panel lists each earlier stage (**Stage 1**, **Stage 2** …).
- From a group stage: **No. of Winners** – "Specify Winners" – takes the top N of every group; or **Custom Selection** – "You can select winners or losers from a group range." – with **Group Range** rows and the **WINNERS** positions to take. **Add field** adds a range.
- From a knockout stage: choose rounds under **WINNERS** and **LOSERS**.
- **No. of Best Finishers** – "When not selected, all players from the selected position across groups qualify. Use only if you want to restrict the qualifying players to the best performers."
- **Selection Criteria** – the ordered criteria used to pick the best finishers; click criteria in the order you want them applied.
- In **Stage 2 configuration**: **Select Winner** – "You can specify the number of winners from each group to be included." – and, for a knockout next stage, **Round of**, **With Bye** / **Without Bye** and **Position Matches**.

## Group stage creation wizard: save bar

- **Save** at the foot creates the draft groups. It is greyed out while saving and until every stage configuration is saved.
- It turns blue only when the stage has participants, the group sizes are valid and, for team categories, a playing format is saved.
- For a sample fixture, **Save** generates the sample groups directly.
- **Delete All Stage** (when the second stage is a template) asks **Delete All Stages?** "Are you sure you want to delete all stages?" and deletes every stage of the category.

## Group stage creation wizard: messages

- "Please correct errors in your selections." – a field is invalid; fix it and save again.
- "Group size … is not available. Please contact admin or create templates for these group sizes." – no template offers these sizes.
- "Not enough remaining participants to increase No Of Such Groups!" – add participants or reduce the number of groups.
- "Please Add Benched Participants Inside Groups" – benched players must be placed before saving.

## Frequently asked questions about the group wizard

**How do I create groups for a group stage?** Work through the panels: choose participants, set Primary and Secondary Group Size, choose the separation criteria and playing format, then Save each panel.

**What are Primary Group Size and Secondary Group Size?** The sizes of the groups. The secondary size must differ from the primary by exactly one.

**How do I choose who qualifies from the group stage?** In the next stage, open **Stage Winners** and set **No. of Winners** per group, or use **Custom Selection** with group ranges.

**Why is Group Creation Configuration greyed out?** The stage has no participants yet. Add them in **Participant Selection** and save.

**Why do I not see Playing Format?** It is shown only for team categories.

**How do I add a second stage?** Click **+** after the stage cards. In the new stage, **Stage Winners** sets who qualifies from the stage before.

**What does Separation Criteria do?** It keeps players from the same club or association apart, choosing at most two options.

**What does "Do you want to create a fixture with Elite/Excluded players" mean?** Elite or excluded players exist in this stage. Choose whether the fixture includes them.

**How do I create custom groups?** Choose **Custom Group** and add rows with the group range and the number of groups until **Remaining** shows 0.
