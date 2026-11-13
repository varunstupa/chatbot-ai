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
  - gateway/src/routers/awards_router.py (awards/v1 endpoints)
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
  - src/app/modules/tms/award-standings/best-player/components/best-player-tms-positions-view/best-player-tms-positions-view.component.html
  - src/app/modules/tms/award-standings/best-player/components/best-player-tms-award-card/best-player-tms-award-card.component.html
  - src/app/modules/tms/award-standings/shared/constants/award-standings-confirm-dialog.constants.ts
  - src/app/core/constants/api-constant.ts
  - src/assets/i18n/en.json
---
# Awards and Standings page

The **Awards and Standings** page (route `tms/awards/...`) builds the standings of an event's stages and categories, sets the prize money of each position, and manages the **Best Player** and **Order of Merit** awards of the event. The example URL `tms/awards/0/169/1358/4869/0` means: participant type 0 (all), category 169, event 1358, event category 4869, stage 0. Leaderboards are used for league events in place of standings.

The award types and their rules are in the award types guide (awards-award-types). The server calls are in the awards API guide (awards-api).

## Where to find the Awards and Standings page

Open **Awards and Standing** from the sidebar. Without an event the page shows "No record found" with a hint to create an event; with an event that has no categories it asks you to add categories, and **Go to Event** opens the event setup.

## Awards and Standings page: header and top bar

- Title: **Awards & Standings**.
- **Notify Users** – shown only when the organisation has the notify feature switched on, the event has categories, and a notification for "standings generated" is set up for the event. It opens the confirmation **Notify Users** – "Do you want to proceed with sending notifications for the created and published fixtures?" – with **Yes, Send**. A result window then shows success or the error (with a retry); a quota window appears when the sending limit is reached.
- **Export** – opens the export of the page's standings and awards.
- The participant type dropdown (**All** and the types of the event) and the category tabs choose the category. A category with sub categories shows their number in brackets and, when selected, a second row of tabs labelled **Sub Division** (league) or **Sub Category**.
- The participant type dropdown is greyed out for league events and while the **Best Player** or **Order of Merit** tab is open.

## Awards and Standings page: tabs

- **Standings** (**Leaderboard** for a league) – the standings of the chosen category.
- **Best Player** and **Order of Merit** – the award tabs. Each appears only when the award type is available for the event (switched on for the organisation). On these tabs the stage row is hidden and **Create Awards** (and **Sync Awards**) are shown above the list.

## Standings tab: stages, Final Standing and Cumulative Standing

- Under the category tabs the stage tiles (**S1**, **S2** … with the stage name) choose the stage whose standing is shown.
- A **Final Standing** tile appears after the stages for the final standing have been chosen in the **Cumulative Standing** panel. Click it to see the final (cumulative) standing of the category.
- The **Cumulative Standing** button on the right opens the panel where the stages are chosen and ordered (see below).
- When positions are set, a podium with the top three is shown above the table, with each player's profile photo (or a default male or female picture); the arrow expands or collapses it. The podium is hidden when two participants share 1st or 2nd place.
- **Search** filters the table by participant name; "No results found" when nothing matches.

## Standings tab: stage standing table

With a stage tile selected:
- Columns: **S.No**, **Position**, **Participant name**, **Member Association** and/or **Club** (as chosen under **Select Organisation** in the category's **Settings** on the Players page), **Total Points** and, when prize money is on, **Prize Money**.
- "No standings declared" appears when the stage has no participants with standings (also in the **Final Standing** view when no one has a final position).
- **Generate stage standing** – shown while some participants have no standing yet; it builds the standing from the results ("Stage Standings Generated"). Only a completed stage can be generated: otherwise "Cant Generate Standings". A stage that already has a standing: "Standings Already Generated" (click **Reset** first).
- **Reset** – clears the stage standing ("Standings Reset"). There is no confirmation.
- **Publish** – a toggle that publishes the stage standing ("Standings Published"). The server does not check that the standing was generated.
- The swap icon on a row opens the **Participants List** dialog: choose the other row, then **Swap** (greyed out until a row is chosen). The two participants trade positions ("Standings Updated"). Both must be in the same group: otherwise "Swap Not Allowed".

## Standings tab: Final Standing table

With the **Final Standing** tile selected:
- Columns: **Position**, **Participant name**, **Member Association** and/or **Club**, **Total Points** and, when prize money is on, **Prize Money**. Only participants with a final position are listed.
- Click a **Position** number to change it in place: digits only (up to 4), a whole number of 1 or more; Enter or leaving the box saves it, Escape cancels.
- The swap icon on a row opens the **Participants List** dialog with **Swap**, as for stages.
- **Publish** – a toggle that publishes the final standing of the category.
- **Settings** (above the table) opens the prize money panel. It is only offered in this view.

## Cumulative Standing panel: choosing stages

- Click **Cumulative Standing**. The panel shows the participant type and category and the note "You can select your final standings by combining the results from multiple stages to create a cumulative standing. Additionally, you have the option to assign priority to specific results."
- The stages are listed with a tick box each. Tick the stages that count and drag them into priority order; a new order is saved at once.
- **Generate** saves the ticked stages and their order ("Stage Priority Updated"), then builds the final standing ("Cumulative Standings Generated"). It is greyed out until a stage is ticked.
- Each ticked stage needs a generated stage standing; otherwise: "Standings for stage(s) {stage_ids} have not been generated yet. Please generate them or remove them from cumulative standings priority and then regenerate."
- An existing final standing is not rebuilt: "Cumulative Standings Already Generated". Click **Reset** first.
- **Reset** clears the saved stage priority ("Stage Priority Reset") and the final positions of the category ("Standings Reset").
- After stages are saved, the **Final Standing** tile appears in the stage row.

## Settings panel: prize money

- Open **Settings** from the **Final Standing** view.
- **Enable Prize money** switches the **Prize Money** column on or off.
- When it is on, **Set awarding preferences** lists each **Standing** with a **Price** box. When nothing has been saved yet, one row per final position is created with price 0.
- **Save** saves the prize table ("Award Settings Updated"); **Reset** clears it and switches **Enable Prize money** off ("Award Settings Reset").
- A position without a price shows "--" in the **Prize Money** column.
- Publishing a standing also records whether prize money is on at that moment, for the public view.

## Best Player and Order of Merit tabs: award list

- The tab lists the event's awards as cards with the award name and a **Published** badge once its standing is published. Each card has **View** (read only) and an edit (pencil) button; clicking the card opens the award's positions.
- **Search** filters the cards by name; "No records found" when nothing matches. More cards load as you scroll.
- With no awards yet: "Start by adding or editing awards created by the admin. Alternatively, you can create new awards by clicking on 'Create Awards'." with a **Sync Awards** button.
- **Create Awards** opens the create award panel (see the award types guide). **Sync Awards** above the list appears once the event has awards.
- Editing an award from its card keeps **Award Name** and the categories read only; only the points (and weightages, tie breakers) can be changed.

## Best Player and Order of Merit tabs: positions, publish and un-publish

Click an award card to open its positions. The award names are shown as tabs at the top, with a back arrow to the list.
- **Generate Positions** – shown before the award has a standing; it builds the standing from the results.
- The table shows **Position**, **Participant Name**, **Club**, **Member Association**, **Total Points** (and **Prize Money** when on), 50 rows per page, with **Search**.
- **Regenerate Positions** – rebuilds the standing. It asks "Are you sure you want to Re-generate?" – "All the order would be changed accordingly."
- **Publish** (this award) and **Publish All** (all awards of this type in the event) – shown while the standing is not published. They ask "Are you sure you want to publish?" – "You are about to publish the generated awards." Success: "Award published successfully."
- **Un-publish** – shown once published. It asks "Are you sure you want to un-publish?" Success: "Award unpublished successfully."
- Each confirmation has **Confirm**; failures show the server's message or "Failed to publish the award." / "Failed to unpublish the award."

## Best Player and Order of Merit tabs: server rules for positions and publishing

- **Generate Positions** and **Regenerate Positions** work the positions out from the award's current points and the latest results. Editing an award does not change its positions until you regenerate.
- Every player gets their own position. Players with equal points are ordered by the tie-breakers; if they are still equal, the server orders them in a fixed internal order, so positions are never shared.
- Regenerating keeps the publish state: a published award shows the new positions publicly at once.
- Award categories that are not in this event are skipped. If none of them is in the event: "None of the award's categories exist in this event. Please update the award categories or sync a matching award."
- **Publish** needs generated positions ("Generate standings before publishing") and at least one award category with a final standing ("Cannot publish: mapped categories have no finalized results"). **Un-publish** is always allowed.
- **Publish All** publishes only the awards that have generated positions and a category with a final standing; the others are skipped without a message.

## Sync Awards panel

- **Sync Awards** opens a panel that lists the **global** awards (set up by the organisation for all events) that can be added to this event: "Select the awards you wish to populate in the list".
- Tick the awards and press **Add** (or **Cancel**). Awards already synced, and awards not yet published at the federation, are skipped by the server.
- The view and edit icons on a global award open it read only or for changes.
- A synced award is a copy: later changes to the global award are not copied into the event, and syncing it again is skipped.
- When the award type is switched off for the organisation: "This award type is disabled at federation level".
- A failed sync shows the server's message or "Failed to sync awards to this event."

## Awards and Standings page: messages

- "Standings not generated yet" – the award's positions are requested before they are generated.
- "Generate standings before publishing" – publish needs generated positions.
- "Cannot publish: mapped categories have no finalized results" – no category of the award has a final standing yet.
- "Cant Generate Standings" – the stage is not completed yet.
- "Standings Already Generated" – the stage already has a standing; reset it first.
- "Cumulative Standings Already Generated" – the final standing exists; click **Reset** in the **Cumulative Standing** panel first.
- "Stage Priority Not Found" – no stages are saved for the cumulative standing.
- "Swap Not Allowed" – the two stage participants are in different groups.
- "Award name '{name}' already exists in this event" – the award name is taken.
- "This award type is disabled at federation level" – the type cannot be used for this event.
- "Award not found" – the award no longer exists.
- Errors without a message show "Something went wrong".

## Awards and Standings page: success messages

- "Stage Standings Generated", "Standings Updated", "Standings Published", "Standings Reset", "Stage Priority Updated", "Stage Priority Reset", "Award Settings Updated", "Award Settings Reset", "Cumulative Standings Generated", "Cumulative Standings Updated", "Manual Standings Updated".

## Awards and Standings page: permissions

- Every change on this page (generating, publishing, swapping, resetting, stage priority, prize money, creating, editing, syncing and deleting awards) needs the **Edit** permission of the Awards and Standings feature. The server refuses the change without it.
- Viewing the event's awards and their positions needs the **Read** permission of that feature.

## Frequently asked questions about the Awards and Standings page

**What is the Awards and Standings page for?** It shows the standings of the event (stage standings and the **Final Standing**, or the **Leaderboard** for a league), sets the prize money, and holds the **Best Player** and **Order of Merit** awards of the event.

**How do I generate the stage standing?** Complete the stage, select its tile, then click **Generate stage standing**.

**What is the difference between final standing and cumulative standing?** They are the same result: the **Cumulative Standing** panel chooses and orders the stages, and **Generate** builds the category's final standing, shown under the **Final Standing** tile.

**How do I choose the stages for the cumulative standing?** Click **Cumulative Standing**, tick the stages and drag them into order, then click **Generate**. **Reset** clears the stage order.

**Why is there no Final Standing tile?** No stages have been chosen yet. Click **Cumulative Standing**, tick the stages and click **Generate**.

**How do I publish the standings?** Turn on the **Publish** toggle under the stage table or the **Final Standing** table. Generate the standing first.

## Frequently asked questions about the Awards and Standings page (continued)

**How do I set the prize money for each position?** Select **Final Standing**, click **Settings**, turn on **Enable Prize money**, enter the **Price** of each **Standing** and click **Save**.

**Why is there no Settings button?** **Settings** is only shown in the **Final Standing** view.

**How do I sync awards from the federation?** Open the **Best Player** or **Order of Merit** tab, click **Sync Awards**, tick the awards and press **Add**.

**How do I publish a Best Player or Order of Merit award?** Click the award card, click **Generate Positions**, then **Publish** (or **Publish All**) and **Confirm**.

**Why do I not see the Best Player or Order of Merit tab?** The award type is not available for this event; it must be switched on for the organisation.

**Why does the page say "Standings not generated yet"?** The standing was requested before it was generated. Generate it first (stage: **Generate stage standing**; award: **Generate Positions**).

## Frequently asked questions about the Awards and Standings page (server rules)

**Why does Generate say "Cumulative Standings Already Generated"?** The category already has a final standing. Click **Reset** in the **Cumulative Standing** panel, tick the stages again and click **Generate**.

**Why can I not publish a Best Player or Order of Merit award?** Generate its positions first, and at least one of its categories must have a final standing.

**I changed an award's points. Why did the positions not change?** Positions are only worked out when you click **Generate Positions** or **Regenerate Positions**. Regenerate after editing.

**Can two players share a Best Player or Order of Merit position?** No. Equal points are split by the tie-breakers, and then by a fixed internal order.
