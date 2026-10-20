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
  - How do I replace a participant in a sample fixture?
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
  - src/app/modules/tms/fixture-configuration/fixture-configuration.component.ts (executeReplaceParticipant)
---
# Fixture replace and swap participant

On a **sample** fixture the participants are placeholders until the real players are known. The **Replace** action puts a real registered player in place of a placeholder, and **Swap** exchanges two players of the same stage.

## When the action is available

- The **Replace** button of a stage shows only for a sample fixture, and only once the previous stages are finished.
- Replacing is allowed in the **first stage** only. A later stage gets: "Replace is only allowed in the first stage".
- A participant who already has a match in progress or a scored match cannot be replaced: "Replace is not allowed".
- Teams cannot be replaced: "Replace is not allowed for team".
- A participant who is not in the stage: "Stage Participant Not Found".

## Choose the replacement (Replace dialog)

1. Click **Replace** on the placeholder. The title reads **Select a participant to Replace with**.
2. Search with **Search participants** and pick a player from the list. The list shows **Seed**, **Participant**, **Member Association**, **Participant Club** and **Points**. Players who cannot be chosen are greyed out.
3. For doubles and mixed doubles choose exactly two players. Choosing a third one shows: "You can only select 2 participants for doubles/mixed doubles." Clicking **Replace** with one player shows "Please select two participants."
4. A **BYE** row is a placeholder, not a player.
5. Click **Replace** to continue to the confirmation.

## Confirm (Replace confirm dialog)

- The title says **You are about to replace-** (or **You are about to swap-**) and the list reads **The following changes are expected to happen:**
- The dialog lists what will happen:
  - the old participant **will be deleted or deleted with refund**, depending on the choice below;
  - the new player **will be registered in** the category, and an order will be generated against the player in **Cash Mode**. Collect the payment from the payee.
- **Select an option for** the old participant, then choose one option:
  - **Delete** – the old participant is removed without a refund;
  - **Delete & Refund** – the old participant is refunded (the refund amount is shown: "will be refunded {amount} and deleted from the system").
- **Confirm & Replace** runs the replacement.

## Swap (two participants of one stage)

- The title reads **Select a participant to Swap with**; the button reads **Confirm & Swap**.
- Choose the second participant and confirm. Without a valid choice: "Please select a valid participant to swap."

## Result messages

- Success: "Participant replaced successfully."
- Failure: the server's message; if none: "Unable to replace participant."
- Loading the list fails: "Failed to load participants. Please try again."

## What the server checks (replace)

The server first runs a dry run that checks the replacement, then registers the new player, then commits the replacement and withdraws the old participant:
- Only the first stage of a category; otherwise "Replace is only allowed in the first stage".
- Not for team categories: "Replace is not allowed for team".
- Not while the old participant has matches in progress or scored: "Replace is not allowed".
- The participant must be in the stage: "Stage Participant Not Found".
- Missing order details for the replacement: "Missing required order fields for replace".
- Dry run passed: "Replace dry run completed successfully" (internal step); the replacement itself ends with "Fixture Updated".
- Online payment: the new player's slot is marked pending, and their matches cannot be scored until the payment clears.
- The new player's registration follows the normal registration rules (see the registration guide): an error from registration is shown as its own message.

## Permissions

- Replacing needs **Edit** on **Edit Stage**. Without it the server answers "Access Denied".

## Frequently asked questions about replacing participants

**How do I replace a participant in a sample fixture?** Click **Replace** on the placeholder, choose the player, then **Replace**, pick the refund option and **Confirm & Replace**.

**Why can I not replace a player in the second stage?** Replacing is allowed only in the first stage.

**What does Delete & Refund mean when replacing?** In the confirmation the old participant's refund amount is shown ("will be refunded … and deleted from the system"). **Delete & Refund** refunds and removes them; **Delete** removes them without refund. This is decided on the replace confirmation, not on the Players page.

**Why is the Replace button not visible?** The button appears only for a sample fixture, after the previous stages are finished. For a genuine fixture, or while a previous stage is still running, there is no Replace button.

**Why does replace say "Replace is not allowed"?** The old participant has a match in progress or already scored, or the team rules block it.

**How do I swap two participants?** Use **Swap**, choose the second participant and confirm.

**Why is the new player's match not scored?** The replacement was paid online and the payment has not cleared yet.
