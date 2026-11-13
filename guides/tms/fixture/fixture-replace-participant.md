---
doc_id: tms.fixture.replace-participant
title: Fixture replace and swap participant
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - replace participant
  - replace player
  - swap participant
  - swap player
  - sample fixture replace
  - replace in first stage
  - delete and refund
  - delete with refund
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I replace the placeholders of a sample fixture?
  - Why can I not replace a player in the second stage?
  - What does Delete & Refund mean when replacing?
  - Why does replace say "Replace is not allowed"?
  - How do I swap two participants?
backend_sources:
  - gateway/src/routers/stage_router.py (replace_stage_participant; feature EDIT_STAGE, Edit; validates, registers the new player, then commits and withdraws the old one)
  - tms/src/service/stage_service.py (replace_stage_participant)
  - tms/src/router/stage_router.py (replace_stage_participant)
source_files:
  - src/app/modules/tms/fixture-configuration/fixture-popups/replace-participant-hosts/replace-participant-hosts.component.html
  - src/app/modules/tms/fixture-configuration/replace-participant-dialog/replace-participant-dialog.component.html
  - src/app/modules/tms/fixture-configuration/replace-participant-confirm-dialog/replace-participant-confirm-dialog.component.html
  - src/app/modules/tms/fixture-configuration/replace-participant-dialog/replace-participant-dialog.component.ts
  - src/app/modules/tms/fixture-configuration/replace-participant-confirm-dialog/replace-participant-confirm-dialog.component.ts
  - src/app/modules/tms/fixture-configuration/fixture-configuration.component.ts (executeReplaceParticipant)
---
# Fixture replace and swap participant

There are two different replace actions on the fixtures screen:
- **Replace With Participants** / **Complete Fixture** – on a **sample** fixture, swaps all placeholders for the real participants in one step.
- **Replace** (row icon) – on a real fixture, puts another registered or queued player in place of one participant. **Swap** exchanges two participants of the same stage.

## Sample fixture: Replace With Participants / Complete Fixture

- The button is in the final bottom bar of a sample fixture, and only once the previous stages are concluded. It reads **Replace With Participants** for a single stage and **Complete Fixture** when the category has several stages.
- Click it: **Replace Participant?** "Are you sure you want to replace participant for this stage?" with the stage name highlighted. Click **Yes**.
- The placeholders are replaced by the real participants, the stage goes back to its draft and the stage list reloads.

## Replace participant: when the row icon is available

- The replace icon is on the participant rows (group standings, knockout draft). It is shown only when all of these are true:
  - the category is singles, doubles or mixed doubles (not teams): otherwise "Replace is not available for teams. Use swap, or use replace in singles, doubles, or mixed doubles.";
  - the stage is the first stage of the category: otherwise "Replace is only allowed in the first stage of the category.";
  - the fixture is not a sample fixture;
  - not every match of the stage is completed.
- The server also refuses a participant who already has a match in progress or scored: "Replace is not allowed".

## Choose the replacement (Replace dialog)

1. Click the replace icon. The title reads **Select a participant to Replace with**, with **Replacing** and the current participant.
2. **Filters**: **Registered players** (paid registrations only) and **Queue players** (queued players show "Queue #n"). Use **+ Add filter** to add one and **Clear all** to remove them.
3. Search with **Search participants**. Columns: **Seed**, **Participant**, **Member Association**, **Participant Club** and **Points**. Elite and excluded players carry an **Elite** or **Excluded** tag. The current participant cannot be chosen; a **BYE** row is a placeholder.
4. Click **Replace** to continue to the confirmation. "Failed to load participants. Please try again." if the list cannot be loaded.

## Replace in doubles and mixed doubles (Replace player in draw)

- The dialog is titled **Replace player in draw** with steps **Select player**, **Choose replacement**, **Confirm**.
- Step 1: "Who would you like to replace?" – "Select player(s) from the current pair to continue". Tick **Player 1**, **Player 2** or both, then **Next**. With none ticked: "Select at least one player to continue."
- Step 2: the header shows "Replacing: … (Player n)" and "… (Player n) remains in pair", or "Replacing entire pair: …". Choose as many players as you are replacing. A third pick shows "You can only select 2 participants for doubles/mixed doubles."; too few shows "Please select two participants." **Back** returns to step 1.

## Replace participant: confirm dialog

- The title says **You are about to replace-** (or **You are about to swap-**) and the list reads **The following changes are expected to happen:** For doubles it shows **Current pair** and **Updated pair** with **Remains** / **Replacing** / **Unchanged** / **New** badges (or **Current pair (outgoing)** and **New pair (incoming)** when both players change).
- The dialog lists what will happen:
  - the old participant **will be deleted or deleted with refund**, depending on the choice below;
  - the new player **will be registered in** the category, and an order will be generated against the player in **Cash Mode**. Collect the payment from the payee.
- **Select an option for** the old participant, then choose one option:
  - **Delete** – the old participant is removed without a refund;
  - **Delete & Refund** – the old participant is refunded (the refund amount is shown: "will be refunded {amount} and deleted from the system"). Offered only when refunds are set up for the event; it is then preselected. Otherwise only **Delete** is offered. When one doubles player is replaced, the refund is half the pair fee.
- **Confirm & Replace** runs the replacement; **Back** returns to the list.

## Swap participant (two participants of one stage)

- Opened with the swap icon of a participant row. The title reads **Select a participant to Swap with**, with **Swapping With**; click **Swap**, then **Confirm & Swap**.
- Server rules: neither participant may have a match in progress or scored in this stage, and the stage must not be completed (otherwise "Swap Not Allowed"). Two participants of the stage exchange their places; a player from outside the stage who belongs to the category takes the other's place, and that participant leaves the stage. For teams, the line-ups of the affected matches are cleared.
- Without a valid choice: "Please select a valid participant to swap."
- Success: "Participants swapped successfully."; failure: "Unable to swap participants.". For a participant type that cannot swap: "Swap is not available for this participant type."

## Replace participant: result messages

- Success: "Participant replaced successfully."
- Failure: the server's message; if none: "Unable to replace participant." For doubles, if the new pair cannot be created: "Unable to create replacement team."
- Loading the list fails: "Failed to load participants. Please try again."

## Replace participant: what the server checks

The server first runs a dry run, then registers the new player (if needed), then commits the replacement and withdraws the old participant:
- The stage must exist ("Stage Not Found") and must not be completed ("Replace is not allowed").
- Only the first stage of a category: "Replace is only allowed in the first stage".
- Not for team categories: "Replace is not allowed for team".
- The old participant must be in the stage: "Stage Participant Not Found".
- Not while the old participant has a match in progress or scored: "Replace is not allowed".
- The new player must belong to the category ("Stage Participant Not Found"), must differ from the old one and must not already be in the stage ("Replace is not allowed").
- Missing order details for a new registration: "Missing required order fields for replace".
- The new player's registration follows the normal registration rules (see the registration guide); an error from registration is shown as its own message, and nothing is replaced.

## Replace participant: what the server changes

- A new player is registered in cash (offline) mode, so the order is created against them and the slot is marked paid. If the order were an online payment, the slot would stay pending and the matches could not be scored until the payment clears.
- A registered or queued player who is chosen is moved into the slot without a new order: they are marked accepted and paid and leave the queue. An elite player chosen this way stops being elite and loses their place in another stage; if that stage is already drawn the replace is refused.
- The new player takes the old participant's seed, group and match places.
- The old participant is then withdrawn (with a refund when **Delete & Refund** was chosen). If the withdrawal fails, the replacement still stands.
- Success messages from the server: "Participants Registered Successfully" (new player) or "Participant replaced successfully" (existing player). The screen shows "Participant replaced successfully.".

## Replace player in draw (doubles): what the server checks

- The draw must be doubles or mixed doubles, the first stage, and the pair must be in the stage; otherwise "Replace is not allowed", "Replace is only allowed in the first stage" or "Stage Participant Not Found".
- The pair has a match in progress or scored: "Replace is not allowed after a match has been played".
- The incoming player is already in another pair or in this draw: "The incoming player is already in another pair or in this draw".
- The selected player is not in the pair: "The selected player is not part of this pair".
- The incoming registration is withdrawn, deleted or another player's: "The incoming player's registration is withdrawn, deleted or belongs to another player".
- The incoming player's partner cannot go back to their own registration: "The incoming player's current partner cannot be returned to their own registration".
- Mixed doubles: "A mixed doubles pair must have one male and one female player".
- The pair keeps its place, schedule and results; only its players and name change. The outgoing players' own registrations are withdrawn, with the refund choice.

## Replace participant: permissions

- Replacing and swapping need **Edit** on **Edit Stage**. Without it the server answers "Access Denied".

## Frequently asked questions about replacing participants

**How do I replace the placeholders of a sample fixture?** In the final bottom bar click **Replace With Participants** (or **Complete Fixture**), then **Yes**.

**How do I replace one participant?** Click the replace icon on the participant's row, choose the player, click **Replace**, pick the delete option and **Confirm & Replace**.

**Why can I not replace a player in the second stage?** Replacing is allowed only in the first stage.

**What does Delete & Refund mean when replacing?** In the confirmation the old participant's refund amount is shown ("will be refunded … and deleted from the system"). **Delete & Refund** refunds and removes them; **Delete** removes them without refund. This is decided on the replace confirmation, not on the Players page.

**Why is the Replace button not visible?** **Replace With Participants** appears only for a sample fixture after the previous stages are concluded. The row replace icon appears only on the first stage of a real singles, doubles or mixed fixture, until all matches are completed.

## Frequently asked questions about replacing participants (more)

**Why is Delete & Refund not offered?** Refunds are not set up for this event, so only **Delete** is available.

**Why does replace say "Replace is not allowed"?** The old participant has a match in progress or already scored, the stage is completed, or the chosen player is the same person or already in the stage.

**How do I swap two participants?** Click the swap icon on a participant row, choose the second participant, click **Swap** and then **Confirm & Swap**.

**Why is the new player's match not scored?** The slot is still marked as payment pending. Replacements made from this screen are registered in cash mode and marked paid, so this happens only when the order is an online payment that has not cleared.
