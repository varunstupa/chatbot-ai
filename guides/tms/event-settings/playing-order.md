---
doc_id: tms.event-settings.playing-order
title: Playing Order settings page
routes:
  - tms/event-settings/playing-order/:event_id
aliases:
  - playing order
  - playing order setting
  - playing order step
  - team playing order
  - team match format
  - match order
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I set the playing order for a team category?
  - Why is my playing order format not in the list?
  - Does changing the format affect draws I already made?
  - How do I give every team category the same format?
backend_sources:
  - gateway/src/routers/events_router.py (update_event_category_playing_order)
  - gateway/src/routers/playing_order_router.py (get_team_playing_order)
  - gateway/src/decorators/decorator.py (auth_decorator, permission_decorator)
  - tms/src/router/events_router.py (update_event_category_playing_order)
  - tms/src/router/playing_order_router.py
  - tms/src/crud/playing_order_crud.py
  - tms/src/crud/events_crud.py (update_category_playing_order)
  - tms/src/service/stage_service.py (create_stage copies the category format to the stage)
source_files:
  - src/app/modules/tms/tournament-playing-order/tournament-playing-order.component.ts
  - src/app/modules/tms/tournament-playing-order/tournament-playing-order.component.html
  - src/app/modules/tms/events-settings/events-settings.component.ts
  - src/app/modules/tms/events-settings/events-settings.component.html
  - src/app/core/services/playing_order/playing_order.ts
  - src/app/modules/admin/playing-order-creation/playing-order-creation.component.html
---
# Playing Order settings page – user guide

This guide describes the **Playing Order** step of an event in the Stupa Event Management System (admin panel). On this page the organiser chooses, for each Teams category of the event, which playing order format (team match format) is used. It also explains what the choice affects and what to do when something is missing.

## Where to find it

Open **Event** from the sidebar, then click **Playing Order** in the row of setup steps at the top of the page.

## Playing Order page: where it is and what it is for

- Page address: `/tms/event-settings/playing-order/<event id>`, for example `/tms/event-settings/playing-order/1358`.
- It is the **Playing Order** step in the row of event setup steps. The step is only shown for organisations that use team playing orders.
- Page heading: **Playing Order Setting**.
- A playing order format describes a team match: which individual matches are played between two teams, in which order, singles or doubles, and an optional **Golden Match Order** used to break a tie between the teams.
- On this page you do not create formats. You pick one of the formats your organisation has already created and published, and link it to a category.
- Only **Teams** categories are listed. Singles, Doubles and Mixed Doubles categories do not use a playing order and never appear here.

## Playing Order page: layout

From top to bottom:

1. **Category tabs** – one tab per Teams category of the event, with a **T** badge. Use the left and right arrows to scroll. The selected tab is shown in bold. The first Teams category is selected when the page opens.
2. **Apply Same format to all Classes** – a checkbox (see "Applying one format to all Teams categories").
3. **Format list** – every published playing order format, each with an info icon, its name and a radio button on the right. The newest formats are listed first.
4. **Reset** and **Update** buttons.

The radio button that is filled shows the format currently saved for the selected category. If no radio button is filled, the category has no format yet.

## Playing Order page: choosing a format for a category

1. Click the category's tab.
2. Click the radio button of the format you want. The format opens below its name and shows its **Match Order** (and **Golden Match Order**, if it has one).
3. Click **Update**.
4. The message "Playing Order updated successfully." confirms the save.

Notes:
- Each category stores its own format. Changing the tab shows the format of that category.
- Selecting a radio button alone does not save anything. Click **Update**.
- If you click **Update** without choosing a format, the message is "Please Select Playing Format".
- When you toggle to a category that has no format yet, click a format's radio button before clicking **Update**. Do not click Update while no radio button is filled.

## Playing Order page: previewing a format

There are two ways to look at a format before choosing it:

- **Info icon** (the "i" in a circle left of the format name): hover over it and click it to open a small preview window with the format's **Match Order** and **Golden Match Order**. Click elsewhere to close it.
- **Radio button**: selecting a format opens its match order below the name.

How to read the preview:
- Each line is one individual match of the team match, in playing order. The two sides are separated by `-`.
- A singles line shows one position per side, a doubles line shows two positions per side.
- A fixed position is shown as its letter or label followed by **Player Name** (for example "A Player Name").
- A position shown as a small dropdown with the placeholder **Set** is one the team chooses itself when the lineup is entered for a match.
- The dropdowns in the preview are for viewing only. A value picked there is **not saved**. Only the choice of format is saved.
- When a saved format is shown on opening the page, click its radio button to see its match order.

## Applying one format to all Teams categories

- Tick **Apply Same format to all Classes**, choose a format and click **Update**. The format is saved for **every Teams category of the event**, not only the selected one.
- After the save the category list reloads.
- There is no way to pick only some categories. To give different categories different formats, leave the checkbox unticked and save each category on its own tab.
- **The checkbox also affects Reset.** While it is ticked, **Reset** removes the format from every Teams category of the event.
- Untick the checkbox before working on a single category again.

## Reset button: removing the format from a category

- **Reset** removes the saved format from the selected category. Afterwards no radio button is filled and the category has no playing order.
- Reset is greyed out until a format is selected.
- Reset saves immediately. No confirmation is asked and no success message is shown; the radio button simply clears.
- With **Apply Same format to all Classes** ticked, Reset clears the format of every Teams category of the event.
- Stages (draws) that were already created keep their format (see "What the playing order affects").

## What the playing order affects

- The category's format is used when a stage (draw) is created for that Teams category on the Fixtures screen. The new stage takes the category's format, and the team matches of that stage follow it: the individual matches, the lineup positions, scoring and score sheets.
- **Set the playing order before creating the draws.** A stage keeps the format it received when it was created.
- Changing or resetting the format here later does **not** change stages that already exist or matches that were already generated. Only stages created after the change use the new format.
- The page does not block a change after draws or matches exist, so check the Fixtures screen before relying on a change.
- A category without a format creates stages without a playing order. Choose a format before creating the stage.

## Where playing order formats come from

- Formats are created and published by your organisation in **Playing Order Configuration** ("Customize Playing Order as per your requirement"), found in the admin manage menu at `/admin/manage/playing-orders`. There a format is added with **Add Playing Order**, given a **Format Name**, its matches and an optional **Golden Match Order** ("Add a golden match order that is only a part of the created playing order. (Performed on tie between the teams)"), and saved with **Save** or **Publish**.
- Only formats whose **Publish** toggle is on are listed on this page. A saved but unpublished format does not appear.
- A deleted format does not appear.
- The page loads the 100 newest formats of the organisation and then shows the published ones among them. A published format that is older than the 100 newest formats does not appear.
- Formats belong to the organisation, not to the event. The same format can be used in many events.
- Editing a format in Playing Order Configuration changes it for every category and event that uses it.

## Playing Order page: empty pages and what they mean

- **"No record found" – "Add Categories in this event to begin with Playing Order."** with a **Go to Event** button: the event has no categories at all. Click **Go to Event** and add categories in the **Add Class/Category** panel of the Details step.
- **"Create Event to begin with Playing Order."**: the event has not been saved yet. Create it on the Details step first.
- **"No category has been added to this event. Please add categories in the Event Details tab first."**: the event has categories, but none of them is a **Teams** category. This page only works with Teams categories. If the event should have team matches, add a Teams category on the Details step.
- **"No formats were found. You can create new formats by clicking the button below."**: the organisation has no published playing order format. Click the button below the message to open Playing Order Configuration, create a format and toggle on **Publish**, then return to this page.

## Playing Order page: messages when saving and what they mean

When you click **Update** or **Reset**, the server's message appears at the bottom of the screen.

- **"Playing Order updated successfully."** – the format was saved.
- **"Please Select Playing Format"** – no format is chosen. Click a format's radio button first.
- **"Playing Order Id is Invalid"** – the chosen format was deleted after the page was opened. Reload the page and choose another format.
- **"Provided Category Ids Are Invalid"** – a category is no longer part of the event (it was deleted on the Details step). Reload the page.
- **"Invalid Event Id Provided"** – the event no longer exists.
- **"Access Denied"** – your role may not change the playing order of this event (see "Playing Order page: permissions and sessions").
- **"Unauthorized Access"** – your session expired or is not valid for this organisation. Sign in again.
- If loading the categories or the formats fails, the server's message is shown and the list stays empty. Reload the page.

## Playing Order page: permissions and sessions

- Saving needs **Edit** permission on **"Edit Playing Order"** for this event. Without it, **Update** and **Reset** fail with "Access Denied". The buttons are still shown; the check happens when you save.
- Permissions are given per event. Having Edit on one event does not give it on another. Other users are given access on the event's **Access-Control** step.
- The main administrator account and users with Live Match Centre access to the event are also allowed to save.
- A sign-in lasts a limited time. After it ends, saving fails with "Unauthorized Access" and you must sign in again.
- Creating or publishing formats in Playing Order Configuration needs the separate **"Playing order Configuration"** permission.

## Frequently asked questions about the Playing Order page

**How do I set the playing order for a team category?** Click the category's tab, click the radio button of a format, then click **Update**.

**How do I give every team category the same format?** Tick **Apply Same format to all Classes**, choose the format and click **Update**.

**Why are my Singles or Doubles categories missing?** Only Teams categories use a playing order and are listed here.

**Why is my format not in the list?** Only published formats are listed. Toggle on **Publish** for it in Playing Order Configuration. Deleted formats, and formats older than the organisation's 100 newest, are not shown.

**Why does the page say no category has been added when my event has categories?** None of the categories is a Teams category.

**Does changing the format affect draws I already made?** No. A stage keeps the format it had when it was created. Only stages created afterwards use the new format.

**When should I set the playing order?** Before creating the draws (stages) for the Teams category.

**How do I remove a format from a category?** Select the category and click **Reset**. Untick **Apply Same format to all Classes** first, or Reset clears every Teams category.

**Why did Reset clear all my categories?** **Apply Same format to all Classes** was ticked.

**Why is Reset greyed out?** No format is selected for the category.

**I chose players in the Set dropdowns but they are gone after reload.** The dropdowns in the format preview are not saved. Lineups are entered per match.

**What is a Golden Match Order?** An extra match played only to break a tie between the two teams, if the format defines one.

**Why do I get "Please Select Playing Format"?** You clicked **Update** without choosing a format. Click a format's radio button first.

**Why do I get "Access Denied"?** Your role needs Edit permission on "Edit Playing Order" for this event. Ask an administrator.

**Where do I create a new playing order format?** In Playing Order Configuration (`/admin/manage/playing-orders`), or with the button shown when no formats are found.

**Does editing a format change other events?** Yes. A format is shared by every category and event that uses it.
