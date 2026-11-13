---
doc_id: tms.fixture.knockout-stage
title: Knockout stage – wizard, draft, customise, position matches and bracket
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - knockout stage
  - knockout creation configuration
  - knockout draft
  - customize participants
  - customise knockout
  - matches bracket
  - position match
  - max round
  - legs per round
  - bye in knockout
  - knockout bracket
  - first time draw settings
  - random seeding
  - save customisation
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I create a knockout stage?
  - What is a Position Match?
  - What is Max round played?
  - How many legs can a round have?
  - What is the difference between Seeding and Random Seeding?
  - How do I place participants in the bracket?
  - What does "Two BYEs are not allowed in a pair" mean?
  - How do I save the knockout draft?
backend_sources:
  - gateway/src/routers/fixture_router.py (draft_knockout_fixture, get_knockout_fixtures, get_knockout_matches; feature FIXTURE_ACCESS, Edit)
  - gateway/src/routers/round_router.py (update_round)
  - tms/src/service/knockout_fixture_service.py (draft_knockout_fixture, get_knockout_fixtures, get_knockout_matches)
source_files:
  - src/app/modules/tms/fixture-configuration/knockout-creation-wizard/knockout-creation-wizard.component.html
  - src/app/modules/tms/fixture-configuration/knockout-creation-wizard/bodies/knockout-config-body/knockout-wizard-config-body.component.html
  - src/app/modules/tms/fixture-configuration/knockout-creation-wizard/bodies/max-round-body/knockout-wizard-max-round-body.component.html
  - src/app/modules/tms/fixture-configuration/knockout-creation-wizard/bodies/legs-body/knockout-wizard-legs-body.component.html
  - src/app/modules/tms/fixture-configuration/knockout-creation-wizard/bodies/position-match-body/knockout-wizard-position-match-body.component.html
  - src/app/modules/tms/fixture-configuration/knockout-creation-wizard/bodies/separation-criteria-body/knockout-wizard-separation-criteria-body.component.html
  - src/app/modules/tms/fixture-configuration/knockout-draft-participants/knockout-draft-participants.component.html
  - src/app/modules/tms/fixture-configuration/knockout-customise-participants/knockout-customise-participants.component.html
  - src/app/modules/tms/fixture-configuration/knockout-customise-participants/positions-panel/knockout-customise-positions-panel.component.html
  - src/app/modules/tms/fixture-configuration/knockout-creation-wizard/save-bar/knockout-wizard-save-bar.component.html
  - src/app/modules/tms/fixture-configuration/knockout-draft-participants/actions-bar/knockout-draft-actions-bar.component.html
  - src/app/modules/tms/fixture-configuration/knockout-customise-participants/actions-bar/knockout-customise-actions-bar.component.html
  - src/app/modules/tms/fixture-configuration/knockout-customise-participants/knockout-customise-layout.service.ts
---
# Knockout stage – wizard, draft, customise and bracket

A **knockout** stage is single elimination: a player who loses a match is out, and winners move on to the next round. This guide covers the knockout wizard, the draft of the participants into the bracket, customising the bracket, and the position matches. The bracket view is in "Knockout bracket" below.

## Knockout creation wizard: the panels

The wizard is shown while the knockout stage has no draft yet. Each panel has **Save** (some also **Skip**):

1. **Stage Winners** – only for a second or later stage: who qualifies from the stage before (as in the group wizard guide).
2. **Participants selection** – choose the participants (**Add participant** / **Edit participants**) and the elite and excluded options (see the group wizard guide).
3. **Knockout Creation Configuration** – **No. Of Seeds** (see below). For a sample fixture, type **Total Participants**.
4. **Max round played** – "Decide the total no. of rounds you want to create in this stage". Pick the round (**Final**, **Round of** 4, 8 …). **With Bye** or **Without Bye** decides whether byes fill the bracket; **Without Bye** minimises byes.
5. **Position Match** – shown only for some max-round choices. "Position match is essentially used to determine the final ranking of participants in a tournament." Choose **Top** N; collapsed it reads "Assign participants to their specific spots in the stage based on the results".
6. **Separation Criteria** – see below. Greyed out until the stage has participants.
7. **Legs** – "Leg refers to the number of matches defined in a particular round". Pick the legs; collapsed it shows "No. Of Legs: …". When legs are locked they cannot be changed.
8. **Playing Format** – team categories only. "Select the playing order you want to implement".

## Knockout creation wizard: Save and continue

- **Save and continue** at the foot creates the knockout draft.
- It is greyed out until the stage has participants and, for team categories, a playing format is saved. It is also greyed out while a save is running.
- For a sample fixture, **Save and continue** creates the sample draft directly.
- If the previous stage is not fully scored, the **Alert!** popup shows "Final Fixture cannot be created for this stage as all matches of the previous stage are not scored." with **Proceed**.

## Knockout wizard: No. of seeds and seeding

- **No. Of Seeds** – how many seeds are placed in the bracket. Digits only; three digits at most.
- **Elite Participants Used** – shows that elite players are used as seeds.
- **Seeding** – "Draw is created strictly based on defined seeds, respecting entity and group separation."
- **Random Seeding** – "The initial knockout draw randomizes seeding within levels, maintaining entity and group separation. This mandatory shuffle applies to the first draw (Global Random Selection)."

## Knockout wizard: separation criteria and first draw settings

- **First Time Draw Settings** – the rules for the first draw.
- **Separation Type**:
  - **As far as possible** – "Current logic to separate entities (Club/MA) for as many rounds as possible."
  - **1st Round Only** – "System ensures separation of entities only in the first round. If Group Separation is enabled, it takes P1 priority."
- **Group Separation** – a toggle; when the knockout follows a group stage, players from the same group are kept apart.
- The entity options (for example club or association) are ticked one by one; a ticked option shows its details.

## Knockout draft: lists and tabs

- Shown after the wizard is saved and before the fixture is created (address bar: **Draft edit**).
- **Participant List** shows the number of benched (unplaced) participants; click it to place them. It is shown only when someone is benched.
- **Export Excel** downloads the bracket participants. **Search** finds a participant.
- Tabs: **Matches** (the draft pairs, with **Bench participant** and **Swap position** icons per row) and **Participant positions** (**S.No**, **Draw Position**, **Flag**, **License ID**, **Seeding**, **Participant**, **Member Association**). A **Position Matches** tab appears when the stage has position matches.
- Swap actions are hidden for team categories and once all matches are completed.

## Knockout draft: bottom bar

- **Customize** – opens **Customize Fixtures** to choose rounds, then the customise view. Shown only when nobody is benched and the search is empty.
- **Shuffle** – places the participants again at random within the rules (hidden while searching).
- **Back to default** – resets the seeding of the draft to the default.
- **Preferences** – asks **Delete Fixture?**; confirming deletes the draft and returns to the wizard so the settings can be changed.
- **Save draft** – saves the draft without creating the fixture.
- **Save and proceed** – creates the fixture. It changes to **Redraw** when benched participants have changed and the bracket must be rebuilt; **Redraw** is greyed out while no participant is placed.
- For a sample fixture only **Preferences**, **Save draft** and the main button are shown.

## Knockout customise view (Customize Participants)

- Title **Customize Participants**. "Drag Participants from Participant Positions to Matches as per your choice to create the right fixtures." "OR. Define player Positions in the input box to allocate them the matches".
- **Full expand** / **Exit full expand** switches full screen.
- **Participant positions** lists the players by seeding level ("… SEEDING"), with **Flag**, **License ID**, **Seeding**, **Participant**, **Member Association**, **Club**; **BYE** is a placeholder.
- **Matches** shows the bracket; the icons expand the matches, view matches, and move all players back to participant positions.
- **Partial Place** places only some players. **Close Customisation** (shown while nobody is benched and players are still unplaced) leaves without saving. **Save Customisation** is shown when someone is benched or every player is placed.

## Knockout customise view: bracket rules

- The bracket rules are checked as you move players:
  - "Two BYEs are not allowed in a pair (e.g., 0 & 1, 2 & 3, etc.)" – a pair of byes cannot share a match.
  - "Invalid move: cannot place two BYEs in the same match pair."
  - "Invalid swap: cannot have a BYE vs BYE match."
  - "Invalid swap: cannot place a BYE with another BYE in same match pair."
- "All participants are in the benched list. Please create groups from the benched participants before saving."

## Knockout bracket

- **Matches bracket** shows each round as a column; the matches connect to the next round.
- **Round of** labels each round.
- The **Position Match** shows the match for places.
- Scores and results are entered on the match (see the scoring guide).
- A **Forfeit Player** marker shows a forfeited player.

## Knockout position matches and legs

- A position match decides third and fourth, and the final places. Set it in the wizard (Position Match step).
- Legs: when the legs of a tie are level, "Tied Legs Detected" is shown; the result rules are in the scoring guide.

## Position filter (Position Matches tab)

- The **Position Matches** tab appears when the stage has position matches. Its buttons are position ranges, each labelled with its round name, or "Position" followed by the range (for example "Position 5-8"). A range with no name shows "--".
- Click a range button to show only the position matches that fall inside that range. The chosen button is highlighted.
- When there are more than seven ranges, left and right arrows scroll the buttons.
- The filter only changes what is shown. It does not move or change any match.

## Knockout stage: messages

- "A redraw is required before creating a draft" – the groups changed; redraw first.
- "Knockout Fixtures Created" – the bracket was created.
- "Knockout Groups Created" / "Knockout Groups Updated" – the knockout groups were saved.
- "Shuffle is only available for knockout stages." – the stage is not a knockout.
- "Stage Configuration Missing" – save the stage configuration first.
- "No Winner Determined" – a round cannot advance until a winner is set.
- "Stage Not Found", "Match Not Found", "No Groups Found" – the item no longer exists; reload the page.
- Swap and replace messages: "Participants swapped successfully.", "Unable to swap participants.", "Replace is only allowed in the first stage of the category.", "Replace is not available for teams. Use swap, or use replace in singles, doubles, or mixed doubles.", "Swap is not available for this participant type.", "Please select a valid participant to replace."

## Knockout stage: permissions

- Drafting, customising, shuffling and creating the knockout fixture need **Edit** on **Fixture Access**. Without it the server answers "Access Denied".

## Frequently asked questions about the knockout stage

**How do I create a knockout stage?** Work through the wizard panels (participants, seeds, max round, position match, separation, legs, and for teams the playing format), saving each, then click **Save and continue**.

**What is a Position Match?** A match that decides the final places, such as third and fourth.

**What is Max round played?** The number of rounds the bracket has. With Without Bye the bracket uses fewer byes.

**How many legs can a round have?** Choose the legs for each round in the Legs panel; a leg is one match of that round.

**What is the difference between Seeding and Random Seeding?** Seeding places the seeds exactly by their number. Random Seeding shuffles the seeds within each level, keeping the separation rules.

## Frequently asked questions about the knockout stage (more)

**How do I place participants in the bracket?** Click **Customize**, tick the rounds and click **Next**, then drag each player to a match position (or type the position) and click **Save Customisation**.

**Why is the Customize button missing?** It is hidden while participants are benched or a search is typed, and for sample fixtures.

**What does "Two BYEs are not allowed in a pair" mean?** Two byes cannot meet each other in one match. Move one bye to another match.

**How do I save the knockout draft?** Click **Save draft**, or **Save and proceed** to create the fixture.

**What does the position filter do in the fixture screen?** On the Position Matches tab it narrows the position matches to the range you click, for example Position 5-8. Click another range to toggle, and the highlighted button shows the range in use.
