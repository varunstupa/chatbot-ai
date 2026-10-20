---
doc_id: tms.awards
title: Awards and Standings page – stage and cumulative standings, prize money, Best Player and Order of Merit
routes:
  - tms/awards/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - awards and standings
  - awards page
  - standings page
  - stage standing
  - cumulative standing
  - final standing
  - generate stage standing
  - publish standings
  - prize money
  - enable prize money
  - awarding preferences
  - stage priority
  - leaderboard
  - sync awards
  - create awards
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Awards and Standings page for?
  - How do I generate the stage standing?
  - What is the difference between final standing and cumulative standing?
  - How do I publish the standings?
  - How do I set the prize money for each position?
  - How do I choose the stages for the cumulative standing?
  - How do I sync awards from the federation?
  - Why does the page say "Standings not generated yet"?
backend_sources:
  - gateway/src/routers/award_router.py (awards/v1 endpoints)
  - gateway/src/routers/award_standing_config_router.py (standings/v1 endpoints)
  - gateway/src/routers/standings_router.py (standings/v1 endpoints)
  - tms/src/router/award_router.py
  - tms/src/router/standings_router.py
  - tms/src/service/award_service.py
  - tms/src/service/standings_service.py
source_files:
  - src/app/modules/tms/award-standings/award-standings.component.html
  - src/app/modules/tms/award-standings/award-standings.component.ts
  - src/app/modules/tms/award-standings/components/award-standings-best-player-tab/award-standings-best-player-tab.component.ts
  - src/app/modules/tms/award-standings/components/award-standings-order-of-merit-tab/award-standings-order-of-merit-tab.component.ts
  - src/app/modules/tms/award-standings/components/award-standings-sync-awards-dialog
  - src/app/core/constants/api-constant.ts
  - src/assets/i18n/en.json
---
# Awards and Standings page

The **Awards and Standings** page (route `tms/awards/...`) builds the standings of an event's stages and categories, sets the prize money of each position, and manages the **Best Player** and **Order of Merit** awards. The example URL `tms/awards/0/169/1358/4869/0` means: participant type 0 (all), category 169, event 1358, event category 4869, stage 0. Leaderboards are used for league events in place of standings.

The award types and their rules are in the award types guide (awards-award-types). The server calls are in the awards API guide (awards-api).

## Where to find it

Open **Awards and Standing** from the sidebar.

## Page header and top bar

- Title: **Awards & Standings**.
- **Notify Users** – shows only when the event allows notifying users. It opens the notify confirmation.
- **Export** – opens the export of the page's standings and awards.
- The category dropdown chooses the participant type and category. Each category chip shows its sub categories in brackets. Sub categories are labelled "Sub Division" for a league and "Sub Category" otherwise.
- Stage tiles (S1, S2 ...) choose the stage.

## Main sections

- **Standings** (**Leaderboard** for a league) – the standings table, with the two views **Final Standing** and **Cumulative Standing**.
- **Best Player** – the Best Player award hub.
- **Order of Merit** – the Order of Merit award hub.
- The action buttons **Create Awards**, **Sync Awards** and **Settings** sit above the award hubs.

## Final standing (stage standings)

- The table lists the participants of the stage: **S.No**, **Position**, **Participant name**, **Member Association**, **Club**, **Total Points** and, when prize money is on, **Prize Money**.
- "No standings declared" appears when the stage has no standings yet.
- **Generate stage standing** – shown while some participants have no standing yet; it builds the standing from the results. Only a completed stage can be generated.
- **Reset** – clears the stage standing. It is not shown while the final standing data is displayed.
- **Publish** – a toggle that publishes the stage standing to the public pages. A published standing is shown on the published standings of the event.
- A position can be swapped with the **Participants List** dialog: choose a row, then **Swap**.

## Cumulative standing

- The cumulative standing combines the results of several stages.
- **Set awarding preferences** opens a side panel:
  - the stages are listed in order (drag to re-order) with a tick box for each stage that counts;
  - **Generate** builds the cumulative standing from the chosen stages;
  - **Reset priority** clears the stage order.
- The cumulative table lists each participant with **Cumulative Standing** (click to edit it in place), **Points** and **Prize Money**.
- **Publish** (cumulative) – a toggle that publishes the cumulative standing.
- Note on the page: the final standing can be built from the results of several stages.

## Prize money and settings

- **Settings** opens the side panel. **Enable Prize money** togglees the prize money columns on or off.
- The prize for each standing is set in the awarding preferences: the **Standing** and the **Price** (an amount per standing).
- **Save** saves the prize table; **Reset** clears it.

## Best Player and Order of Merit hubs

- Each hub has an **Enable** toggle. Turning a type on or off is saved for the tenant. "Enable Best Player" and "Enable Order of Merit" are the first screen when a type is off.
- **Create Award** opens the create award side panel (see the award types guide).
- Award cards list the awards with their categories and their status, and open for viewing or editing.
- "Start by creating awards for your designated categories, and then assign points for each position." (Best Player) and "Start by creating awards ... and then assign points and weightage ..." (Order of Merit) are shown when there are no awards.
- A search box filters the awards by name; "No results" when nothing matches.

## Sync Awards

- **Sync Awards** opens a side panel that lists the **global** awards (federation awards) that can be added to this event.
- Tick the awards to add and press **Add**. Awards already synced, and awards not yet published at the federation, are skipped.
- **View** and **Edit** on a global award open it read only or for changes (where allowed).

## Messages

- "Standings not generated yet" – the standing is requested before it is generated.
- "Generate standings before publishing" – publish needs a generated standing.
- "Cannot publish: mapped categories have no finalized results" – the categories of the award have no final results.
- "Cant Generate Standings" – the stage is not completed yet.
- "Standings Already Generated" – the stage already has a standing.
- "Stage Standings Generated", "Standings Updated", "Stage Priority Updated", "Award Settings Updated", "Cumulative Standings Generated" – the success messages.
- "Award name '{name}' already exists in this event" – the award name is taken.
- "This award type is disabled at federation level" – the type cannot be used for this event.
- "Award not found" – the award no longer exists.
- Errors without a message show "Something went wrong".

## Permissions

- Changing standings, awards and settings needs the edit permission for the event. The server refuses changes without it.

## Frequently asked questions

**What is this page for?** Building the standings and prize money of the event's stages and categories, and managing the Best Player and Order of Merit awards.

**How do I generate the stage standing?** Complete the stage first, then click **Generate stage standing**.

**What is the cumulative standing?** A standing that combines the results of several stages, using the stage order and the stages you choose in the awarding preferences.

**How do I publish the standings?** Turn on the **Publish** toggle of the stage or the cumulative standing. Generate the standing before you publish.

**How do I set the prize money?** Turn on **Enable Prize money** in Settings, then enter the price for each standing in the awarding preferences.

**How do I sync awards from the federation?** Click **Sync Awards**, tick the awards, and press **Add**.
