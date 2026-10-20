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
---
# Group stage – draft groups, final groups and actions

A **group stage** puts the participants of a category into groups, and each group plays a round robin (every participant plays every other one in the group). This guide covers the group draft (before the matches are made) and the final groups (after). The group creation wizard and the participant popups are in the next guides.

## Stage address bar

The page header of a group stage shows the links **Fixture Settings**, **Draft edit**, **Final Edit**, **Participants List** and **Schedule Matches**. **Match Access** opens the match access panel (documented with the scheduling guide).

## Draft groups card

- Shown while the fixture is not yet created. Once the matches are created the card is replaced by the final groups.
- **Search Participants & Groups** filters the list by name as you type.
- **Export Excel** downloads the groups as a spreadsheet.
- The groups are listed one under the other. Expand a group to see its participants.
- Columns: **Seed** (when display seeding is on), **Participant**, **Member Association** and **Club** (as set in the category's Settings), and the forfeit mark for forfeited players.
- Doubles and mixed doubles show both players of a pair; a single player shows its licence.

## Draft bottom bar (before the matches are made)

- **Preference** – opens the group preferences (the preview of how groups will be built). See the popups guide.
- **Shuffle** – places the participants again at random into the groups.
- **Sequence** – places the participants in seed order into the groups.
- **Save draft** – saves the groups as a draft; the fixture is not created yet.
- **Redraw** (shown when groups already exist) – builds the groups again. It is greyed out while the groups are not valid.
- **Save** (shown when no groups exist yet) – creates the groups and the fixture.

## Final groups (after the matches are made)

- **Edit** – opens the editing of the final stage.
- **Preference** – opens the preferences preview.
- **Delete** – deletes the fixtures of this stage (matches and groups) after confirming.
- **Delete All Stages?** – deletes every stage of the category; the confirmation asks first.
- **Publish** – a toggle that publishes the fixture of this stage.
- **Replace participants** – opens the replace action of the first stage (see the replace guide).

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

**How do I shuffle participants into groups?** Click **Shuffle** in the draft bar. Use **Sequence** to place them in seed order instead.

**What is the difference between Save draft and Save?** **Save draft** keeps the groups for later. **Save** creates the groups and the fixture.

**How do I redraw the groups?** Click **Redraw**. It is greyed out while the groups are not valid, for example when a group has zero participants.

**How do I publish the group stage?** Use the **Publish** toggle in the final groups bar.

**What does "have zero participants" mean?** A group is empty; every group needs at least one participant before the groups can be saved.

**How do I delete the group stage?** Click **Delete** to delete the fixtures of this stage, or **Delete All Stages?** to delete every stage of the category.

**How do I export the groups to Excel?** Click **Export Excel** on the draft groups card.
