---
doc_id: tms.players.adding
title: Players page – adding singles players and fixing add errors
routes:
  - tms/players/:event_id
aliases:
  - add player
  - temporary player
  - team-up
  - ineligible players
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I add a player to a category?
  - What is a temporary player?
  - Why is a player in the Ineligible players list?
  - How do I pair two singles into a doubles team?
  - What does the Self toggle do?
  - Why does adding a player say "Event payment settings are required"?
backend_sources:
  - gateway/src/routers/registration_router.py (register_event_participants, create_team_up, configure_category_registration_settings)
  - gateway/src/handlers/registration/helpers.py (validate_event_payment_settings)
  - gateway/src/routers/user_router.py (create_temporary_user_role, update_user_and_participant)
  - tms/src/service/registration_service.py (create_team_up)
  - tms/src/crud/registration_crud.py (validate_manual_pair_participants_ready)
source_files:
  - src/app/modules/tms/players/players.component.ts
  - src/app/shared/components/player-registration-form/player-registration-form.component.html
  - src/app/modules/tms/players/team-player-list/team-player-list.component.ts
  - src/app/modules/tms/players/team-player-list/team-up-popup/team-up-popup.component.ts
---
# Players page – adding singles players and fixing add errors

This guide explains how to add singles players and temporary players on the **Players** page, what the server checks when you add anyone, how to fix the error messages, and how to pair players who registered alone (Team-up). Adding and editing pairs and teams is described in the guide "Players page – pairs and teams".

## Adding singles players on the Players page

1. Select a singles category tab and click **Add**. The **Add Player** side panel opens.
2. Choose the **Licensed** tab (players with an account and licence) or **Unlicensed** (temporary players).
3. Search with **Search**; with **Search by** you can search by player or by organisation.
4. Click **Add** on each player you want; it turns into **Remove**. You can pick several players.
5. The chosen players are listed in the panel; removing one asks "Are you sure you want to remove this player?".
6. Click **Add** at the bottom to register them: "Participants Registered Successfully".

- The list shows each player's gender, date of birth, member association and club, and points.
- A player chosen twice gives "Player already exists.".
- **Add** on the toolbar is greyed out when no category is selected or the **Registration** toggle of the category is off (on the **Registration** page).

## Eligible and ineligible players

- By default the panel lists **eligible** players – those who match the category's rules.
- Click **Ineligible players** to see the players who do not match; click **Eligible players** to go back. Ineligible players cannot be added.
- In organisations that register by hierarchy, first pick the **role** (for example member association) and then the **parent** ("Select Parent"); the list then shows that organisation's players.

## Temporary players: adding a player without an account

1. In the **Add Player** panel (or the pairs or team panel) click **Add Temporary Player**.
2. **International Player** / **Choose Player type** – mark the player as international if needed.
3. Fill in the fields your organisation requires (they are set per organisation; fields with * are required).
4. **Member Association**: **Old** (pick an existing one) or **New** (type a new name). **Club**: **Old** or **New** the same way.
5. Click **Submit**. Use **Back** to return to the list.

- "Existing Club cannot be added in New MA" – a new member association needs a new club.
- "Please Wait For Verification Add Members" – your own account is not verified yet, so you cannot create players.
- To change a temporary player later: ⋮ on the row → **Edit**, change the form and click **Update** ("Please Wait For Verification Edit Members" if your account is not verified).

## The Self toggle in the pairs and teams panels

- The **Self** toggle in the **Add Pairs** and team panels is saved for the category at once: "Settings updated successfully" (or "Failed to update settings", and the toggle turns back).
- With **Self** on, every player of a pair or team gets an individual entry and pays their own fee. With **Self** off, the pair or team is one entry with one order.

## Players added to the unpaid list

When the event takes payment **online**, players you add are not added to the category list straight away. The message **Player Added** says: "Players added to unpaid list. Payment link sent via email. Payment can also be completed on the OTT platform. After payment, players will be added to the respective category list." See **Unpaid Players** in the queue and delete guide.

## Error "Event payment settings are required" when adding players

Adding players, pairs or teams on the Players page fails with "Event payment settings are required" when the event's payment setup is incomplete:
1. No payment settings have been saved for the event (no **Payment Type** saved).
2. **Payment Type** is **Online** but no receiving account is selected.
3. You are the event organiser and no **Raised To** role is selected (invoice settings are missing).

How to fix it:
1. Open the event's **Payment & Invoice** step (event setup).
2. In **Payment and Invoices** select at least one **Raised To** role.
3. Choose **Enable Invoicing for this Event?** (Yes or No) and the **Payment Type**: **Cash** or **Online**. For **Online** also select the receiving account.
4. Click **Save**, come back to the Players page and add the players again.

## Other errors when adding players and how to fix them

When you add players from the Players page, the registration dates, the role access and the point restriction of the category are not checked. These checks still apply:
- "Registration Not Enabled" – the **Registration** toggle of the category is off. Turn it on on the **Registration** page.
- "Role Not Eligible For Registration" – no role is ticked in **Allow Registrations** on the **Registration** page.
- "Category Registration Settings Not Found" – the category's registration settings were never saved. Save them on the **Registration** page.
- "Participant Already Exists" / "All Participants Already Registered" – the player is already in the category.
- "Participant cannot be registered in multiple categories when multi-entry is disabled" – the player is in another category of this type; turn on **Multiple Entry** on the **Registration** page.
- "Player Max Categories Reached" – the player has reached the number of categories allowed by **Multiple Entry**.
- "Players Already Registered With Another Pair" – a player is already in another pair.
- "Participants Registered Successfully Except …" – some were added, the ones named were not.

## Team-up: pairing players who registered alone

In doubles, mixed doubles and team categories the **Singles** tab lists players who registered alone (columns **Participant name**, **Requested Partner**, **Back No.**, **Participant No.**, **Seeding**, **State**, **Club**).

1. Tick the players and click **Team-up**.
2. Doubles and mixed doubles: the popup shows "Participant 1" and "Participant 2"; the pair is named "player A / player B". Teams: "You are about to create a team with N members" – enter **Create a team name**.
3. Click **Save**: "Team Created Successfully". The new entry appears on the **Team-up** tab, already accepted.

From the **Singles** tab you can also **Delete** or **Delete & Refund** single entries.

## Team-up rules and messages

- "Please select at least 2 players to team up" – tick at least two players.
- "You can select maximum 2 players for team up" – doubles and mixed doubles take exactly two.
- "Both participants must be paid before forming a pair" – both players need a paid registration.
- "Each participant must be a single entrant before pairing" – a player is already in a pair.
- "Invalid or inactive participant IDs for pairing" – a player was deleted or is in another category.
- "Duplicate participant in pairing request" – the same player was chosen twice.

## Frequently asked questions about adding players

**How do I add a player to a category?** Select the category, click **Add**, click **Add** on the players, then **Add** at the bottom.

**How do I add a player who has no account?** **Add** → **Add Temporary Player**, fill the form, **Submit**.

**Why can I not add a player?** The player is in the **Ineligible players** list, the **Registration** toggle of the category is off, or the server refused it – see the error message.

**Why did the player not appear in the list after adding?** The event takes payment online: the player is on the unpaid list until paid.

**How do I pair two players who registered alone?** Open the **Singles** tab, tick both players, click **Team-up**, then **Save**.

**Why does Team-up say both participants must be paid?** Pairs can only be formed from players whose registration is paid.

## Frequently asked questions about errors when adding players

**Adding a player shows "Event payment settings are required". How do I fix it?** Open the event's **Payment & Invoice** step, select a **Raised To** role, choose the **Payment Type** (and the account for Online), click **Save**, then add the player again.

**Adding a player shows "Registration Not Enabled".** Turn on the **Registration** toggle of the category on the **Registration** page.

**Does the registration closing date stop me adding players here?** No, organisers can add players on the Players page outside the registration dates, as long as the **Registration** toggle is on.

**Why "Please Wait For Verification Add Members"?** Your own account is still waiting for verification; temporary players can be created once it is accepted.
