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
  - src/app/modules/tms/fixture-configuration/fixture-configuration.component.html
  - src/app/shared/confirm-popup/confirm-popup.constants.ts
  - src/app/modules/tms/fixture-configuration/fixture-popups/view-group-stage/view-group-stage.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/edit-stage/edit-stage.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/select-next-stage/select-next-stage.component.html
  - src/app/modules/tms/fixture-configuration/fixture-popups/fixture-success/fixture-success.component.html
---
# Fixture stages – create, edit, delete and publish

A fixture **stage** is one step of a category's draw: a group stage, or a knockout stage. A category can have several stages in order (for example group stage, then knockout). This guide covers the stage actions on the **Fixtures and Results** page. The page itself is in "Fixtures and Results page – overview".

## Stage bar: the stage cards

- When a category has no stage yet, the page shows the templates screen instead (see "Fixture templates"). Once a stage exists, the stages are shown as cards in a row, joined by arrows.
- Each card shows the stage name, **Stage 1**, **Stage 2** … in order, an edit icon, a delete icon and, once set, the number of **Participants** expected in the stage.
- Click a card to open that stage. The open stage is highlighted.
- The **+** button after the last card opens **Select Your Next Stage** to add another stage.
- When the second stage was created from a template, the **+** button and the delete icons are hidden.
- While the first stage of a template is still a draft, the other stage cards are greyed out and cannot be opened.

## Stage names and types

- A new stage is named **Knockout Stage** when you pick the knockout card, and **Group Stage** otherwise.
- The stage name is typed in the **Stage Name** box. It can be at most 12 characters.
- For a group stage the format is **Round Robin** or **Double Round Robin**. In the edit popup, once one of them is chosen, the other is greyed out.

## Create a stage (Select Your Next Stage popup)

1. Click **+** after the stage cards. The popup **Select Your Next Stage** opens.
2. Click the **Knockout Stage** card ("Knockout is a single elimination round where the losing participant is immediately eliminated from the competition and only the winner advances.") or the **Group Stage** card ("A competition format where each participant plays every other participant once in a round, regardless of win or loss.").
3. For a group stage choose **Round Robin** or **Double Round Robin** under **Select Group** (Round Robin is the default).
4. Click **Create Stage** on the chosen card. The button appears only on the selected card.

The new stage is named **Knockout Stage** or **Group Stage**; rename it afterwards with the edit icon. The server confirms with its message (for example "Stage Created"), or shows its error. Close the popup with the close icon to create nothing.

## Edit a stage name (Edit stage popup)

1. Click the edit icon on the stage card. The popup **Edit stage** opens and shows whether it is a **Group Stage** or a **Knockout Stage**.
2. Change the name in the **Stage Name** box (at most 12 characters).
3. For a group stage the **Select Group** choice is shown; the format that is not in use is greyed out, so the format cannot be switched here.
4. Click **Update**. The stage list reloads with the new name.
5. If the name is empty: "Please enter a Stage Name" is shown and nothing is saved.
6. Close the popup with the close icon to keep the old name.

## Delete a stage

- The delete icon on a stage opens the confirmation **Delete stage?**.
- The text reads: "Are you sure you want to delete this fixture stage? All the changes made will be lost".
- The name of the stage you are deleting is highlighted in the popup.
- Buttons: **Yes, Delete** (deletes the stage) and **Cancel** (keeps it).
- After deleting, the page opens the previous stage (or the next one when you delete the first stage), and the **Ready for Print** count is refreshed.
- The delete icon is hidden on every stage when the second stage was created from a template (see the templates guide).

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

## Stage pictures in Select Your Next Stage

- In **Select Your Next Stage**, the eye icon on each card opens a picture of how that stage looks (an example image, with the title "Group Stage" or "Knockout Stage"). Close them with the close icon; nothing is saved.

## Stage messages from the server

- Create stage: "Stage Created". Missing name: "Stage Name Required". Category not found: "Event Category Not Found". Stage creation for a non sub category when one is needed: "Create Stages Only For Sub Categories".
- Update stage: "Stage Updated". Unknown stage: "Stage Not Found". Not allowed in the current state: "Stage Update Not Allowed" (publishing is always allowed; a delete is blocked when a dependent stage is in progress or completed; other changes when this stage or a dependent stage is). Published points block edits: "This action is not permitted. Points for this event have been published to OTT. ..." (deleting: "Deletion is not permitted. ...").
- Position match not allowed: "Position Match Not Allowed".
- Generate fixtures: "Group Created" for a group; "Configuration Missing" when a stage has no configuration; "Expected Participants Count Missing" when the participant count is not set; "Cannot Generate Fixture, Pair Not Complete" when a doubles or mixed pair has fewer than two players.
- Delete fixtures: "Fixture Deleted"; blocked when this stage or a stage that depends on it is in progress or completed: "Stage Update Not Allowed".
- A State, District or Association separation: "State, District and Association separation are no longer supported. Choose a parent level instead."
- Apply to all stages: "Updates applied to all stages successfully"; unknown or disallowed fields: "Unknown or disallowed keys for apply-to-all: …".

## Permissions for stages

- Creating, editing and applying stage settings needs **Edit** on **Edit Stage**.
- Generating and deleting fixtures needs **Edit** on **Fixture Access**.

## Frequently asked questions about fixture stages

**How do I create a new stage?** Click **+** after the stage cards, pick **Knockout Stage** or **Group Stage**, and click **Create Stage**.

**Why is there no + button or delete icon on the stages?** The second stage was created from a template. Template stages cannot be added to or deleted one by one.

**How do I rename a stage?** Click the edit icon, change **Stage Name** (up to 12 characters) and save.

**How do I delete a fixture stage?** Click the delete icon, then **Yes, Delete**. All changes made in the stage are lost.

**Why do I see "Please save all stage configurations before generating fixtures"?** A stage was changed but not saved. Save each stage, then generate again.

**Why can I not change Round Robin to Double Round Robin?** Once one of the two is chosen, the other is greyed out for that stage.

**What does "Secondary group size must differ from primary by exactly 1" mean?** The two group sizes in a stage must be one apart. Change one of the sizes.

**What does Publishing Successful mean?** The preview was published. Choose **Go to Scheduler** to schedule the matches, or **Stay here**.
