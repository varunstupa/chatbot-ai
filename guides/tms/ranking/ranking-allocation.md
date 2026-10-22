---
doc_id: tms.ranking.allocation
title: Ranking and rating allocation – stages, award and standing, the report, edit sidebar, publishing and new players
routes:
  - tms/ranking/:param1/:param2/:event_id
aliases:
  - ranking allocation
  - point allocation
  - points allocation stages
  - allocate points by stage
  - award and standing ranking
  - award and standing configuration
  - ranking report
  - rating report
  - generate ranking report
  - recalculate report
  - publish report
  - publish ranking list
  - edit ranking points
  - penalty points
  - victory points
  - bonus points
  - point exchange
  - new players rating
  - initial points new player
  - qualifier position
  - winning prize ranking
  - define points
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I allocate ranking points by stage?
  - What is Award and Standing in the ranking module?
  - How do I add a qualifier to a stage?
  - What does Recalculate report do?
  - How do I publish the report?
  - Why can I not edit the points after publishing?
  - What is the Point Exchange in a rating?
  - How do I set the initial points of a new player?
  - What is the penalty point and where do I add it?
  - What does the Award and Standing Configuration popup ask for?
backend_sources:
  - gateway/src/routers/ranking_config_router.py (event-category-config, tenant settings)
  - gateway/src/routers/award_standing_config_router.py (event/category award and standing config)
  - gateway/src/routers/ranking_router.py (lists, compute, publish, standings, adjustments)
  - gateway/src/routers/ranking_router_v2.py
  - gateway/src/routers/combined_report_router.py (combined lists, report, publish)
  - gateway/src/routers/rating_config_router.py (rating settings, point exchange)
  - gateway/src/routers/elo_rating_router.py
  - tms/src/router/section_router.py (event categories)
source_files:
  - src/app/modules/tms/ranking-allocation/ranking-allocation.component.html
  - src/app/modules/tms/ranking-allocation/stages/stages.component.html
  - src/app/modules/tms/ranking-allocation/stages/stages.component.ts
  - src/app/modules/tms/ranking-allocation/award-and-standing/award-and-standing.component.html
  - src/app/modules/tms/ranking-allocation/award-and-standing/award-and-standing.component.ts
  - src/app/modules/tms/ranking-allocation/award-and-standing/filter-sidebar/filter-sidebar.component.html
  - src/app/modules/tms/ranking-allocation/edit-sidebar/edit-sidebar.component.html
  - src/app/modules/tms/ranking-allocation/generate-ranking-points/generate-ranking-points.component.html
  - src/app/modules/tms/ranking-allocation/popup/popup.component.html
  - src/app/core/services/ranking-rating/point-allocation/ranking-management.service.ts
  - src/app/core/services/ranking-rating/award-and-standing/award-and-standing.service.ts
---
# Ranking and rating allocation

The allocation pages decide how many points (ranking) or how much rating change (rating) each player gets for a result. They are opened from the Ranking Management page (see the ranking guide). There are two ways to allocate points:

- **Stages** – points by the stage a player reached (group stage, quarter-final and so on). The stages page is used for both ranking and rating. The **Edit point allocation** button is shown for ranking in categories that are not team categories.
- **Award and Standing** – points by the final position of the player in the event standing.

The home of the allocation is the page **Ranking Management** with the choice "Stages" or "Award and Standing". On the combined "Rating + Ranking" system, the Stages choice is not available: the page shows the note "This Settings is not available in Ranking and Rating combination."

## Stages page

- Header: the system name ("Ranking" or "Rating") and the steps **Step** and **Stages**. The category and sub category (or sub division) chips above the table choose the category; the arrows scroll the chips.
- For ranking, **Edit point allocation** opens the point allocation sidebar. For team categories the button is not shown.
- Two tabs: **Points Allocation** and **View Report**.

### Points Allocation tab

- One row per stage. The columns are **Stage**, **Points**, and when prize amounts are on, **Winning Prize**.
- For a group stage (format 1) an **Add Qualifier** button adds a row for each qualifier position: its label (for example "Qualifier Position"), its points and its prize amount.
- **Bonus points** – a set of **Match Points** results, each with a points box that is given for that result.
- **Winning Prize** – a toggle that turns the prize amount column on or off.
- The points boxes accept zero or more.
- **Define Points** (shown when the category has no stages yet) opens the setup. "No stages configured for {category}." and "Set up point allocation to finalize your reward configuration" are shown until the stages are set up.
- **Reset** (when the configuration is saved and published) or **Edit** (to change it) togglees between editing and locked states. A published configuration is read only until it is edited again.
- Saving: "Point allocation saved successfully!". Saving without a stage: "Please select a stage to save points.".

## Stages page – View Report tab

- Shows the report of the stage points: the ranking or rating list of the category.
- Columns: **S.No**, **Name**, the Club or Member Association (by the parent role), the stage scores (**S1**, **S2** ...) and **Total Points**. For doubles and mixed doubles, each member's points are shown.
- For rating the columns are **Club/MA**, **Rating Points** (with the penalty and the bonus), and the total. For the combined system the columns are **Elo Points** and **Bonus points**.
- **Search** – "Search by Name" filters the rows.
- **Filter** – opens the filter sidebar (categories, stages and other filters of the report).
- **Export** – downloads the list ("Export initiated." then the file, or "Export failed.").
- **Recalculate report** – recalculates the report from the current results. A confirmation is shown.
- **Publish** – see Publishing below.
- Hovering a row shows the edit action. The edit sidebar opens for the player (see Edit sidebar).
- A message while the report is being prepared: "Generation of Ranking report is in progress. Please come back later...". "Please select a category to view the report." when no category is chosen. "Season information is missing. Cannot generate report." when the season is not set.

## Award and Standing

- Shown as a card on the allocation page ("Allocate points based on the final position received, linked to event standing").
- Categories and sub categories are chosen as in the Stages page. Once every match of the category is complete, the note says to go to the report tab to generate the ratings.
- **Positions** table: the positions with a label each. The value column depends on the award mode:
  - **Percentage** – the share of the prize pool or points for the position (0 to 100). A value above 100 is refused: "Can't enter greater than 100%". A value that is out of order (a lower position with a higher share) only shows a warning and does not block publishing.
  - **Ranking Points** or **Final points** – the points for the position. Final points are used for the combined system.
- **Winning Prize** – a toggle. When on, each position has a **prize amount** box.
- **Publish** – saves the configuration for the selected categories (see Publishing below). "Published Successfully" on success; "Error saving award standing configs" on failure. With a percentage error, publishing is refused: "Please fix percentage errors before publishing. No row may exceed 100%."
- The combined system shows the calculation: "Rating: {point selection} Calculation", "Event Factor" and "Category Percentage".

## Award and Standing configuration popup

- Opens from the award card. It asks for:
  - **Ranking points till which position?** – a dropdown of the position ranges (for example 17-32).
  - **Calculate positions upto** – a number of positions to calculate.
- **Save** stores the choice for the category ("ranking_points_till_position" and "calculate_positions_upto"). Missing values: "Please fill all required fields". **Reset** clears the form. The popup text "Edit participants in each match as per your choice" describes its purpose.

## Edit sidebar (per player)

- Opened from a player row of the report. The title is "Edit" followed by the system (Ranking, Rating or Ranking/Rating for the combined view).
- **Stage blocks** – each stage shows its points and the tournament weight (x weight). The total of the stage is shown in points.
- **Add Penalty** – adds a penalty for a stage. A penalty is entered as a negative number ("-0" placeholder). "No penalty changes to save." when nothing changed.
- **Based on Position** – the bonus points from the final position.
- **Rating Points** (rating) with **Total Rating Points**; **Bonus points** and **Total Points** (ranking).
- **Undo Changes** and **Save Changes**. "Changes undone" after undo; "Ranking changes saved successfully" or "Rating changes saved successfully" after save.
- **International player** – a player from outside the tenant. The sidebar shows the international player figures and its own **Undo** and **Save**. "International player data not found" when the data is missing.

## Edit sidebar – victory points and point exchange

- **Victory Points** (VP) and **Bonus Points** (BP) for each match – the table lists the match, its date, its score and its position, with a VP box and a BP box (BP is not shown for an award and standing). **Victory Points Total** and **Bonus Points Total** are shown in points. "No VP or BP changes to save." when nothing changed; "Victory and bonus points saved successfully" on save.
- **Point Exchange** (rating) – the rating change of each match: the opponent, the result, the rating before and after, and the change (shown green or red).

## Generate report

- The report generation page is the same report as the View Report tab, opened for the chosen category.
- **Generate Report** starts a new report from the selected configuration. "Generate report from your selected configurations" is shown before the first run. "We couldn't find anything for your search" when a search has no rows.
- Each row can be edited (the edit icon on hover) and the members of a pair can be edited separately.

## New players (rating)

- When a rating report would include players who have no rating, the **New Players Detected** dialog opens. It lists the player name, ID, matches, wins and losses, the recent match details (the opponent and its rating) and an **Initial Points** box.
- **Calculate** saves the initial points and continues. Each new player needs points above zero: "Player must have valid initial points (> 0)."
- **Skip** opens a confirmation ("Confirm Skip!"). Skipped players are left out of this rating generation.
- "Failed to save new player points. Please try again." when the points cannot be saved.

## Recalculate and publish

- **Recalculate report** asks for confirmation, then starts the recalculation for the category. The screen does not offer recalculation of a published rating list and shows "Cannot recalculate a published rating list." instead. "Failed to trigger ranking recalculation." or "Failed to trigger rating recalculation." is shown when the request fails.
## Publish report

- **Publish report** opens the confirmation "Publishing the report will make it official." with **Cancel** and **Proceed**. Publishing is a two-step lifecycle on the server (see the publication guide): the list is first **validated** (from calculated or edited), and only then **published**.
  - Ranking: **Proceed** submits the list for publication, which makes it validated. The list goes live when the publication run promotes it, either on its schedule or after a manual trigger. "No report generated yet to publish." when there is nothing to submit. "Error publishing Ranking List." on failure.
  - Rating: **Proceed** validates the list; the publish step then puts the validated list on the rating board at once and builds a new leaderboard snapshot. "Rating List published successfully" on success.
- A published report is locked on the allocation screen (its inputs are disabled). Its points change again only through a new calculation.
- For the combined system a computation is triggered first. The failure message "Failed to trigger ranking and rating computation." is shown when it fails. The message for a successful start has no English translation in the file, so the screen may show the raw key.

## Filter sidebar

- The **Filter** sidebar narrows the report rows by the filters the report offers (the category, stage and other report filters). "Report component not ready for filtering." appears when the report has not loaded yet.

## Permissions

- Saving points, publishing and recalculating need the ranking permission (Edit). Reading the report needs the login. The server refuses changes without the permission.

## Frequently asked questions

**How do I allocate ranking points by stage?** Open the category from the Ranking page, choose **Stages**, click **Define Points** or edit the stage rows, set the points and the qualifiers, then click **Save**.

**What is Award and Standing?** An allocation that gives points by the final position of each player in the event standing, optionally with a prize for each position.

**How do I add a qualifier?** Click **Add Qualifier** on the Points Allocation tab (group stages), then fill in its label and points.

**What does Recalculate report do?** It recalculates the points of every player from the current results. It does not publish the report.

**How do I publish?** Click **Publish report**, read the confirmation, then **Proceed**. The list is validated first. For ranking, it then goes live when the publication run promotes it; for rating, the publish step puts it on the rating board straight away. See the publication guide.

**Why can I not edit the points after publishing?** A published configuration is locked. Use **Edit** to unlock it, change the points and publish again.

**What is the Point Exchange?** For a rating, the change in rating for each match, showing the rating before and after.

**How do I set the initial points of a new player?** In the New Players Detected dialog, type the initial points in each row and click **Calculate**, or click **Skip** to leave them out.

**What is the penalty point and where do I add it?** A penalty lowers a player's points for a stage. In the report, open the player's **Edit** sidebar, click **Add Penalty** on the stage and enter it as a negative number, then **Save Changes**.

**What does the Award and Standing Configuration popup ask for?** **Ranking points till which position?** (a position range, for example 17-32) and **Calculate positions upto** (how many positions to calculate). **Save** stores them for the category.
