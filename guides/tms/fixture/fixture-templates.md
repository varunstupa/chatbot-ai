---
doc_id: tms.fixture.templates
title: Fixture templates – choose a ready-made draw
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - fixture template
  - fixture templates
  - genuine fixture
  - sample fixture
  - custom fixture
  - select from our templates
  - create your own fixture
  - predefined templates
  - predefined fixture templates
  - predefine template
  - ready-made templates
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I create fixtures from a template?
  - What is the difference between a Genuine and a Sample fixture?
  - How do I create a custom fixture?
  - Why are the templates not shown?
  - Why did creating a fixture from a template fail?
backend_sources:
  - gateway/src/routers/stage_router.py (create_fixture_from_template, delete_fixture_template; feature EDIT_STAGE, Edit)
  - tms/src/service/stage_service.py (create_fixture_from_template, delete_fixture_template)
source_files:
  - src/app/modules/tms/fixture-templates/fixture-templates.component.ts
  - src/app/modules/tms/fixture-templates/fixture-templates.component.html
---
# Fixture templates – choose a ready-made draw

A **fixture template** creates all the stages of a draw in one step, for example a group stage followed by a knockout stage. The templates are shown on the **Fixtures and Results** page under **Specify stage details**. Choose one, or choose **Create your Own** to build the stages yourself.

## Where the templates are

- Open **Fixtures/Results** from the sidebar (the templates are not on the Event page). The section **Specify stage details** shows **Select from our Templates** above the custom option.
- While the list loads, **Loading templates...** is shown.
- The templates are hidden for organisations with the option that hides them (the section is then not shown at all).
- Each template shows its name, its stages (for example "Group Stage" and "Knockout Stage") and its description.
- The format descriptions used in the stage choice:
  - Round Robin – "A competition format where each participant plays every other participant once in a round, regardless of win or loss."
  - Knockout – "Knockout is a single elimination round where the losing participant is immediately eliminated from the competition."
  - **Hide stage selection** closes the list of stages; **Close dialog** closes the whole panel.
- Under the description a template can show three labels when the organiser has set them: the suitable duration, the competition type and the tournament type.

## Create fixtures from a template

1. Click a template to expand it.
2. Choose the **fixture type** in the panel **Select fixture type**:
   - **Genuine** – "Once your participants are finalised, use the genuine option to create the fixtures."
   - **Sample** – "If participants aren't finalized, use the sample fixture. Update it with the real participants later."
3. The choice creates all the stages of the template at once. The page then opens the first stage of the new draw.
4. Click the close button of the panel to close it without creating anything.

## Create your own (custom fixture)

1. Click **Custom Fixture** – "Any fixture format": "Select Knockout or Group Stage and configure settings manually at each step."
2. **STEP 1**: choose **Genuine** or **Sample** (same meaning as above).
3. **STEP 2 – Select stage to start with**:
   - **Knockout Stage** – "Single-elimination; losing one match eliminates."
   - **Group Stage** – "Groups then knockout; teams play within groups." Then choose **Round Robin** or **Double Round Robin**. Once one is chosen, the other is greyed out.
4. The stage then opens in the configuration wizard (see the group and knockout guides).

## Predefined templates: group formats

There are six predefined templates: Group Playoff, Group Play-Off + Consolation, Group + Preliminary + Main Draw, Round Robin, Double Round Robin and Knockout. They are on the Fixtures/Results page: open **Fixtures/Results** from the sidebar, then look under **Select from our Templates** in **Specify stage details**. The group formats are:

- **Group Playoff** (code GROUP_PLAYOFF): a Group Stage, then a Knockout Stage. Participants compete in groups; the top 2 of each group advance to the Knockout. Description: "Participants compete in groups, and the top players advance to a final Knockout stage." Labels: Med-Duration, Fair competition, Small-Med Tournaments.
- **Group Play-Off + Consolation** (code GROUP_PLAYOFF_CONSOLATION): a Group Stage, then a Knockout Stage (Main Draw), then a Knockout Stage (Consolation). The top 2 of each group go to the Main Draw; the losers of the Main Draw go to the Consolation bracket. Labels: Longer Duration, Maximum Playtime, Medium Tournaments.
- **Group + Preliminary + Main Draw** (code GROUP_PRELIMINARY_KNOCKOUT): a Group Stage, then a Knockout Stage (Preliminary), then a Knockout Stage (Main Draw). The top 2 of each group go to the Preliminary; all Preliminary winners go to the Main Draw. Labels: Longer Duration, Structured Multi Stage, Large Tournaments.

## Predefined templates: round robin and knockout

There are six predefined templates: Group Playoff, Group Play-Off + Consolation, Group + Preliminary + Main Draw, Round Robin, Double Round Robin and Knockout. They are on the Fixtures/Results page: open **Fixtures/Results** from the sidebar, then look under **Select from our Templates** in **Specify stage details**. The round robin and knockout formats are:

- **Round Robin** (code ROUND_ROBIN): one stage with all participants in one group. Each participant plays every other once, and the winner is decided through the standings. Labels: Longer Duration, Maximum Playtime, Small Tournaments.
- **Double Round Robin** (code DOUBLE_ROUND_ROBIN): one group where each pair plays twice (2 legs). The winner is decided through the standings. Labels: Longest Duration, Maximum Playtime, Small Tournaments.
- **Knockout** (code KNOCKOUT): one single-elimination Knockout Stage using all registered players. One loss and the player is out. Labels: Short Duration, Quick Elimination, Any Size.
- The templates and their descriptions can be updated for your organisation; the screen always shows the current ones.


## Messages

- Success: the server's message, for example "Fixture template created successfully". When the server sends none: "Fixture created from template." The page then shows the new stage.
- Failure: the server's message; if none: "Failed to create fixture from template."
- Server checks when a template is created:
  - the event category does not exist → "Event Category Not Found";
  - the category is not a sub category when the template needs one → "Create Stages Only For Sub Categories";
  - the category already has stages → "Stages Already Exist For Event Category" (**this text has no English translation yet**, so the screen may show an empty message; report it to the administrator).

## Delete the stages of a template

- Deleting a template removes all its stages of the category (the stages are marked deleted, not lost from the database).
- Success: "Fixture template deleted successfully".
- "No Stages Found" when the category has no stages; "Event Category Not Found" when the category does not exist.
- A knockout stage's delete icon is hidden when it belongs to a template (see the stages guide).

## Permissions

- Creating or deleting a template needs **Edit** on **Edit Stage**. Without it the server answers "Access Denied".

## Frequently asked questions about fixture templates

**How do I create fixtures from a template?** Expand the template, choose **Genuine** or **Sample**, and the stages are created.

**What is the difference between a Genuine and a Sample fixture?** Use Genuine when the participants are final. Use Sample when they are not, and update the sample with the real participants later.

**How do I create a custom fixture?** Click **Custom Fixture**, choose Genuine or Sample, then Knockout Stage or Group Stage (with Round Robin or Double Round Robin).

**Why are the templates not shown?** The organisation has hidden them. Use **Custom Fixture** instead.

**Why did creating a fixture from a template fail?** Read the message. "Stages Already Exist" means the category already has stages; delete them or open the existing draw.

## Frequently asked questions about predefined templates

**What are the predefined fixture templates (which templates are available)?** Six: Group Playoff, Group Play-Off + Consolation, Group + Preliminary + Main Draw, Round Robin, Double Round Robin and Knockout. To see them: 1. Open **Fixtures/Results** from the sidebar. 2. In **Specify stage details**, look under **Select from our Templates**.

**Which template has a consolation bracket?** Group Play-Off + Consolation. The losers of the Main Draw play in the Consolation bracket.

**Which template suits a large event?** Group + Preliminary + Main Draw, labelled Large Tournaments.
