---
doc_id: tms.players
title: Players page
routes:
  - tms/players/:event_id
aliases:
  - players page
  - players screen
  - player list
  - participants list
  - registered players
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What can I do on the Players page?
  - What do the columns of the player list mean?
  - Why is the Add button greyed out?
  - What does the red mark next to a player mean?
  - Why do I not see a category on the Players page?
backend_sources:
  - gateway/src/routers/registration_router.py (get_event_participants, get_participant_counts; feature "Player Screen")
  - tms/src/service/registration_service.py
source_files:
  - src/app/modules/tms/players/players.component.ts
  - src/app/modules/tms/players/players.component.html
  - src/app/modules/tms/players/category-participant-count-tab/category-participant-count-tab.component.html
---
# Players page – user guide

This guide describes the **Players** page of an event in the Stupa Event Management System (admin panel). It lists every participant registered in each category of the event – singles players, doubles and mixed doubles pairs, and teams – and is where the organiser adds, removes, seeds, numbers, moves and exports them.

Other guides cover the Players page in more detail: adding singles players and add errors; pairs and teams; seeding and back numbers; queue, delete, forfeit and unpaid players; transfer, recreate, merge and sub categories; import, export and settings.

## Where to find it

Open **Players** from the sidebar.

## Players page: where it is and what it is for

- Page address: `/tms/players/<event id>`, for example `/tms/players/1358`.
- Open it from the event's menu (**Players**).
- Without an event the page shows "No record found" – "Create Event to begin with Players." With an event that has no categories: "Add Categories in this event to begin with Players." **Go to Event** opens the event setup.
- The page header shows **Classes/Categories** (tournaments) or **Divisions** (leagues), and the counter **Participants remaining** – how many participants still have no back number, out of all participants (for example "12 / 40").
- Header buttons: **Back No.** (back numbers), **Seeding** (bulk seeding for all categories) and **Sync** (refresh seeding metrics).

## Category tabs and participant type filter on the Players page

- The tab row shows one tab per **Category** (tournament) or **Division** (league). Use the arrows to scroll. Click a tab to see its participants.
- Each tab shows a badge: players registered (singles, doubles, mixed doubles) or teams registered (teams). Hover over it for the breakdown – singles: **Players Registered**; doubles: also **No. of Pairs**; mixed doubles: also **Males** and **Females**; teams: **Teams Registered**, total players, **Males**, **Females**.
- A category that has sub categories shows their number in brackets, for example "Men's Singles ( 3 )". Selecting it shows a second tab row with the **Sub Category** (or **Sub Division**) tabs.
- The dropdown before the tabs filters the tabs by participant type: **All**, **Singles**, **Teams**, **Doubles**, **Mixed Doubles**.
- For doubles, mixed doubles and team categories two sub-tabs appear: **Singles** (players who registered alone and still need a partner or team) and **Team-up** (the formed pairs or teams). They only appear when the **Player** role is ticked in **Allow Registrations** for the category.
- The first category is selected when the page opens.

## Player list columns on the Players page

- **Sr.No**, **License ID** (not for teams), **Player Name** or **Team Name**.
- **Club** and/or **Member Association** (MA) – the player's parent organisations. They are hidden until **Select Organisation** is saved in the category's **Settings** (see "Players page – Club and Member Association columns").
- **Back No.** – the player's back (bib) number.
- **Seed** – the seed; when the organisation's **Display Seed** setting is on, this column shows the display seed. **Rank**, a world-rank column when the organisation enabled it, **Points** – "In" points come from the internal platform, "Ex" points from an external platform.
- **Gender** and **DOB** (singles), **Total Player** (teams), **Registration Entry Date**, **Action** (the ⋮ menu).
- Doubles rows show both players with their licence IDs, back numbers and dates of birth. Mixed doubles show the male and the female player.
- An **Elite** badge next to a doubles player marks an elite participant; elite entries are counted separately when the draw stages are set up.
- In the Queue, Deleted and Back No. lists, the player type column shows **Federation-Registered Player**, **Unaffiliated Player** or **Passport-Eligible Player** (league lists: **Federation/Unaffiliated/Passport**).
- "--" means the value is missing.

## Who appears in the player list

The list shows only entries that are **accepted** (verified), **paid**, active, and not queued or deleted. A registered player who is missing is in one of these places:
- not yet paid → **Unpaid Players**;
- in the queue (category full or moved there) → **Queue**;
- deleted or withdrawn → **Deleted**;
- waiting for verification → appears after the registration is accepted;
- doubles/teams player without partner or team → the **Singles** tab.

## Searching, sorting and paging the player list

- Type in **Search** to find participants by name.
- Click the **Player Name** (or **Team Name**) heading or the **Seed** heading to sort ascending or descending.
- Use the paginator at the bottom to change page or rows per page.
- "No record found" means nothing matches the category, filter or search.

## Row menu (⋮) on the Players page (tournaments)

In tournaments, click ⋮ in the **Action** column of a participant:
- **Edit** – pairs and teams: change the players of the entry. Singles: only temporary players (added without an account) can be edited here.
- **Forfeit** / **Undo Forfeit** – withdraw the participant from upcoming matches or restore them.
- **Delete** / **Delete & Refund** – remove the participant (see the queue and delete guide).

Forfeited participants show a red mark instead of the checkbox and "(forfeited)" after the name.

## League events: no ⋮ menu, action icons on each row instead

League events have no ⋮ menu. The **Action** column of each row shows these icons instead:
- **Player Details** – the team's roster: players, Active/Reserve, rank values, player images, loan players.
- **Team Details** – the team's profile: name, organisations, contact, members, venues, team image and logo.
- **Delete** and **Delete & Refund** – remove the entry.
- **Forfeit** (the "F" icon) – forfeit the entry or, when forfeited, **Undo Forfeit**.

See "Players page – pairs and teams" for both panels.

## What each participant type offers on the Players page

- **Singles** – columns License ID, Gender, DOB; **Add** opens **Add Player**; ⋮ → **Edit** only for temporary players; no Singles/Team-up tabs.
- **Doubles** – both players per row with licence IDs, back numbers and DOBs; **Add** opens **Add Pairs**; **Singles** and **Team-up** tabs; ⋮ → **Edit** changes the pair.
- **Mixed Doubles** – as doubles, with the male and the female player; a pair must have one of each.
- **Teams** – Team Name and **Total Player** columns; **Add** opens the team panel; **Singles** / **Team-up** tabs; team size and bifurcation rules apply; **Current Average Seeding Criteria** in Auto Seed.
- All types: search, sort, Back No., seeding, Unpaid Players, Queue, Deleted, Transfer, Recreate, Merge, Sub Category, Settings, Import (with a template per type), Export, Forfeit, Delete.

## Players page: what the server does for each button

- List and badges: `register/v1/get_event_participants`, `get_participant_counts`.
- **Add**: `register/v1/register_event_participants` (teams first `team/v1/create_team`); **Edit**: `register/v1/update_event_participant`; temporary players: `user/v1/create_temporary_user_role`.
- **Delete**, **Add to Queue**, queue **Add to List**, **Forfeit**: `register/v1/update_event_participant_status`; self-registered entries: `withdraw_self_registered_player`.
- **Unpaid Players → Add to List**: `register/v1/mark_participants_paid`. **Team-up**: `register/v1/create_team_up`.
- **Back No.**: `backnumbers/v1/auto_assign`, `manual_assign`, `reset`. Seeding: `register/v1/auto_seeding`, `update_seeding`, `reset_seeding`, `bulk_seeding`; **Sync Points** / **Sync**: `sync_ranking_points_to_participants`, `sync_event_seeding_metrics_to_participants`.
- **Settings**, **Sub Category**, **Reset Sub Category**: `event/v1/create_event_categories`. **Self**: `configure_category_registration_settings`.
- **Import**: `import_export/v1/import_player`. **Export**: `worker/export/participants`.

## Players page: toolbar buttons

With a category selected the toolbar shows:
- **Sync Points**, **Auto Seed** – seeding (see the seeding guide). A green tick on **Auto Seed** means the category is already seeded.
- **Unpaid Players** – players registered but not yet paid.
- **Sub Category** / **Sub Division** – split the category.
- **Add** – add players, pairs or teams. **Queue** – the queue list, with its count.
- **Settings** – entity, rank type and seeding settings of the category.
- **Export** and the import (upload) icon.
- After ticking participants: **Transfer**, **Recreate**, **Add to Queue**, **Delete**, **Delete & Refund**. **Merge** needs no ticking. With nothing ticked, **Deleted** opens the deleted list.
- **Recreate** is hidden when the category has sub categories.
- **Add** and **Settings** are greyed out when no category is selected or the **Registration** toggle of the category is off; **Queue** and **Deleted** when no category is selected; **Transfer** and **Recreate** until participants are ticked.

## Players page: permissions

- Changing participants needs **Edit** permission on **Player Screen**. Without it the server answers "Access Denied".
- **Settings**, **Sub Category** and **Reset Sub Category** also need **Edit** permission on **Edit Category**; the **Self** toggle also needs **Edit Registration Settings**.
- An expired sign-in gives "Unauthorized Access". Sign in again.
- Messages such as "Error loading players", "Error loading form data" or "Something went wrong" mean data could not be loaded or saved. Reload the page and try again.

## Frequently asked questions about the Players page

**What can I do on the Players page?** See and search the participants of each category, add players, pairs and teams, seed them, give back numbers, move them between categories, queue, forfeit or delete them, and import or export the list.

**Why is the Add button greyed out?** No category is selected, or the **Registration** toggle of the selected category is off. Turn it on on the event's **Registration** page. The registration dates do not matter here.

**Why is the Settings button greyed out?** Same reason as **Add**: select a category and turn on its **Registration** toggle.

**Why is a registered player not in the list?** Only accepted and paid entries are listed. Check **Unpaid Players**, **Queue** and **Deleted**, or wait until the registration is verified.

## Frequently asked questions about the Players page columns and lists

**What does "Participants remaining" mean?** How many participants still have no back number, out of all participants of the event.

**What is the difference between "In" and "Ex" points?** "In" points are generated by the internal platform, "Ex" points by an external platform.

**What does the red mark next to a player mean?** The participant has been forfeited.

**Why can I not edit a singles player?** Only temporary players can be edited on this page; registered players keep their profile data.

**Why does the Club or Member Association column not appear?** Choose **Club**, **Member Association** or **Both** under **Select Organisation** in the category's **Settings** and save. Each category and sub category has its own setting.

**Why do I see Singles and Team-up tabs?** The category is doubles, mixed doubles or teams: **Singles** lists players who registered alone, **Team-up** the formed entries.
