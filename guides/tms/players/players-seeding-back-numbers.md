---
doc_id: tms.players.seeding-back-numbers
title: Players page – seeding and back numbers
routes:
  - tms/players/:event_id
aliases:
  - auto seed
  - manual seed
  - seed range
  - back number
  - back numbers
  - bulk seeding
  - sync points
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I seed the players of a category?
  - How do I seed manually?
  - Why can I not change the seeds?
  - How do I assign back numbers?
  - Why does it say Back No Duplicate?
  - How do I seed all categories at once?
backend_sources:
  - gateway/src/routers/seeding_router.py (auto_seeding, update_seeding, reset_seeding, bulk_seeding, sync_event_seeding_metrics_to_participants)
  - gateway/src/routers/registration_router.py (sync_ranking_points_to_participants)
  - tms/src/service/registration_service.py (update_seeding, reset_seeding, auto_seeding, bulk_seeding)
  - tms/src/service/back_number_service.py
source_files:
  - src/app/modules/tms/players/players.component.ts
  - src/app/modules/tms/players/seeding-method-dialog/seeding-method-dialog.component.html
  - src/app/modules/tms/players/bulk-seeding-dialog/bulk-seeding-dialog.component.html
  - src/assets/json-data/auto_seed_list.json
  - src/assets/json-data/back_no_data.json
---
# Players page – seeding and back numbers

This guide explains seeding (giving the best participants seed positions for the draw) and back numbers (bib numbers) on the **Players** page.

## Auto Seed: seeding one category

1. Select the category and click **Auto Seed**.
2. **Seeding Method** → **SELECT METHOD**: **Points** ("higher points receive the higher seed") or **Rank** ("lower rank receives the higher seed"). Click **Next**.
3. The **Auto-seed settings** window shows **Applied Seeding Configuration** – **Method** (Internal Points or External Points) and **Mode**. "Contact your administrator to change the method." – the method is set in the organisation's seeding configuration.
4. Choose a **Seed Range**: 1-4, 1-8, 1-16, 1-32, 1-64, 1-128, 1-256 or 1-512. The top participants get seeds at once.
5. Click **Save**: "Seed Update Success".

- When the category allows both criteria, **Select Seeding Criteria** (Points or Rank) is shown above the list. The refresh icon reloads the list.

## Manual seeding and reset

- In the **Auto-seed settings** window click **Manually seed**. Each row then has a seed dropdown; pick the seed for each participant and click **Save**.
- The dropdown offers the seeds of the chosen **Seed Range** that are not yet given to another participant. Choose a **Seed Range** first.
- **Reset** removes all seeds of the category: "Seed Reset Success".
- Errors:
  - "Duplicate Seed" – two participants got the same seed.
  - "Seed values are already assigned for this event category" – the seed is already taken by another participant.
  - "Cant Update Seed" – the draw (fixture) of the category is already created; seeds can no longer be changed or reset.

## Average seeding criteria for teams

- For team categories the window shows **Current Average Seeding Criteria** – "Number of top participants whose points are averaged for seeding."
- Click **Edit** and choose a number from 1 to 12 ("Select from the options"). The seeds are recalculated at once. "Changing the average seeding criteria will recalculate the seeds."
- It cannot be changed in manual seeding mode.

## Seeding all categories at once

1. Click **Seeding** in the page header.
2. **Select Category** (participant type: singles, doubles, mixed doubles or teams), choose **Internal Points-Rank** ("choose between points and rank") or **External Points-Rank** ("use external points"), for internal also **Points** or **Rank**, and a **Seeding Range**. Click **Next**.
3. "Seeding in progress" is shown, then the **Execution Summary Report** with **Category**, **Status** and **Participant Seeds** per category. Click **Okay**.

- Categories whose draw is already created are skipped; the summary shows their status.
- "Seeding failed" – the bulk seeding could not run; nothing was changed.
- To remove seeds, use **Auto Seed** → **Manually seed** → **Reset** in each category.

## Display seed (organisation setting)

When **Display Seed** is turned on in the organisation's seeding configuration, every participant has two seeds:
- **System Seeding** – the seed calculated by Auto Seed.
- **Seeding** – the display seed, which can differ from the system seed.

The player list's **Seed** column then shows the display seed. In the **Auto-seed settings** window both columns are shown; with **Manually seed** you can set both per participant. Sorting by **Seed** uses the display seed.

## Sync and Sync Points

- **Sync Points** (category toolbar) copies the latest ranking points to the participants of the category: "Points synced successfully".
- **Sync** (page header) refreshes the seeding metrics of all participants of the event: "Sync successful" or "Sync failed".
- Use them before seeding when rankings have changed.

## Back numbers

Click **Back No.** in the page header. The **Back No Settings** window lists the participants (**S.No**, **Participant name**, back number, member association, club).

- **Specify the no to start from**: choose 1, 100, 500 or 1000. Numbers are given at once in sequence: "Backno Auto Success".
- Only accepted, paid, active participants who are not in the queue get numbers.
- Back numbers belong to the person for the whole event, not per category.
- To set numbers by hand, type them in the boxes and click **Save**: "Backno Manual Success".
- **Reset** removes all back numbers of the event.
- "N New players found" means N participants still have no back number.

## Back number errors

- "Back No Duplicate" – the same number was typed twice.
- A conflict message when a number is already used by another participant of the event.
- "No Event Found" – the event no longer exists.

## Frequently asked questions about seeding and back numbers

**How do I seed the players of a category?** **Auto Seed** → choose **Points** or **Rank** → **Next** → choose a **Seed Range** → **Save**.

**How do I seed manually?** **Auto Seed** → **Next** → **Manually seed**, choose the seeds, **Save**.

**Why can I not change the seeds ("Cant Update Seed")?** The draw of the category is already created.

**Who gets the higher seed with Rank?** The lower (better) rank.

**Can I change the seeding method (internal or external)?** No, contact your administrator; it is set in the organisation's seeding configuration.

**How do I assign back numbers?** **Back No.** → choose the start number, or type numbers and click **Save**.

**Why does a player have no back number?** They are unpaid, queued, not accepted, or registered after numbers were given – choose the start number again.

**Are back numbers per category?** No, one back number per person for the whole event.

**Why does it say Back No Duplicate?** The same back number was typed twice. Give each participant a different number; one back number is used per person for the whole event.

**How do I seed all categories at once?** Click **Seeding** in the page header, choose the participant type, **Internal Points-Rank** or **External Points-Rank** (for internal also **Points** or **Rank**) and a **Seeding Range**, then **Next**. The **Execution Summary Report** shows the result per category; categories whose draw already exists are skipped.
