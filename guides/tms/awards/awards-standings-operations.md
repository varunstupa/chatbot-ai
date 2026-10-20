---
doc_id: tms.awards.standings-operations
title: Awards and Standings – publishing stage and cumulative standings, swaps, manual standings, reset, automatic recalculation and export
routes:
  - tms/awards/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - publish stage standing
  - publish cumulative standing
  - publish toggle standings
  - cumulative swap
  - swap cumulative standing
  - manual standing
  - edit cumulative standing
  - edit final standing
  - reset standings
  - reset stage standing
  - standings recalculated after score
  - standings overwritten
  - export standings
  - export awards
  - swap stage standing
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What happens when I turn on the Publish toggle of a stage standing?
  - What is the difference between publishing the stage standing and the cumulative standing?
  - How do I swap two places in the final standing?
  - How do I set a participant's cumulative standing by hand?
  - Why did my manual cumulative standing change after a score was saved?
  - What does Reset do to the standings?
  - How do I export the standings?
  - Which standings are shown to the public?
backend_sources:
  - gateway/src/routers/standings_router.py (publish, reset, cumulative_swap, manual_standing, swap)
  - tms/src/router/standings_router.py
  - tms/src/service/standings_service.py (publish_standings, reset_standings, swap_stage_positions, swap_cumulative_standings, set_manual_standings, auto_generate_and_publish_standings)
  - tms/src/utils/scoring/phases/finalize.py (standings refresh after scoring)
  - tms/src/crud/standings_crud.py
  - gateway/src/routers/worker_router.py (export/fixtures)
source_files:
  - src/app/modules/tms/award-standings/award-standings.component.ts
  - src/app/modules/tms/award-standings/award-standings.component.html
  - src/app/modules/tms/award-standings/components/award-standings-order-of-merit-tab
  - src/app/core/services/common-service/common-service.service.ts
  - src/app/core/constants/api-constant.ts
  - src/app/shared/export-sidebar/export-sidebar.component.ts
---
# Awards and Standings – publishing, swaps, manual standings, reset, recalculation and export

This guide covers the operations on the standings of one category: publishing the stage and cumulative standings, changing positions by hand, resetting, the automatic recalculation after each score, and exporting. The page itself is in the Awards and Standings guide; the award types are in the award types guide; the API rules are in the awards API guide and the operations API guide.

## Publish the stage standing

- The **Publish** toggle of the final standing publishes the standing of the chosen stage.
- Switching on sends the publish request for that stage. Switching off unpublishes it.
- The success message is "Standings Published". If the request fails the toggle goes back to its old position and the server's message is shown.
- The publish request checks that the event, the category and the stage exist ("No Event Found", "No Category Found", "Stage Not Found"). It does not check that the standing has been generated.
- Publishing a stage standing also sends a standings-generated notice for the stage (for the public side) when the request carries the tenant. Unpublishing does not send it.

## Publish the cumulative standing

- The **Publish** toggle of the cumulative standing publishes the category-level standing.
- The same checks and messages apply. The public listing of the category uses this category-level toggle (see Public views below).
- Stage-level and category-level togglees are saved separately. Turning on the stage toggle does not change the category toggle.

## Swap two positions

- **Final standing (stage)**: choose a row in the **Participants List** and press **Swap**. The two stage participants trade positions.
  - A participant that is not in the stage: "Stage Participant Not Found" (404).
  - Participants from different groups: "Swap Not Allowed" (400). The swap works only inside one group.
  - Success: "Standings Updated".
- **Cumulative standing**: the same dialog on the cumulative table. The swap is sent with the event participant IDs.
  - A participant that does not belong to this category: "Event Participant Not Found" (404).
  - Success: "Cumulative Standings Updated".

## Set a cumulative standing by hand

- Click the **Cumulative Standing** number of a row to edit it. Only digits are accepted and the number must be a whole number of at least 1.
- Press Enter or leave the box to save. Escape cancels. A number equal to the current one closes the box without a request.
- The request sets the standing of that one event participant. Success: "Manual Standings Updated". An unknown participant: "Event Participant Not Found" (404).
- Manual standings are overwritten by the automatic recalculation after the next finalized score (see below).

## Reset

- **Reset** on the final standing clears the stage standing of the chosen stage. It is not offered while the final standing data is shown.
- A reset of the cumulative standing clears the cumulative positions of the category.
- The reset of the category clears the stage standings and the cumulative positions of all stages.
- Success: "Standings Reset". Reset priority and reset prize settings have their own messages ("Stage Priority Reset", "Award Settings Reset").
- The page does not ask for confirmation before a reset.

## Automatic recalculation after a score

- Every finalized score in the category runs the standings refresh. The refresh:
  1. clears the stage standings and the cumulative positions of the whole category;
  2. regenerates the standing of every stage that is completed, and publishes each one;
  3. for a predefined fixture where every stage is complete, validates the cumulative priority, regenerates the cumulative standing and publishes it.
- Consequence: a position set by a manual swap or a manual cumulative edit is cleared by the next finalized score. A cumulative standing is only rebuilt when every stage is complete; before that, the cumulative positions stay cleared.
- Stage standings are rebuilt from the results when a stage is regenerated. Whether a manual stage swap survives that rebuild was not traced, so check the standing after a regeneration.
- This is what the code does; a live check against an event with data was not made.

## Export

- **Export** on the page opens the export sidebar. Pick the export format and the categories, then export.
- The categories are the event categories of the page, with sub categories shown in brackets.
- For a team category the export also takes the singles and doubles options and the horizontal or vertical layout. Doubles categories take the layout options.
- The request is the fixtures export job of the worker service. The worker code is not in the repos, so the file contents are not described here.
- Success: the message of the export (shown in a snackbar); the sidebar closes.

## Public views

- The public award list and the public award standings are read through the OTT route `ott/v1/awards/standings`. It is open without a login and cached for 60 seconds.
  - Without an award ID it returns the published awards of the type (name and row count only).
  - With an award ID it returns the published standing rows, filtered by name and paged.
  - An award that is not published, or missing: "Published standings not found" (404).
- The participant listing used by the public (for example the standings of a category) returns "Standings Not Published" (200, with no participants) when the category toggle is off.
- The player dashboards read the category publish toggle as well, so a player sees a standing only after it is published.
- The public pages themselves are not in the repos; their layout is not described here.

## Permissions

- Publishing, swapping, editing, resetting and exporting need the edit permission of the event. The server refuses the change without it.

## Frequently asked questions

**What happens when I turn on Publish for a stage standing?** The stage standing becomes public for that stage. A notice for the stage is also sent to the public side.

**Is publishing the cumulative standing the same as publishing the stage?** No. Each has its own toggle, and the public category listing uses the cumulative (category) toggle.

**Why did my manual cumulative position change after a score was saved?** The next finalized score rebuilds the category standings (see Automatic recalculation). Set the positions again after the last score, or after the stage is complete.

**How do I swap two places?** Use **Swap** in the participants dialog. For the final standing the two players must be in the same group.

**Can I reset everything?** Use the reset of the category; it clears the stage and cumulative standings. Rebuild them with Generate.

**How do I export?** Click **Export**, choose the format and categories, then export. The file is produced by the export job.
