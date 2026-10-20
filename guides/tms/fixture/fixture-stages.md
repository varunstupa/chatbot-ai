---
doc_id: tms.fixture.stages
title: Fixture stages – create, edit, delete and publish
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - fixture stage
  - stage name
  - create stage
  - edit stage
  - delete stage
  - next stage
  - generate fixtures
  - publishing successful
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I create a new stage?
  - How do I rename a stage?
  - How do I delete a fixture stage?
  - Why do I see "Please save all stage configurations before generating fixtures"?
  - Why can I not change Round Robin to Double Round Robin?
  - What does Publishing Successful mean?
backend_sources:
  - gateway/src/routers/stage_router.py (stage endpoints)
  - gateway/src/routers/fixture_router.py (generate_fixtures)
  - tms/src/router (stage and fixture routers)
source_files:
  - src/app/modules/tms/fixture-configuration/fixture-configuration.component.ts
  - src/app/modules/tms/fixture-configuration/fixture-popups/edit-stage/edit-stage.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/select-next-stage/select-next-stage.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/fixture-success/fixture-success.component.html
---
# Fixture stages – create, edit, delete and publish

A fixture **stage** is one step of a category's draw: a group stage, or a knockout stage. A category can have several stages in order (for example group stage, then knockout). This guide covers the stage actions on the **Fixtures and Results** page. The page itself is in "Fixtures and Results page – overview".

## Stage names and types

- A new stage is named **Knockout Stage** when you pick the knockout card, and **Group Stage** otherwise.
- The stage name is typed in the **Stage Name** box. It can be at most 12 characters.
- For a group stage the format is **Round Robin** or **Double Round Robin**. In the edit popup, once one of them is chosen, the other is greyed out.

## Create a stage (Next stage popup)

- The **Create Stage** button of the popup creates the stage for the category.
- The popup shows a create button for stage 1 or stage 2; the second stage is created from the same popup after the first.
- A multi-stage option is also supported by the popup; the stage list shows the result.

## Edit a stage name (Edit stage popup)

1. Click the edit icon on the stage.
2. Change **Stage Name**. The popup title shows the name you are editing.
3. Click save (**update_stage_info**). Then the stage list reloads.
4. If the name is empty: "Please enter a Stage Name" is shown and nothing is saved.
5. The popup is closed with the close button; nothing is saved then.

## Delete a stage

- The delete icon on a stage opens the confirmation **Delete stage?**.
- The text reads: "Are you sure you want to delete this fixture stage? All the changes made will be lost".
- Buttons: **Yes, Delete** (deletes the stage) and **Cancel** (keeps it).
- For a knockout stage the delete icon is hidden when the second stage is a template (see the templates guide).

## Save before generating fixtures

- **Generate** creates the fixtures of all stages. It needs every stage configuration saved first.
- If one is not saved: "Please save all stage configurations before generating fixtures."
- If generation fails, the message from the server is shown. When the server gives none: "Fixture generation failed".
- A stage that is not allowed to generate (server code 403) shows the server's own message.

## Stage 2 and group size rules

Shown when you enter sizes for a stage:
- "Secondary group size (X) must differ from primary (Y) by exactly 1" – a secondary group must be one player bigger or smaller than the primary group.
- "Cannot add a new group while there is an existing group with 0 value!" – fill the group that has 0 before adding another one.
- "Error: 'end' value is required and must be selected." – choose the end value of the range.
- "Please correct errors in your selections." – the selections contain an error; fix the marked fields and save again.

## Publishing successful

After a fixture preview is published, the **Publishing Successful** popup says: "This Preview was published successfully. Where would you like to re-direct now?"
- **Go to Scheduler** opens the scheduler page.
- **Stay here** closes the popup and keeps you on the fixtures page.

## Select next stage popup

- The popup title is **Select Your Next Stage**.
- For a group stage choose **Select Group** and the format (Round Robin or Double Round Robin), then **Create Stage**.

## View stage pictures

- **View group stage** and **View knockout stage** open a picture of how that stage looks (an example image, with the title "Group Stage" or "Knockout Stage"). Close them with the close icon; nothing is saved.

## Stage messages from the server

- Create stage: "Stage Created". Missing name: "Stage Name Required". Category not found: "Event Category Not Found". Stage creation for a non sub category when one is needed: "Create Stages Only For Sub Categories".
- Update stage: "Stage Updated". Unknown stage: "Stage Not Found". Not allowed in the current state: "Stage Update Not Allowed". Published points block edits: the OTT message (no English text yet; see the overview guide).
- Position match not allowed: "Position Match Not Allowed".
- Generate fixtures: "Group Created" for a group; "Configuration Missing" when a stage has no configuration; "Expected Participants Count Missing" when the participant count is not set; "Cannot Generate Fixture Pair Not Compete" when the pairs cannot compete.
- Delete fixtures: "Fixture Deleted"; blocked while the stage is not allowed to change: "Stage Update Not Allowed".
- Apply to all stages: "Updates applied to all stages successfully"; unknown or disallowed fields: "Unknown or disallowed keys for apply to all" (no English text yet).

## Permissions for stages

- Creating, editing and applying stage settings needs **Edit** on **Edit Stage**.
- Generating and deleting fixtures needs **Edit** on **Fixture Access**.

## Frequently asked questions about fixture stages

**How do I create a new stage?** Open the next-stage popup and click **Create Stage**.

**How do I rename a stage?** Click the edit icon, change **Stage Name** (up to 12 characters) and save.

**How do I delete a fixture stage?** Click the delete icon, then **Yes, Delete**. All changes made in the stage are lost.

**Why do I see "Please save all stage configurations before generating fixtures"?** A stage was changed but not saved. Save each stage, then generate again.

**Why can I not change Round Robin to Double Round Robin?** Once one of the two is chosen, the other is greyed out for that stage.

**What does "Secondary group size must differ from primary by exactly 1" mean?** The two group sizes in a stage must be one apart. Change one of the sizes.

**What does Publishing Successful mean?** The preview was published. Choose **Go to Scheduler** to schedule the matches, or **Stay here**.
