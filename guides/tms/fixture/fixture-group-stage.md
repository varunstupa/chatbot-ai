---
doc_id: tms.fixture.group-stage
title: Group stage – draft groups, final groups and actions
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - group stage
  - draft groups
  - final groups
  - group draft
  - shuffle groups
  - sequence groups
  - redraw groups
  - delete all stages
  - round robin groups
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I shuffle participants into groups?
  - What is the difference between Save draft and Save?
  - How do I redraw the groups?
  - How do I publish the group stage?
  - Why is the Redraw button greyed out?
  - What does "Groups have zero participants" mean?
  - How do I export the groups to Excel?
backend_sources:
  - gateway/src/routers/fixture_router.py (draft_group_fixture, generate_fixtures; feature FIXTURE_ACCESS, Edit)
  - gateway/src/routers/group_router.py (group endpoints)
  - tms/src/service/fixture_service.py (draft_group_fixture, delete_fixtures)
  - tms/src/service/group_service.py (create_group, upsert_group_participants)
source_files:
  - src/app/modules/tms/fixture-configuration/groups-stage-view/address-bar/groups-stage-address-bar.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/draft-groups-card/groups-stage-draft-groups-card.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/draft-bottom-bar/groups-stage-draft-bottom-bar.component.html
  - src/app/modules/tms/fixture-configuration/groups-stage-view/final-bottom-bar/groups-stage-final-bottom-bar.component.html
  - src/app/modules/tms/fixture-configuration/fixture-configuration.component.ts
  - src/app/modules/tms/fixture-configuration/groups-stage-view/groups-stage-view.component.html
---
# Group stage – draft groups, final groups and actions

A **group stage** puts the participants of a category into groups, and each group plays a round robin (every participant plays every other one in the group). This guide covers the group draft (before the matches are made) and the final groups (after). The group creation wizard and the participant popups are in the next guides.

## Group stage address bar

- The bar above the group stage starts with **Fixture Settings**. It adds **Draft edit** while the groups are a draft, and **Final Edit** once the matches are made.
- **Participants List** is shown only before the draft groups exist (while the creation wizard is open). It opens the participants popup.
- **Schedule Matches** is shown only for league events, after the matches are made and once at least one match is ticked. Its tip reads "Schedule any new matches. This change will reflect in scheduler & Planner". When the event has venue registration on, it is greyed out with the tip "Venue Registration is enabled."
- After the matches are made the bar also shows the scoring settings button (see "Fixture game settings").

## Group stage draft groups card: header

- Shown while the draft exists and the matches are not made yet. Title **Created Groups**.
- **Search Participants & Groups** filters the list by name as you type.
- **Benched participants** (shown when someone is benched) opens the benched list.
- **Export Excel** downloads the groups as a spreadsheet.
- **Preview** opens a preview of the group matches before they are made.
- **Add Group** (shown only when someone is benched) adds an empty group named "Group N" at the end.
- When there are no groups, **No record found** is shown.

## Group stage draft groups card: groups and columns

- Each group is a panel showing its number of **Participants**. Expand it to see the table and the group icons: rename the group, remove the group, and **+** to add benched participants (the **+** shows only when someone is benched).
- Removing a group that has participants benches them first ("Player benched successfully"); an empty group is just removed.
- Columns: **Flag**, **Back No.** (singles only), **License Id** (not for teams), **Seeding**, **Participant**, **Member Association** and **Club** (only when the category's parent role uses them), **Points** and **Action button**.
- Doubles and mixed doubles show both players of a pair. A forfeited player shows the forfeit mark and "(Forfeited)".
- In **Action button**, the remove icon benches the participant; the swap icon opens the swap popup. Swap is hidden for team categories and once every match of the stage is completed.

## Group stage draft bottom bar: Preference, Shuffle, Sequence, Save draft

Shown while the groups are a draft:
- **Preference** – asks **Delete Fixture?** "Are you sure you want to delete this fixture? All the changes made will be lost." with **Yes, Delete** and **Close**. Confirming deletes the draft so the group creation wizard opens again and you can change the preferences.
- **Shuffle** – builds the groups again from the saved stage settings. It needs every stage configuration saved ("Please save all stage configurations before generating fixtures.").
- **Sequence** – shown only when at least one group has participants. It moves every participant out of the groups to the benched list ("Successfully benched participants"), so you can place them yourself. With empty groups: "No Participants In Groups".
- **Save draft** – saves the groups as a draft; the matches are not made yet.
- For a sample fixture only **Preference** and **Save draft** are shown. The arrow at the end of the bar collapses it.

## Group stage draft bottom bar: Save and Re-draw

- With suggested groups, the main button reads **Save** when nobody is benched, and **Re-draw** when the benched list has changed and the groups must be built again. **Re-draw** is greyed out while no participant is placed in any group.
- With custom groups, only **Save** is shown, and only when nobody is benched.
- **Save** makes the groups and their matches (the stage moves to **Final Edit**).
- If the previous stage is not fully scored, the **Alert!** popup shows "Final Fixture cannot be created for this stage as all matches of the previous stage are not scored." with **Proceed**.

## Group stage final bottom bar (after the matches are made)

- **Edit** – asks **Edit Final Fixture?** "Going back to the edit stage will remove/reset your current final fixture. Are you sure you want to proceed?" with **Confirm**. Confirming returns the stage to **Draft edit**. When the stage is in progress or completed: "you need to reset score to edit this stage".
- **Preference** – opens the preferences preview (read only).
- **Delete** – asks **Delete Fixture?** and deletes the matches and groups of this stage. Hidden for sample fixtures and template stages.
- **Delete All Stage** (template stages only) – asks **Delete All Stages?** "Are you sure you want to delete all stages?" and deletes every stage of the category.
- **Publish** – toggle that publishes this stage. Turning it on shows **Publishing Successful**.
- **Replace With Participants** (single stage) or **Complete Fixture** (several stages) – shown only for a sample fixture once the previous stages are concluded. See "Replace participant".

## Group messages

Shown while you build the groups:
- "Group size {size} is not available. Please contact admin or create templates for these group sizes." – a group size is not offered by the templates of the organisation.
- "Groups {from}–{to}" – the custom selection of group numbers.
- "{group names} have zero participants." – each group must have at least one participant before saving.
- "Not enough remaining participants to increase No Of Such Groups!" – there are not enough players left to add another group of that size.
- "No Participants In Groups" – nothing to save.
- "Please Add Benched Participants Inside Groups" – benched participants must be placed in a group first.
- "No Format created or publish" – the playing format is not yet set up or published.
- "Please correct errors in your selections." and the group size messages from the stages guide (group size must differ by exactly one, and the zero-value group rule).

## Server messages for group actions

- Draft or redraw saved: "Groups Updated Successfully"; with matches created: "Matches Updated Successfully".
- Stage not editable (for example already published): "Stage Update Not Allowed".
- Create a group: "Group Created". Missing group name: "Group Name Required".
- Update a group participant: "Participant Updated". Unknown group: "Group Not Found".
- Delete fixtures: "Fixture Deleted".

## Permissions

- Drafting, redrawing, deleting and publishing the groups needs **Edit** on **Fixture Access**. Without it the server answers "Access Denied".

## Frequently asked questions about the group stage

**How do I shuffle participants into groups?** Click **Shuffle** in the draft bar. To empty the groups and place everyone yourself, click **Sequence**: all participants move to the benched list.

**Why does Preference in the draft bar ask to delete the fixture?** In the draft, **Preference** takes you back to the creation wizard; the draft groups are deleted so they can be built again with new preferences.

**Why can I not edit the final groups?** Scores have been entered ("you need to reset score to edit this stage"). Reset the scores first.

**What is the difference between Save draft and Save?** **Save draft** keeps the groups for later. **Save** makes the groups and their matches.

**How do I redraw the groups?** Click **Re-draw**. It appears when the benched list has changed, and is greyed out while no participant is placed in a group.

## Frequently asked questions about the group stage (more)

**How do I publish the group stage?** Use the **Publish** toggle in the final groups bar.

**What does "have zero participants" mean?** A group is empty; every group needs at least one participant before the groups can be saved.

**How do I delete the group stage?** Click **Delete** in the final bar to delete the fixtures of this stage. For a template draw, **Delete All Stage** deletes every stage of the category. To remove the stage itself, use the delete icon on its stage card.

**How do I export the groups to Excel?** Click **Export Excel** on the draft groups card.

**Why is the Re-draw button greyed out?** No participant is placed in any group. Place participants first. Redrawing also needs **Edit** on **Fixture Access**.
