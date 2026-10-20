---
doc_id: tms.players.club-association
title: Players page – Club and Member Association columns
routes:
  - tms/players/:event_id
aliases:
  - club column
  - member association column
  - MA column
  - club and member association
  - parent organisation
  - select organisation
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - Why is the Club column not visible?
  - Why is the Member Association (MA) column missing?
  - How do I show both Club and Member Association?
  - Why is the club empty for some players?
  - Why do I see short names instead of club names?
backend_sources:
  - tms/src/crud/registration_crud.py (selected parents per category: _register_event_category_selected_parent_roles, _build_selected_parents_config_map)
  - gateway/src/routers/events_router.py (create_event_categories; Player Screen + Edit Category permissions)
source_files:
  - src/app/modules/tms/players/players.component.ts (applyEntitySettingsConfiguration, create_enitity_setttings, playerEntity, updateColumnsForSelectedRole)
  - src/app/modules/tms/players/players.component.html
  - src/app/shared/components/stupa-entity-setting/stupa-entity-setting.component.ts
  - src/app/core/services/common-service/common-service.service.ts (getParentDisplayForRole, getParentDisplayValue)
---
# Players page – Club and Member Association columns

This guide explains the **Club** and **Member Association** columns of the player list on the **Players** page: what they show, why one or both may be missing or empty, and how to turn them on. MA is short for Member Association.

## Club and Member Association: what the columns show

- A player belongs to organisations above them, called parents: their **Club**, and the **Member Association** (MA) the club belongs to.
- The **Club** and **Member Association** columns of the player list show these parents for each entry.
- For pairs (doubles, mixed doubles) each cell has two lines, one per player.
- For teams the cells show the organisation the team belongs to.
- The values are the ones recorded when the entry was registered, so a later club change in the player's profile does not change the list.

## Why the Club or Member Association column is not visible

The columns are not shown by default. They appear only for what is chosen under **Select Organisation** in the category's **Settings**. Check in this order:
1. **Settings were never saved for this category.** With no saved choice, neither column is shown. Open **Settings**, choose the organisation and save.
2. **The other organisation is chosen.** **Club** shows only the Club column, **Member Association** only the MA column. Choose **Both** to see both.
3. **Each category has its own setting.** Showing the club in one category does not show it in another. A sub category also has its own setting: select the sub category tab and save **Settings** there.
4. **Settings is greyed out**, so the choice cannot be changed: no category is selected, or the category's **Registration** toggle is off. Turn the toggle on on the event's **Registration** page.
5. **The columns stay from the category you looked at before.** After switching to a category that has no saved choice, the page can keep the previous category's columns. Reload the page to see the real setting.

## How to show the Club and Member Association columns

1. Select the category (or sub category) tab on the Players page.
2. Click **Settings**. The side panel opens.
3. Under **Select Organisation** choose **Club**, **Member Association** or **Both**.
4. Under **Parameter** choose how the organisation is shown (see below).
5. Save. The server confirms it and the list reloads with the columns.

- Saving needs **Edit** permission on **Player Screen** and on **Edit Category**; without it the server answers "Access Denied".
- The choice is stored on the category, so everyone who opens the category sees the same columns.

## Why the Club or Member Association cell is empty

The column is shown but a cell is empty:
- **No parent was recorded.** The player had no club (or no member association) when they were registered, for example a player without a club or a temporary player added without one.
- **Abbreviation is ticked but the organisation has no abbreviation.** With **Abbreviation** on, the cell shows the organisation's short name only; an organisation without one shows an empty cell. Untick **Abbreviation** to show full names, or add the abbreviation to the organisation's profile.
- **Pairs:** only the line of the player without that parent is empty.

## Parameter: names, abbreviations, logo and flag

- Without **Abbreviation** the cells show the full name of the club or association.
- With **Abbreviation** they show its short name (abbreviation) instead of the full name.
- **Logo** or **Flag** (only one of the two) choose whether the organisation's logo or the country flag is used where the event shows organisations with an image, for example schedules and match lists. They do not add an image to the Players list.
- With **Both** chosen, **Logo**, **Flag** and **Abbreviation** are all greyed out.

## Club and Member Association columns: order and other lists

- Singles: **Club** comes first, then **Member Association**. Pairs and teams: **Member Association** first, then **Club**.
- The **Queue** and **Deleted** lists use the same setting.
- In the **Add Player** panel the list shows one organisation column: **Member Association** when it is chosen (also with **Both**), otherwise **Club**.
- The same setting is also used by other event screens that show a participant's organisation.

## Frequently asked questions about the Club and Member Association columns

**Why is the Club column not visible?** Club is not chosen for this category. **Settings** → **Select Organisation** → **Club** or **Both** → save.

**Why is the Member Association (MA) column missing?** **Settings** → **Select Organisation** → **Member Association** or **Both** → save.

**What does MA mean?** Member Association, the organisation a club belongs to.

**How do I show both Club and Member Association?** Choose **Both** under **Select Organisation** in **Settings** and save.

**I set Club in one category but another category has no Club column. Why?** Each category and each sub category has its own **Settings**.

**Why is the club empty for some players?** No club was recorded when they registered, or **Abbreviation** is on and their club has no abbreviation.

**Why do I see short names instead of club names?** **Abbreviation** is ticked in **Settings**. Untick it and save.

**Why can I not open Settings to change the columns?** Select a category and turn on its **Registration** toggle on the Registration page.

**A player changed club. Why does the list show the old one?** The list shows the club recorded at registration.
