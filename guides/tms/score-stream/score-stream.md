---
doc_id: tms.score-stream
title: Scoring and Streaming page – score matches, walkovers, streaming, lineups and print queue
routes:
  - tms/score-stream/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - score stream
  - scoring and streaming
  - scoring page
  - score matches
  - enter scores page
  - streaming page
  - stream settings
  - match id search
  - search by match id
  - scoring tab
  - scoring walkthrough
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What is the Scoring and Streaming page for?
  - How do I enter a score on this page?
  - How do I search a match by its match ID?
  - How do I enable streaming for a match?
  - What are the Stream Settings?
  - How do I filter the matches on this page?
  - Why is there no record on the Scoring and Streaming page?
  - How is the scoring different for each sport?
  - Why is the Update button disabled for a walkover?
  - Why can't I disable streaming after a match starts?
  - Why can't I save a team sub-match?
  - Why can't I see players in the lineup?
backend_sources:
  - gateway/src/routers/scoring_router.py (update_score)
  - gateway/src/routers/match_router.py (matches, update_match_status, sub-matches, reverse-participants-order)
  - gateway/src/routers/teams_router.py (fetch_lineup, update_lineup)
  - gateway/src/routers/rule_setting_router.py (get_rule_settings)
  - gateway/src/routers/playing_order_router.py (get_team_playing_order_with_matches bulk)
  - gateway/src/routers/planner_router.py (event official notes)
source_files:
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.html
  - src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts
  - src/app/modules/tms/score-and-streaming/manual-scoring-toggle-button
  - src/app/modules/tms/score-and-streaming/umpire-refree-notes
  - src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts
  - src/app/modules/tms/tms.module.ts
  - src/assets/i18n/en.json
---

# Scoring and Streaming page

## Scope and purpose

The **Scoring and Streaming** page is used to enter match results, record walkovers or disqualifications, manage manual scoring, enable streaming, manage team-match lineups and sub-matches, view umpire/referee notes, and prepare scoresheets for printing.

Route pattern: `tms/score-stream/:participant_id/:category_id/:event_id/:event_category_id/:stage_id`.

This is the same screen as the Scoring tab on the Fixtures and Results page, opened directly. The sport configured for the event determines how scores are entered and validated. Refer to the sport-specific guides for Table Tennis, Badminton, Padel, and Tennis.

### Route example

Example URL:

`tms/score-stream/0/87/487/1495/11562`

The example parameters mean:
- `participant_id = 0`: all participant types
- `category_id = 87`
- `event_id = 487`
- `event_category_id = 1495`
- `stage_id = 11562`

The page resolves the event from the URL and uses the event saved in the browser session.

## Where to find the page

Open **Scoring and Streaming** from the sidebar.

The page has three tabs:
- **Scoring:** enter scores and manage match results.
- **Streaming:** enable streaming for eligible matches and view their stream status/link.
- **Stream Settings:** configure which matches streaming preferences apply to.

## Page header and top bar

### Search by Match ID

Enter a match ID and press **Enter**, or wait for the search to run. The page displays the matching match when found.

If the search fails, the page shows:

`Error searching matches`

### Ready for Print

Select **Ready for Print** to open the print queue. The badge count shows how many matches are waiting to be printed.

### Categories and stages

- The category list shows the event's categories, with the number of subcategories in brackets.
- Subcategories are labelled **Sub Division** for a league and **Sub Category** otherwise.
- Stage tiles such as **S1**, **S2**, and so on select the stage.

## Scoring tab: match list

### Match-list views

Use these submenus to narrow the list:
- **ALL**
- **Without results**
- **With results**

### Filter Preferences

Select **Filter** to open **Filter Preferences**. Choose and add any of these filters:
- Participant Type
- Category
- Stage
- Round
- Groups
- Umpire

Select **Apply** to apply the filters. Select **Reset** to clear them.

### Match-list columns

The list can display:
- Match ID
- Date/Time
- Table No.
- Group or Knockout, depending on the stage format
- Round
- Legs
- Match participants, shown with **VS**
- Match Umpire (one or more umpires)
- Status
- Score
- Action

For doubles and mixed doubles, both players in each pair are shown. A forfeited player is indicated with a forfeited icon.

The Score column shows sets won, or match points for a match-point system. A walkover is shown with a label instead of a score.

The table is paginated. The page-size control is at the bottom of the table.

### Empty states

- **No records found:** no matches fit the current filters.
- **Create fixtures to begin with.** with **Go to Fixtures:** there are no fixtures at all.

If the list is empty, first check the selected category, stage, and filters. If there are no fixtures for the event, go to Fixtures to create them.

## Update score dialog

Select **Update score** on a match row to open the score dialog. It displays the match venue, group, match order, date, time, table, umpires, and both sides.

### Entering and saving scores

- Each set has one score box for each side.
- Each score box accepts at most two digits.
- A tie-break, where supported by the match format, has its own two score boxes.
- The page checks scores against the sport's rules and marks a rejected set. A snackbar explains the rule that failed.
- The server validates the full score again when it is saved.
- Select **Update** to save the score.
- Select **Cancel** to close the dialog without saving.
- Select **Reset** to clear the entries.
- After a successful save, the match list refreshes.

Use the sport-specific scoring guide to interpret validation messages and understand which score formats are accepted.

## Walkovers and disqualifications

The walkover dropdown offers:
- **Walk Over**
- **Disqualified**
- **Injured**
- **Double Walk Over**
- **Others**

The **Double Walk Over** option is not available for team matches.

To record a walkover or disqualification:
1. Select the reason.
2. Select the player who did not play, if the selected option requires a player. A double walkover does not require a player.
3. Complete the required choices; **Update** remains disabled until the selection is complete.
4. Save the result.

The walkover can be reset from the same panel. Resetting clears the walkover before set scores can be changed.

Relevant message:

`Match Already Walkover Reset First`

This means the recorded walkover must be reset before new set scores can be entered.

## Manual scoring

The **Manual scoring** toggle starts or stops manual scoring for a match.

The displayed label is:
- **Start match scoring**
- **Stop match scoring**

If the operation fails, the page displays:

`Failed to update manual scoring`

The source material does not specify every reason manual scoring might fail. Check the match state and the user's permissions if the action is refused.

## Streaming tab

To access streaming controls:
1. Open **Scoring and Streaming** from the sidebar.
2. Select the **Streaming** tab.
3. Use **Enable Streaming** for the relevant match.

The Streaming tab is not on the Event page.

### Streaming status and link

The status can show:
- **Streaming** — live
- **Completed**
- **Not Streamed**

The stream link can be copied.

### Disabling streaming after a match starts

A match that has already started cannot have streaming disabled. The page shows:

`The match has already started. You can't disable streaming right now.`

If the match has started, this is an expected restriction rather than a generic streaming failure.

## Stream Settings tab

**Select Stream Preferences** controls which matches streaming applies to. The available preference types are:

- **Participant specific:** matches involving selected participants.
- **Round specific:** matches in selected rounds.
- **Match specific:** selected individual matches.

Choose the relevant preference type and select the matches or values it applies to. Do not assume streaming preferences automatically enable streaming for every match unless the configured behavior confirms that.

## Lineups (team matches)

For a team match, the lineup panel shows **Players in the Lineup**, with a status dropdown for each player.

- Select a team to view its players.
- If no team is selected, the page displays: `Please select a team to view players`.
- A successful player-status change displays: `Player status updated successfully`.
- A successful lineup save displays: `Lineup saved successfully`.
- **Reserve Players** lists players who are not in the lineup.

If players are not visible, select the team first.

## Umpire and referee notes

The notes panel shows the match's umpires and referee. Umpires are numbered, for example **Umpire 1** and **Umpire 2**. Notes are saved from this panel.

The source material does not describe additional note permissions or validation rules; do not infer them from this guide.

## Sub-matches (team matches)

A team match is scored through sub-matches, one per playing table.

### Playing table required

Each sub-match needs a playing table before it can be saved. The validation message is:

`Select a playing table for sub-match {matchNumber} before saving.`

Select a playing table for every sub-match before saving.

### Duplicate participants on the same side

The same participant cannot be selected in both slots on the same side.

Messages include:
- `Match #{n}: The same participant is selected for both slots on Side A.`
- `Match #{n}: The same participant is selected for both slots on Side B.`
- For golden matches, the message begins with `Golden Match #{n}: ...`.

Check the player selections for the side named in the error and make sure each slot has a different participant.

### Playing order

The playing order of team matches is configured through the playing order dialog. Refer to the relevant results guide for details.

## Common messages

| Message | Meaning / next check |
|---|---|
| `Invalid normal set score in set {set_number}` | The set score is invalid under the configured sport rules. Refer to the sport-specific guide. |
| `Score Updated` | The server confirms that the score was saved. |
| `Match Already Walkover Reset First` | Reset the recorded walkover before changing set scores. |
| `Match Data Not Reset` | A match reset operation is blocked; the exact cause is not specified here. |
| `Something went wrong` | A request failed without a more specific server message. Check the action, current match state, and permissions. |
| `Error searching matches` | The match-ID search failed. Verify the ID and retry. |
| `Failed to update manual scoring` | The manual-scoring update failed. The exact cause is not specified by this message alone. |

## Permissions

- **Scoring:** requires the event's score permission (**Update Score, Edit**).
- **Streaming:** requires the stream permission (**Update Stream, Edit**).

Without the required permission, the server refuses the change and its message is shown. If an action is refused, check that the user has the relevant permission before assuming the score or stream settings are invalid.

## Frequently asked questions

### What is the Scoring and Streaming page for?

It is used to enter match results, record walkovers or disqualifications, start or stop manual scoring, enable streaming, manage team lineups and sub-matches, view umpire/referee notes, and prepare scoresheets for printing.

### How do I enter a score?

Select **Update score** on the match row, enter each set's score, add tie-break points in the tie-break boxes when required, and select **Update**.

### How do I search for a match?

Enter its match ID in **Search by Match ID**, then press **Enter** or wait for the search.

### How do I filter the match list?

Select **Filter**, add the desired Participant Type, Category, Stage, Round, Groups, or Umpire filters, then select **Apply**. Use **Reset** to clear the filters.

### Why are there no records on the page?

If the page says **No records found**, no matches fit the current filters. Check the selected category, stage, and filters. If it says **Create fixtures to begin with.**, the event has no fixtures; use **Go to Fixtures**.

### How do I enable streaming for a match?

Open **Scoring and Streaming** from the sidebar, select the **Streaming** tab, and select **Enable Streaming** for the match.

### Why can't I disable streaming?

If the match has already started, the system does not allow streaming to be disabled and displays: `The match has already started. You can't disable streaming right now.`

### What are Stream Settings?

They determine which matches streaming preferences apply to: participant-specific, round-specific, or match-specific selections.

### Why can't I see players in the lineup?

Select a team first. Without a selected team, the page displays `Please select a team to view players`.

### Why can't I save a team sub-match?

Check that a playing table is selected for each sub-match and that the same participant is not selected in both slots on the same side.

### Why is Update disabled when recording a walkover?

The required walkover choices may be incomplete. Select the reason and the player who did not play when required. A double walkover does not require a player.

### How is scoring different for each sport?

The accepted scores and validation rules depend on the event's sport and Game Play configuration. Use the sport-specific guide for Table Tennis, Badminton, Padel, or Tennis rather than applying one sport's rules to another.

## Natural-language and Hinglish query patterns

Treat these as equivalent intents when retrieving this document:

- "Scoring and Streaming page ka use kya hai?"
- "Match ka score kahan enter karna hai?"
- "Match ID se match kaise search karun?"
- "Scoring page par records kyun nahi aa rahe?"
- "Without results aur With results mein kya difference hai?"
- "Matches ko umpire ya round ke hisaab se filter kaise karun?"
- "Streaming kaise enable karun?"
- "Match start hone ke baad streaming off kyun nahi hoti?"
- "Stream Settings mein participant-specific ka matlab kya hai?"
- "Lineup mein players kyun nahi dikh rahe?"
- "Team sub-match save kyun nahi ho raha?"
- "Walkover ke baad score edit kyun nahi ho raha?"
- "Ready for Print ka use kya hai?"
- "Manual scoring start ya stop kaise karun?"

## Answering guidance for the TMS assistant

1. Identify which part of the page the user means: match list, score dialog, walkover, manual scoring, streaming, stream preferences, lineup, sub-match, notes, or print queue.
2. Give the shortest relevant UI path using the exact control labels in this document.
3. For empty results, distinguish **No records found** (filters match no records) from **Create fixtures to begin with** (no fixtures exist).
4. For score errors, identify the sport and use its sport-specific guide; do not generalize one sport's scoring rules to another.
5. For streaming or score updates that fail, check the relevant permission and the specific error message.
6. Do not invent extra controls, permissions, reset conditions, or streaming behavior not stated in the source.
7. Treat server validation and permission responses as authoritative for whether an action succeeded.

## Source references

- Score update: `gateway/src/routers/scoring_router.py` (`update_score`)
- Match list, status, sub-matches, participant order: `gateway/src/routers/match_router.py`
- Team lineups: `gateway/src/routers/teams_router.py` (`fetch_lineup`, `update_lineup`)
- Game Play rules: `gateway/src/routers/rule_setting_router.py` (`get_rule_settings`)
- Team playing order: `gateway/src/routers/playing_order_router.py` (`get_team_playing_order_with_matches`, bulk)
- Event official notes: `gateway/src/routers/planner_router.py`
- Scoring and Streaming UI: `src/app/modules/tms/score-and-streaming/score-and-streaming.component.html`
- Scoring and Streaming logic: `src/app/modules/tms/score-and-streaming/score-and-streaming.component.ts`
- Manual scoring toggle: `src/app/modules/tms/score-and-streaming/manual-scoring-toggle-button`
- Umpire/referee notes: `src/app/modules/tms/score-and-streaming/umpire-refree-notes`
- Score feedback constants: `src/app/modules/tms/score-and-streaming/score-input-feedback.constants.ts`
- TMS module: `src/app/modules/tms/tms.module.ts`
- English translations: `src/assets/i18n/en.json`
