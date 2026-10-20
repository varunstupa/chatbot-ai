---
doc_id: tms.players.pairs-teams
title: Players page – pairs and teams
routes:
  - tms/players/:event_id
aliases:
  - add pairs
  - add team
  - edit team
  - edit pair
  - unpaired participants
  - team details
  - player details
  - loan player
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I add a doubles pair?
  - How do I add a team?
  - How do I change the players of a team?
  - What are Unpaired Participants?
  - Why does saving a team say Minimum Members Required?
  - How do I add a team logo in a league?
backend_sources:
  - gateway/src/routers/registration_router.py (register_event_participants, update_event_participant, update_team_details)
  - gateway/src/routers/teams_router.py (create_team)
  - gateway/src/routers/user_router.py (create_temporary_user_role)
source_files:
  - src/app/modules/tms/players/players.component.ts
  - src/app/modules/tms/components/double-player-registration-sidebar/double-player-registration-sidebar.component.html
  - src/app/shared/components/team-registration-sidebar/team-registration-sidebar.component.ts
  - src/app/modules/tms/players/player-details/player-details.component.ts
  - src/app/modules/tms/players/team-details/team-details.component.ts
---
# Players page – pairs and teams

This guide explains how to add and edit doubles pairs, mixed doubles pairs and teams on the **Players** page, what the server checks when you save them, and the **Player Details** and **Team Details** panels of league events. Adding singles players, temporary players and the general add errors are in "Players page – adding singles players and fixing add errors".

## Adding doubles and mixed doubles pairs

1. Select a doubles or mixed doubles category and click **Add**. The **Add Pairs** panel opens: "Choose participants to create a pair, you can also borrow participant from other organizations with unpaired participants."
2. Click **Add participant 1**, pick the player from **Available Participants** (use **Search**, **Search by**, the **Licensed** / **Unlicensed** tabs or **Add Temporary Player**), then do the same for **Add participant 2**.
3. Click **Add** to register the pair.

- **Unpaired Participants** lists players of this category who registered without a partner, so you can pair them – also players of other organisations.
- **Ineligible players** shows players who do not match the category's rules; they cannot be chosen.
- **Add** becomes active once a participant is chosen. In leagues, "Both players cannot be loan players" – only one player of a pair may be on loan.
- The **Self** toggle decides whether each player pays separately (see the adding guide).

## Pair rules and messages

- "Select Two Players." – a pair needs exactly two players.
- "Select Players from Dropdown." – a player was not chosen from the list.
- "Duplicate Players." – the same player is twice in the pair.
- "Cannot Add the Same Gender Player." – a mixed doubles pair needs one male and one female player.
- "Players Already Registered With Another Pair" – a player is already in another pair of the category.
- The payment and registration errors of the adding guide apply too (for example "Event payment settings are required").

## Adding teams

1. Select a team category and click **Add**. The team panel (**Add Member**) opens.
2. Choose the **role** (for example member association or club) and then the organisation in **Select Parent**.
3. Enter the **Team Name**.
4. Click **Add Player** and pick the players (Licensed, Unlicensed, **Add Temporary Player**, **Ineligible players** as for singles). Each chosen player shows their points.
5. In leagues, mark each player **Active** or **Reserve**; with loan players enabled, **Loan** adds a player borrowed from another team.
6. Click **Save**.

- **Add Player** and **Loan** stay greyed out until the role and the organisation are chosen (not when editing).
- For teams created with **Team-up**, the **Ineligible players** toggle is not offered.
- "Please enter team name" – the team name is empty.
- "Please select both Roles and User" – the role or the organisation is missing.

## Team rules checked by the server

When a team is created or saved, the server checks the category's team settings (on the **Registration** page):
- "Minimum Members Required" / "Maximum Members Allowed" – the number of players is outside **Players in Team**.
- "Maximum EU Members Allowed", "Maximum Non EU Members Allowed", "Maximum Other Members Allowed" – too many players of one type for **Player Bifurcation**.
- "Player Already Registered In Category" – a player is already in another entry of the category.

## Editing a pair or a team

- Tournaments: ⋮ on the row → **Edit**. The panel (**Edit Team** for teams) opens with the current players; change them and click **Update** (pairs) or **Save** (teams).
- Leagues: click the **Player Details** icon on the row (see below).

The server then checks:
- "Modification Not Allowed" – the **Registration** toggle of the category is off. Turn it on on the **Registration** page to edit entries.
- "Player Already Registered In Category" – a new player is already in another entry.
- The team size and bifurcation limits above.
- "Registration blocked due to point restriction" – the point restriction of the category still applies when editing (unlike adding).

A player removed from a pair goes back to the **Singles** tab as an unpaired player. For teams this only happens for teams created with **Team-up**.

## League events: Player Details panel (team roster)

In league events the **Action** column shows icons instead of ⋮: **Player Details**, **Team Details**, **Delete**, **Forfeit** (F) and **Delete & Refund**.

**Player Details** opens the team's roster:
- **Team Name** and **Verification Status**.
- **Add Players** → **Add** opens the player list (search, **Ineligible players**). **Loan** (when loan players are enabled) adds a player from another team.
- Each player shows their rank values. Expand a player to **ADD DETAILS** (rank values) and a **Player Image** (270 × 480 px), then **Save**.
- **Active** / **Reserve** sets the player's lineup status.
- "No players added yet" – click **Add First Player**.
- "Please enter team name" / "Please select at least one participant" when saving an incomplete team.

## League events: Team Details panel (team profile)

**Team Details** edits the team's profile:
- **Basic Info**: **Team Name**, **Link Organizations**, **Email**, **Team Website**, **Address**.
- **Add Member**: **Full Name**, **Role**, email, **Member Image** (270 × 480 px) – "Member updated successfully.". Tick members and **Delete** to remove them ("N member(s) deleted successfully."; nothing ticked: "Please select at least one member to delete").
- **Add venue** (panel **Create New Venue**): **Venue Name**, **Spectator Capacity**, **Table**, Net, Ball, Flooring, **Upload Venue Image** (480 × 270 px) – "Venue updated successfully.". Delete: "Venues deleted successfully" or "Please select at least one venue to delete".
- **Upload Photos**: **Team Image** (1256 × 320 px, up to 15 MB) and **Team Logo** (80 × 75 px, up to 5 MB).
- Save: "Team details updated successfully."

Image messages: "File exceeds max limit of N MB.", "… resolution must be W px X H px. Current: …", "Invalid image file.", "Upload failed. Please try again".

## Frequently asked questions about pairs and teams

**How do I add a doubles pair?** **Add** → **Add participant 1** and **2** → **Add**.

**What are Unpaired Participants?** Players of the category who registered without a partner; you can pair them, also across organisations.

**How do I add a team?** **Add** → role and **Select Parent** → **Team Name** → **Add Player** → **Save**.

**Why does saving a team say Minimum Members Required?** The team has fewer players than **Players in Team** on the Registration page requires.

**Why "Modification Not Allowed" when editing a team?** The **Registration** toggle of the category is off.

**Why can I edit a pair only with players inside the point limits?** The point restriction is checked when entries are edited.

**Where is the ⋮ menu in a league?** Leagues show icons instead: Player Details, Team Details, Delete, Forfeit and Delete & Refund.

**How do I edit the roster of a team in a league?** Click the **Player Details** icon on the team's row, add players with **Add Players** → **Add** (or **Loan**), set **Active** / **Reserve**, and save. The team's name, members, venues and images are edited under **Team Details**.

**How do I add a team logo in a league?** **Team Details** icon → **Upload Photos** → **Team Logo** (80 × 75 px).
