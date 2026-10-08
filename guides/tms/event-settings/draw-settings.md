---
doc_id: tms.event-settings.draw-settings
title: Draw Settings page
routes:
  - tms/event-settings/draw-settings/:event_id
aliases:
  - draw settings
  - draw setting
  - draw settings step
  - global draw settings
  - separation settings
  - entity separation
  - club separation
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I keep players from the same club apart in the draw?
  - What is the difference between Seeding and Random Seeding?
  - Do these settings change draws I already made?
  - What does Group Separation do?
backend_sources:
  - gateway/src/routers/events_router.py (get_event_configs, upsert_event_configs)
  - gateway/src/decorators/decorator.py (auth_decorator)
  - tms/src/router/events_router.py (get_event_configs, upsert_event_configs)
  - tms/src/service/event_config_service.py
  - tms/src/service/draw_settings_service.py (fallback and stage creation defaults)
  - tms/src/schema/draw_settings_schema.py
  - tms/src/service/stage_service.py (create_stage applies draw settings)
source_files:
  - src/app/modules/admin/tournament-config/draw-setting/draw-setting.component.ts
  - src/app/modules/admin/tournament-config/draw-setting/draw-setting.component.html
  - src/app/core/utils/draw-setting/draw-setting.mapper.ts
  - src/app/core/utils/draw-setting/draw-setting.constants.ts
  - src/app/core/services/draw-setting/draw-setting.service.ts
  - src/app/modules/tms/events-settings/events-settings.component.ts
---
# Draw Settings page – user guide

This guide describes the **Draw Settings** step of an event in the Stupa Event Management System (admin panel). On this page the organiser sets how draws for this event keep participants from the same club or member association apart, and how the first knockout draw is seeded. It also explains when these settings are used and where they come from.

## Draw Settings page: where it is and what it is for

- Page address: `/tms/event-settings/draw-settings/<event id>`, for example `/tms/event-settings/draw-settings/2958`.
- It is the **Draw Settings** step in the row of event setup steps.
- The heading on the page reads **Global Draw Settings** with the text "Define the default entity separation criteria and their priority for both Group Stage and Knockout Draws." On this step the settings apply to **this event only**, despite the word "Global".
- The settings are **defaults for new draws**. They are used when a stage (draw) is created on the Fixtures screen. They do not create a draw themselves.
- The settings apply to the whole event: every category and every stage created afterwards. They cannot be set per category on this page.
- The event must be saved first. For an unsaved event the step shows "Create Event to begin with Draw Settings."

## Draw Settings page: layout

From top to bottom:

1. **Group Stage settings** – "Select a default criterion and assign priorities". Two choices: **Member Association** and **Clubs**.
2. **Knockout Stage settings** – "Select a default criterion and assign priorities", with four parts:
   - **PARENT SELECTION ORDER** – **Member Association** and **Clubs**.
   - **GROUP SEPARATION** – a switch.
   - **First Time Draw Settings** – **Seeding** or **Random Seeding**.
   - **Separation Type** – **As far as possible** or **1st Round Only**.
3. **Save** button in the bar at the bottom of the page, always visible.

Nothing is stored until you click **Save**. Leaving the page discards unsaved changes without warning.

## Separation criteria and priorities (Member Association, Clubs)

The criteria decide which participants the draw keeps apart: those from the same **Member Association**, the same **Club**, or both.

- Click a criterion to select it. It gets a number badge: its **priority**. The first one you click is **1**, the next **2**.
- Click a selected criterion again to remove it. The remaining criteria move up (2 becomes 1).
- To change the order, click both to remove them, then click them again in the order you want.
- Priority **1** is the most important separation. When the draw cannot satisfy every criterion, the higher priority is kept.
- A criterion that is not selected shows an empty circle and is not used.
- With **no criterion selected**, draws created afterwards do not separate by club or member association.
- **Group Stage settings** are used for group (round robin) stages. **PARENT SELECTION ORDER** under Knockout Stage settings is used for knockout stages. The two lists are independent.

## Knockout Stage settings: GROUP SEPARATION

- Panel text: "Control whether separation based on Group Stage finishing position is applied."
- Switch on: when a knockout stage follows an earlier stage (for example groups, then knockout), participants who came from the same group are kept apart in the knockout draw.
- Group separation then becomes priority **1**. The criteria chosen in PARENT SELECTION ORDER move down one place (Clubs priority 1 becomes priority 2).
- It has no effect on the first stage of a category, because there are no earlier groups.
- Switch off: the group a participant came from is not used to separate them.
- It applies to knockout stages only.

## Knockout Stage settings: First Time Draw Settings (Seeding or Random Seeding)

Choose how the first knockout draw places seeded participants.

- **Seeding** – "Draw is created strictly based on defined seeds, respecting entity and group separation."
- **Random Seeding** – "The initial knockout draw randomizes seeding within levels, maintaining entity and group separation. This mandatory shuffle applies to the first draw (Global Random Selection)."
- The shuffle happens when the knockout draw is made, so drawing the same stage again can give a different result.
- Separation by club, member association and group is kept with both options.
- Only one option can be selected. **Seeding** is used if neither has been chosen.

## Knockout Stage settings: Separation Type

Choose how far into the knockout draw participants from the same club or member association are kept apart.

- **As far as possible** – "Current logic to separate entities (Club/MA) for as many rounds as possible." Participants of the same entity meet as late as the draw allows.
- **1st Round Only** – "System ensures separation of entities only in the first round. If Group Separation is enabled, it takes P1 priority, and entity separation will apply the \"1st Round Only\" rule." Participants of the same entity can meet from the second round on.
- Only one option can be selected. **As far as possible** is used if neither has been chosen.
- The entities used are the ones selected under **PARENT SELECTION ORDER**.

## Draw Settings page: saving

- Click **Save** at the bottom. The button is disabled while the save is in progress.
- Success message: "Config Upserted Successfully".
- One Save stores the whole page: both stage cards and every knockout option together.
- The page keeps showing the saved values. Reload the page to confirm what is stored.
- If the save fails, the server's message is shown, or "Something went wrong" when there is none. Nothing is changed in that case.

## Where the values on the page come from (event, organisation, default)

When the page opens it shows, in this order of preference:

1. **The settings saved for this event**, if Save was ever clicked on this step.
2. Otherwise, **your organisation's global draw settings**, set in the admin area under **Event Configuration** > **Draw Settings** (`/admin/manage/tour-config`). That page has the same layout and the description "Configure default Group Stage and Knockout draw settings, including separation criteria, separation basis, group separation, and bracket generation rules."
3. Otherwise, the **system defaults**:
   - Group Stage settings: **Clubs** priority 1, **Member Association** priority 2.
   - Knockout PARENT SELECTION ORDER: **Clubs** priority 1.
   - GROUP SEPARATION: off. First Time Draw Settings: **Seeding**. Separation Type: **As far as possible**.

Until you click **Save** on this step, the event follows the organisation's settings. After saving, the event keeps its own settings: later changes to the organisation's global draw settings no longer affect it.

## What the draw settings affect and when

- The settings are read **when a stage is created** on the Fixtures screen:
  - A **group** stage takes the Group Stage criteria.
  - A **knockout** stage takes the PARENT SELECTION ORDER criteria, GROUP SEPARATION, First Time Draw Settings and Separation Type.
- A value already chosen for the stage itself on the Fixtures screen wins. The draw settings only fill in what the stage does not set.
- **Stages that already exist are not changed** when you save this page. Only stages created afterwards use the new settings. To use new settings for an existing draw, change them on that stage on the Fixtures screen, or delete the stage and create it again.
- **Set the draw settings before creating the stages** of the event.
- The page does not block changes after draws exist, so check the Fixtures screen if you change settings late.

## Draw Settings page: messages and what they mean

- **"Config Upserted Successfully"** – the settings were saved for this event.
- **"Something went wrong"** – the save or load failed and the server gave no reason. Try again.
- **"Unauthorized Access"** – your session expired or is not valid for this organisation. Sign in again; unsaved changes are lost.
- **"Create Event to begin with Draw Settings."** – the event has not been saved yet. Create it on the Details step first.
- A message starting with "Invalid" names a value the server could not accept. Reload the page and choose the options again.
- If loading fails, an error message is shown and the page shows its starting values. Reload the page before saving, so you do not overwrite the stored settings with those starting values.

## Frequently asked questions about the Draw Settings page

**How do I keep players from the same club apart in the draw?** Select **Clubs** in Group Stage settings and in PARENT SELECTION ORDER, give it priority 1 if it matters most, and click **Save** before creating the stages.

**How do I change the priority order?** Click the selected criteria to remove them, then click them again in the order you want. The first one clicked gets priority 1.

**What is the difference between Seeding and Random Seeding?** Seeding places seeds strictly by their seed number. Random Seeding shuffles seeds within the same level for the first knockout draw. Both keep club, association and group separation.

**What does Group Separation do?** In a knockout stage that follows a group stage, players who came from the same group are kept apart. It becomes priority 1, ahead of club and member association.

**What is the difference between As far as possible and 1st Round Only?** As far as possible keeps same-entity participants apart for as many rounds as possible. 1st Round Only keeps them apart in the first round only.

**Do these settings change draws I already made?** No. They are applied when a stage is created. Change an existing stage on the Fixtures screen.

**Why does the page say "Global Draw Settings" on my event?** The heading is shared with the organisation-wide page. On the event step the settings are saved for this event only.

**Why does my event show settings I never saved?** The event has no settings of its own yet, so the page shows your organisation's global draw settings or the system defaults.

**Do changes to the organisation's global draw settings affect my event?** Only if the event never saved its own settings on this step.

**Can I set different draw settings per category?** Not on this page. It applies to the whole event. Adjust an individual stage on the Fixtures screen.

**What happens if I select no criterion?** New stages are drawn without club or member association separation.

**Where are the organisation-wide draw settings?** In the admin area under Event Configuration > Draw Settings.

**I changed options but they are gone.** Click **Save** before leaving the page. Unsaved changes are discarded without warning.
