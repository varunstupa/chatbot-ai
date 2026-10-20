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
---
# Knockout stage – wizard, draft, customise and bracket

A **knockout** stage is single elimination: a player who loses a match is out, and winners move on to the next round. This guide covers the knockout wizard, the draft of the participants into the bracket, customising the bracket, and the position matches. The bracket view is in "Knockout bracket" below.

## The knockout creation wizard

The wizard has panels, each with a **Save** (or **Skip**). The main panels:

1. **Stage Participants** – choose the participants of the stage (**Add participant**, **Participant Selection**), and the elite and excluded options (see the group wizard guide).
2. **Knockout Creation Configuration** – how many seeds and the knockout settings.
3. **Max round played** – "Decide the total no. of rounds you want to create in this stage". Pick the round. **With Bye** or **Without Bye** decides whether byes are used to fill the bracket. Without Bye ("minimise byes") gives a smaller bracket where possible.
4. **Legs** – "Choose the no. of legs you wish to give". A leg is one match of a round; a round can have 1, 2 or more legs. Pick a round and its legs; a round whose legs are disabled cannot be changed.
5. **Position Match** – "Position match is essentially used to determine the final ranking of participants in a tournament." Choose the round in which the losing semi-finalists play for third and fourth.
6. **Separation Criteria** – see below.
7. **Playing Format** – "Select the playing order you want to implement".
8. **Stage Winners** – "You can select the number of winners you want to include in this stage". Winners of a round move on.

**Save and continue** saves the stage.

## No. of seeds and seeding

- **No. Of Seeds** – how many seeds are placed in the bracket. Digits only; three digits at most.
- **Elite Participants Used** – shows that elite players are used as seeds.
- **Seeding** – "Draw is created strictly based on defined seeds, respecting entity and group separation."
- **Random Seeding** – "The initial knockout draw randomizes seeding within levels, maintaining entity and group separation. This mandatory s…"

## Separation criteria and first draw settings

- **First Time Draw Settings** – the rules for the first draw.
- **Separation Type**:
  - **As far as possible** – "Current logic to separate entities (Club/MA) for as many rounds as possible."
  - **1st Round Only** – "System ensures separation of entities only in the first round. If Group Separation is enabled, it takes P1 priority."
- **Group Separation** – when the knockout follows a group stage, players from the same group are kept apart.

## Draft the bracket (Knockout draft)

- **Participant List**, **Participant positions** and **Matches** show the bracket being built.
- **Search** finds a participant. **Export Excel** downloads the bracket participants.
- **Customize** opens the customise view (below).
- **Shuffle** – "Shuffle is only available for knockout stages." Places the participants again at random within the rules.
- **Reset Seeding** – clears the seeds of the draft.
- **Preferences** – shows the preferences of the draft.
- **Save draft** – saves the draft without creating the fixture.
- **Save and proceed** (or **Redraw** for an existing draft) – creates the fixture. It is greyed out while the draft is not valid.
- Bench a participant: "Bench participant". A benched participant is placed later.

## Customise (Customize Participants)

- **Full expand** opens the view full screen; **Exit full expand** closes it.
- **Drag Participants from Participant Positions to Matches as per your choice to create the right fixtures.** Or type the player positions in the input box.
- **Matches bracket** – the matches of each round; **Expand matches** shows every match.
- **Swap position** exchanges two players; **Move all players to participant positions** places everyone in their seeded spots.
- **Positions** panel: for each seed, the player with **Member Association** and **Club** and the seeding; a **BYE** is a placeholder.
- Actions: **Partial Place** (place only some players), **Close Customisation** (leave without saving) and **Save Customisation**.
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

## Position matches and legs

- A position match decides third and fourth, and the final places. Set it in the wizard (Position Match step).
- Legs: when the legs of a tie are level, "Tied Legs Detected" is shown; the result rules are in the scoring guide.

## Position filter (Position Matches tab)

- The **Position Matches** tab appears when the stage has position matches. Its buttons are position ranges, each labelled with its round name, or "Position" followed by the range (for example "Position 5-8"). A range with no name shows "--".
- Click a range button to show only the position matches that fall inside that range. The chosen button is highlighted.
- When there are more than seven ranges, left and right arrows scroll the buttons.
- The filter only changes what is shown. It does not move or change any match.

## Messages

- "A redraw is required before creating a draft" – the groups changed; redraw first.
- "Knockout Fixtures Created" – the bracket was created.
- "Knockout Groups Created" / "Knockout Groups Updated" – the knockout groups were saved.
- "Shuffle is only available for knockout stages." – the stage is not a knockout.
- "Stage Configuration Missing" – save the stage configuration first.
- "No Winner Determined" – a round cannot advance until a winner is set.
- "Stage Not Found", "Match Not Found", "No Groups Found" – the item no longer exists; reload the page.
- Swap and replace messages: "Participants swapped successfully.", "Unable to swap participants.", "Replace is only allowed in the first stage of the category.", "Replace is not available for teams. Use swap, or use replace in singles, doubles, or mixed doubles.", "Swap is not available for this participant type.", "Please select a valid participant to replace."

## Permissions

- Drafting, customising, shuffling and creating the knockout fixture need **Edit** on **Fixture Access**. Without it the server answers "Access Denied".

## Frequently asked questions about the knockout stage

**How do I create a knockout stage?** Work through the wizard: participants, max round, legs, position match, separation, playing format and winners, saving each panel.

**What is a Position Match?** A match that decides the final places, such as third and fourth.

**What is Max round played?** The number of rounds the bracket has. With Without Bye the bracket uses fewer byes.

**How many legs can a round have?** Choose the legs for each round in the Legs panel; a leg is one match of that round.

**What is the difference between Seeding and Random Seeding?** Seeding places the seeds exactly by their number. Random Seeding shuffles the seeds within each level, keeping the separation rules.

**How do I place participants in the bracket?** Use **Customize** and drag each player to a match position, or type the position, then **Save Customisation**.

**What does "Two BYEs are not allowed in a pair" mean?** Two byes cannot meet each other in one match. Move one bye to another match.

**How do I save the knockout draft?** Click **Save draft**, or **Save and proceed** to create the fixture.
**What does the position filter do in the fixture screen?** On the Position Matches tab it narrows the position matches to the range you click, for example Position 5-8. Click another range to toggle, and the highlighted button shows the range in use.
