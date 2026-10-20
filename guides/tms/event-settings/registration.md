---
doc_id: tms.event-settings.registration
title: Registration settings page
routes:
  - tms/event-settings/registration/:event_id
aliases:
  - registration settings
  - registration step
  - registration page
  - registration form
  - create registration
  - how to create registration
  - registration setup
  - enable registration
  - category registration
  - player registration settings
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I open registration for a category?
  - What happens when a category is full?
  - How do I set the fee and refund rules?
  - Why can't players register for this category?
backend_sources:
  - gateway/src/routers/registration_router.py
  - gateway/src/routers/order_router.py
  - gateway/src/utils/registration_utils.py
  - tms/src/service/registration_service.py
  - tms/src/crud/registration_crud.py
  - tms/src/service/events_service.py (category eligibility, participant restriction)
  - tms/src/schema/registration_schema.py
  - user_role_service/src/service/auth_service.py (token verification)
  - user_role_service/src/service/role_service.py (roles, eligible roles)
  - user_role_service/src/service/user_service.py (list_all_users)
  - user_role_service/src/service/resource_permissions_service.py
source_files:
  - src/app/modules/tms/registration-settings/registration-settings.component.ts
  - src/app/modules/tms/registration-settings/registration-settings.component.html
  - src/app/modules/tms/registration-settings/entry-restriction-sidebar/entry-restriction-sidebar.component.ts
  - src/app/modules/tms/registration-settings/entry-restriction-sidebar/entry-restriction-sidebar.component.html
  - src/app/modules/tms/registration-settings/delegation-sidebar/delegation-sidebar.component.ts
  - src/app/modules/tms/registration-settings/delegation-sidebar/delegation-sidebar.component.html
---
# Registration settings page – user guide

This guide describes the **Registration** step of an event in the Stupa Event Management System (admin panel). On this page the organiser decides, for each category (class) of the event, who can register, when, at what fee and under which restrictions. It also explains how each setting is applied when someone registers.

## Where to find it

Open **Event** from the sidebar, then click **Registration** in the row of setup steps at the top of the page.

## Registration page: where it is and what it is for

- Page address: `/tms/event-settings/registration/<event id>`, for example `/tms/event-settings/registration/1358`.
- It is the **Registration** step in the row of event setup steps, after **Details**.
- Settings are saved **per category**. Each category of the event has its own registration settings.
- The event must already have categories. If it has none, the page shows "No records found" and the message "No participant types found for this event." Add categories in the **Add Class/Category** panel of the Details step first.
- Layout from top to bottom: the **Enable Delegation** button, the participant type dropdown and category tabs, the **Registration** toggle, the **Multiple Entry** toggle, and the setting cards.
- Each setting is a card showing the current values with an **Edit** button. Edit opens a side panel on the right; **Update** (or **Save**) in the panel stores it.
- The **Edit** buttons need Edit permission for "Player Registration Settings". Without it the buttons do not appear.

## Registration page: choosing participant type and category

- The dropdown at the top left lists **All** and the participant types that exist in this event (Singles, Teams, Doubles, Mixed Doubles).
- The tabs next to it list the categories of the chosen type. Use the left and right arrows to scroll. Click a tab to load that category's settings.
- With **All** selected, every category is listed and each tab shows a letter for its participant type (S, T, D, M).
- The cards always show the settings of the **selected category only**. Changing the tab changes all values on the page.
- Which cards appear depends on the participant type of the selected category (see "Registration page: which cards appear").
- The **Multiple Entry** toggle is only shown when a specific participant type is chosen in the dropdown, not with **All**.

## Registration page: which cards appear

Cards marked with a red `*` are the main settings to complete.

- **Verification*** – every participant type.
- **Pair Request*** – Doubles and Mixed Doubles only.
- **Date and Time*** – every participant type.
- **Fee & Refund Information*** – every participant type.
- **Gender and Age Restriction** – every participant type.
- **Point Restriction** – every participant type.
- **Players in Team** – Teams only.
- **Player Bifurcation** – Teams only.
- **Queue Settings** – every participant type.
- **Allow Registrations*** – every participant type.
- **Deregistration** – every participant type.
- **Entry Restriction** – every participant type.
- **Entry Format** – Teams only.

A card shows "On" or "Off" for togglees and "--" or an empty value when nothing is set.

## Registration toggle: opening and closing a category manually

- The **Registration** toggle under the category tabs turns registration on or off for the selected category.
- Text on the page: "The organizer can control registration settings and choose to manually close registrations in any category, regardless of registration deadlines."
- It is on by default. Turning it off saves immediately.
- While it is off, every **Edit** button on the cards is disabled. Turn it back on to change settings.
- While it is off, nobody can register for that category, even inside the registration dates. People see the category as not eligible with the reason "Registration is not active for this category".
- The toggle affects only the selected category. Other categories keep their own state.

## Applying a setting to other categories ("Apply to all classes")

Every side panel has **Apply to all classes** at the bottom left (the fee panel calls it **Apply to All Class**).

- Click the arrow next to it to open the list of the other categories. Tick the categories that should receive the same values, then click **Update**.
- The selected category is always included.
- The list contains the other categories shown in the tabs, so choose a participant type in the dropdown first to limit it. In the **Pair Request** panel the list only shows Doubles and Mixed Doubles categories.
- **Ticking the "Apply to all classes" checkbox itself applies the setting to every category of the event, including categories of other participant types.** To copy to only some categories, tick those categories individually and leave "Apply to all classes" unticked.
- For **Fee & Refund Information** and **Entry Format** the setting is applied only to the categories that are ticked.
- Only the fields of the panel you are saving are copied. Other settings of those categories are not touched.

## Verification card: who must be approved before they are registered

Panel text: "By enabling verification for a class, only participants who are verified by an admin can register for this class."

- **Enable Verification?** – Yes or No.
- **Verification Type** (only when Yes):
  - **One-way Verification (Admin)** – one verifier.
  - **Two-way Verification** – two verifiers.
- **Select Verifiers*** – for Verifier 1 choose a role, then choose a user of that role in **Select User**. For Two-way, do the same for Verifier 2. The user list loads more names as you scroll.
- Errors: "Verifier 1 is required", and for Two-way "Verifier 2 is required". The panel does not save until these are chosen.
- With One-way, any Verifier 2 that was set before is removed when you save.
- With verification on, a registration waits for the verifier(s) to accept it. With it off, registrations are accepted directly.
- Important note shown in the panel: "In case of direct player registration default partner request will be enabled. This setting will not be applicable for direct player registration."
- The card shows Verification On/Off, the Verification Type and the Verifier(s) roles.

## Pair Request card (Doubles and Mixed Doubles)

This card controls how players find a partner and whether a pairing must be verified.

- **1. Partner Request ?** – Yes or No. Yes allows an entity to request a player from another entity when it cannot form a full pair.
- **Additional Settings for Self Registration** – a checkbox that appears when Partner Request is Yes. It can only be ticked if the **Player** role is selected in **Allow Registrations**; otherwise it is greyed out. If Player is the only role allowed to register, this option is applied automatically and the checkbox is not shown.
- **1.1 Select Input Type** (shown with self-registration settings):
  - **Select from Player List** – "Displays the complete roster of players registered in the system".
  - **Request a Partner** – "System provides a text box to enter the partner's name to pair up with".
- **2. Pair Verification** – Yes or No. Only shown when Partner Request is Yes. It is disabled when Player is the only role allowed to register.
- **3. Verifier** – when Pair Verification is Yes, choose the role where the verification is sent.
- If Partner Request is No, Pair Verification is saved as off.
- The card shows Partner Request On/Off, Pair Verification On/Off and the Verifier.
- A pair occupies a place in the category only once the pair is confirmed. A single player still waiting for a partner does not take a place and is not put in the queue.

## Date and Time card: registration opening and closing

Panel text: "Mention the day and time the registration should be open. This will automatically show this class as open for registration."

- **Open Registration on** – date and time registration starts.
- **Close Registration on** – date and time registration ends.
- You enter times in your own time zone; the card shows them in your time zone as `YYYY-MM-DD, HH:mm`.
- Before the opening time, registration is refused with "Registration Not Started" and the category shows "Registration has not started yet for this category".
- After the closing time, registration is refused with "Registration Closed" and the category shows "Registration is closed for this category".
- A date left empty is not checked: no opening time means registration is open immediately; no closing time means it never closes by date.
- Clearing a date in the panel and saving removes that limit.
- The page does not check that the closing time is after the opening time. If you swap them, the category is never open. Check both values.
- These dates also drive the event's status in **Auto** mode: REGISTRATION OPEN while any category is inside its dates, REGISTRATION CLOSED after the last closing time.
- The manual **Registration** toggle overrides the dates: off means closed.

## Fee & Refund Information card: setting the fee

- **Set Currency** – shown but not editable. The currency is fixed for your organisation.
- **Enter Registration Fee** – the fee for this category. Whole numbers only: decimals are dropped when saving (for example `12.50` is saved as `12`). An empty fee is saved as `0`.
- The panel header shows the participant type and whether registration is currently **Open** or **Closed** for this category (based on the Date and Time card).
- The card shows Currency and Fee. "--" means no fee has been set.
- For Doubles and Mixed Doubles the fee is for the pair; each player is shown half of it when registering.
- Click **Save** to store. The message "Registration Setting Create" confirms the save.

## Fee & Refund Information card: refund rules

Turn on **Enable Refund Options** to give money back to participants who withdraw. Then choose a type:

- **Full Refund** – "100% refund if cancelled before the deadline." Choose one **Withdraw Before** date.
- **Partial Refund** – "Refund amount varies based on cancellation time or conditions." Add one or more rows, each with a **Withdraw Before** date and a **Refund %**. Use **Add Condition** for another row and the delete icon to remove one (the last remaining row cannot be removed).

Rules:
- A Withdraw Before date can be no later than the day before the event's Start Date. Later dates are not selectable.
- Refund % must be a whole number from 0 to 100. Other values are cleared.
- Later withdrawal dates cannot have a higher percentage than earlier ones.
- Two rows with the same date must have the same percentage.
- A withdrawal counts as "before" up to the end of the chosen day.
- With refunds switched off, no refund rule is stored for the category.

## Fee & Refund Information card: error messages

- "Choose a withdraw-before date for full refund." – Full Refund is selected without a date.
- "Enter a valid withdraw-before date." – the typed date is not a real date.
- "Withdraw-before date must be on or before the last allowed day before the event starts (same limit as the calendar)." – the date is on or after the event's Start Date.
- "Add at least one withdrawal date and refund %." – Partial Refund has no complete row.
- "Enter a withdrawal date and refund % for the current row before adding another." – you clicked Add Condition while the last row is incomplete.
- "Refund % must be between 0 and 100."
- "Refund % can't increase for later withdrawal dates."
- "Same withdrawal date: refund % must match on every row."
- "Error updating settings" – the server could not save; try again.

## Gender and Age Restriction card

- **Select Gender** – Male, Female or Mixed.
- **Add Age Restriction (Born Before Year)** – a date. Players born after this date are not eligible.
- **Add Age Restriction (Born After Year)** – a date. Players born before this date are not eligible.
- How it is applied when registering:
  - Gender Male or Female: a player of another gender is not eligible, with the reason "Gender requirement: Male" or "Gender requirement: Female". **Mixed** means no gender check.
  - Born Before: reason "Born before DD/MM/YYYY". Born After: reason "Born after DD/MM/YYYY".
  - A player without a date of birth or gender on their profile is not checked against that rule.
- To allow an age range, set Born After to the earliest birth date and Born Before to the latest birth date.
- The page does not check that the two dates make sense together. If Born After is later than Born Before, nobody is eligible.
- Clearing a date and saving removes that restriction.
- When a category is added to the event it starts with the gender and birth dates of its class.

## Point Restriction card

Panel text: "Set a Minimum and Maximum Point Restriction for this class of participants".

- **Point Restriction Type** – not shown for Singles. For Teams, Doubles and Mixed Doubles choose **Individual Player** (each player's points are checked) or **Pair-Team** (the pair or team is checked as a whole). The default is Individual Player.
- **Minimum Points** and **Maximum Points** – digits only. Typing anything else shows "Please enter a valid non-negative number." Negative values are also rejected by the server.
- How it is applied: a player with fewer points than the minimum is not eligible ("Points below minimum required"); a player with more than the maximum is not eligible ("Points above maximum allowed").
- A player with no ranking points counts as 0 points, so any minimum above 0 excludes them.
- A maximum of 0 means no upper limit.
- Clearing a field and saving removes that limit.
- The page does not check that minimum is lower than maximum.

## Players in Team card (Teams)

- **Minimum number of Player in a Team** and **Maximum number of Player in a Team**.
- A team registering with fewer or more players is refused: "Min member length does not match with required members for this category" or "Max member length does not match with required members for this category".
- The maximum must be set before **Player Bifurcation** can be opened.
- After registration, a player cannot be removed from a team if that would leave it below the minimum.

## Player Bifurcation card (Teams)

Bifurcation splits a team's players into groups with a fixed number of each.

- The panel only opens after **Maximum Players** is set in **Players in Team**. Otherwise the message "Please fill settings - max members in a team." appears.
- **Enable Player Bifurcation?** – Yes or No.
- Three numbers: Federation-Registered Players, Unaffiliated Players, and Passport-Eligible Players in a team. The exact names of these three groups can differ per organisation.
- A team whose players do not match these numbers is refused with "Bifurcation data mis-match".
- The card shows Player Bifurcation On/Off and the three numbers.

## Queue Settings card: category capacity and the queue

- **Minimum** and **Maximum** number of Players, Teams or Pairs that can participate in the class (the word depends on the participant type).
- **What happens when the category is full:** a registration that arrives after the maximum is reached is not rejected. It is placed in the **Queue** as a reserve.
- Queued entries do not take a place. If a place becomes free the organiser can move an entry out of the queue from the Players screen.
- A registration made by the main administrator account is not auto-queued, so the organiser can go over the maximum on purpose.
- No maximum means unlimited places.
- For Doubles and Mixed Doubles only confirmed pairs count towards the maximum.
- Clearing a field and saving removes the limit.

## Allow Registrations card: which roles can register

- **Select who can send registrations for this class** – tick one or more roles (for example Player, Club, Member Association). The roles offered are set up by your organisation.
- When someone tries to register, their role must be one of the ticked roles. Otherwise the category is shown as not eligible with "Role does not have access to register for this category".
- **Select at least one role.** If no role is ticked, nobody can register for the category.
- The card shows the **Enabled Roles**.
- The roles chosen here are the roles offered in the **Entry Restriction** panel.
- The **Player** role here also controls the self-registration options in the **Pair Request** panel.

## Deregistration card

- **Enable deregistration?** – Yes or No. Off by default.
- With Yes, participants can withdraw (deregister) themselves from the category.
- With No, a withdrawal attempt is refused with "De-registration Not available".
- Refunds for withdrawals follow the refund rules in the **Fee & Refund Information** card.

## Multiple Entry toggle

The **Multiple Entry** toggle (top right, shown when a specific participant type is chosen) decides whether one player can be entered in more than one category of that participant type. It applies to the whole event, not to one category.

- **Singles**: turning it on opens a dialog: "You have enabled multiple registrations in different categories for the tournament. Please choose the number of categories for which you want to accept multiple registrations." Choose **2**, **3** or **all**, then **Save**. **Cancel** turns the toggle back off.
- **Teams, Doubles, Mixed Doubles**: the toggle saves immediately.
- With it off, a player who is already registered in one category of that type cannot be registered in another: "Participant cannot be registered in multiple categories when multi-entry is disabled".
- With it on for Singles and a limit of 2 or 3, registering a player in more categories than the limit is refused with a message naming the player and the allowed number.
- Success message: "Participant Restriction Setting Updated Successfully".
- If the change cannot be saved the page always shows "Some Error Occured", whatever the cause. The usual causes are a missing "Edit Registration Settings" permission or an expired session.

## Entry Restriction card: limits per role

Entry Restriction limits how many entries each role (and optionally each user) can make in a category.

1. Click **Edit** on the card and turn on **Enable entry restriction**.
2. The roles listed are the roles ticked in **Allow Registrations**. Click the arrow on a role.
3. **Default Value** – the maximum entries for every user of that role, from 0 to 99. A new role starts at 1 (2 for Mixed Doubles).
4. **Exceptions** – below the default, search for a specific user and give that user a different limit.
5. Use **Apply to all classes** to choose other categories, then **Update**. **Go back** returns to the role list.

Rules and messages:
- "Invalid input. Please enter a number between 0 and 99."
- For Mixed Doubles the number must be even: "Invalid input. Please enter an even number."
- "Cannot update the event! Please check the input values." – a value is out of range.
- Turning the toggle off and clicking **Update** removes all limits.
- When a user registers beyond their limit: "Max entries allowed for category <name> is <number>. Cannot proceed."
- The card shows Enabled On/Off and the roles that have a limit.

## Entry Format card (Teams)

- **Select Entry Format**:
  - **All Players** – no loan players.
  - **Hierarchy** – shows the loan player options.
- With Hierarchy:
  - **Enable Loan Players** – toggle.
  - **Loan Fee** – shown as **Shared Membership Fee** on the card. A number; empty is saved as 0.
  - **Select Verifiers** – appears when loan verification is two-way: choose **Select Verifier 1** and **Select Verifier 2**. Errors: "Verifier 1 is required", "Verifier 2 is required".
- **Select Categories** (bottom left) – choose other Teams categories that should get the same entry format. The current category is always included.
- Click **Update**. Success message: "Settings updated successfully". Failure: "Error updating settings".
- The card shows the Entry Format, Enable Loan Player (Yes/No) and the Shared Membership Fee.

## Enable Delegation button and Delegation Setting panel

The **Enable Delegation** button at the top opens the **Delegation Setting** panel. Delegation applies to the whole event.

- **Enable Delegation** toggle – "Users can manage delegation lists, providing chosen individuals with full data access for registration purposes".
- Choose one option:
  - **Delegation Players / Other Role Users** – "Restricts the entry flow completely. Senders can only select users explicitly included in the delegation list. No other directory lookup is allowed."
  - **All Players / Other Role Users** – "Expands accessibility. Senders can select from the delegation list AND search/add any user from the entire system directory directly on the Registration, Accommodation, and Travel screens."
- Click **Update** (it shows "Updating..." while saving). On success the panel closes without a message.
- Saving delegation needs Edit permission on "Event Access", which is a different permission from the one for the registration cards. Without it the save fails with "Access Denied".
- If the save fails, the toggle turns back off and the error is shown:
  - "Delegation Show Users Required" – delegation was enabled without one of the two options chosen.
  - "No Event Found" – the event was deleted.
  - "Something went wrong" – the server gave no reason; try again.
- "Unable to load delegation state" means the current setting could not be read; reopen the panel.
- The first time delegation is enabled without choosing, the restrictive option (Delegation Players) is used.

## Registration page: success messages for each action

Each action on the page saves separately. What you see when it works:

- **Update on a card panel** (Verification, Pair Request, Date and Time, Gender and Age Restriction, Point Restriction, Players in Team, Player Bifurcation, Queue Settings, Allow Registrations, Deregistration, Entry Restriction) – "Registration Setting Create". The panel closes and the cards reload.
- **Save in Fee & Refund Information** – "Registration Setting Create".
- **Update in Entry Format** – "Settings updated successfully".
- **Registration toggle** – no message. The cards reload with the new state.
- **Multiple Entry toggle** – "Participant Restriction Setting Updated Successfully".
- **Update in Delegation Setting** – no message. The panel closes.

Each panel saves only its own fields. Saving one card never changes the values of another card. "Registration Setting Create" is shown both the first time a setting is saved and when it is changed later.

## Registration page: error messages when saving and what they mean

When a save is refused, the server's message appears at the bottom of the screen.

- **"Unauthorized Access"** – you are not signed in any more, your session expired, or your sign-in belongs to a different organisation than this site. Sign in again.
- **"Access Denied"** – your role may not change these settings for this event. Saving a card needs Edit permission on both "Player Screen" and "Edit Registration Settings". The Multiple Entry toggle needs "Edit Registration Settings". Delegation needs "Event Access".
- **"Invalid …" followed by a field name** – a value has the wrong type or range, for example a negative Minimum Points or Maximum Points. Up to three field names are listed. Correct those fields and save again.
- **"Invalid Request Format"** – the save could not be read by the server. Reload the page and try again.
- **"Some Error Occurred"** – an unexpected server failure. Try again; if it repeats, report it.
- **"Error updating settings"** – shown by the Fee and Entry Format panels when the server gave no message.
- **"Provided Event Id is Invalid"** – the event no longer exists (Multiple Entry toggle).
- A message without text usually means the connection to the server was lost. Check your network and reload.

## Registration page: what loads when you open it and messages when loading fails

Opening the page, or choosing another category, loads data in this order:

1. The event's participant types and categories. If the event has none: "No participant types found for this event." and "No records found". If the request fails: "Some Error Occured".
2. The registration settings of the selected category. If the category is not part of the event any more: "Category registration settings not found". Reload the page; if it stays, add the category again on the Details step.
3. The roles of your organisation (for the Verifier dropdowns), the roles that may register (for Allow Registrations), and the event's Start Date (for the latest Withdraw Before date). If one of these fails there is no message: the dropdown or list is simply empty, or any Withdraw Before date can be picked. Reload the page.
4. The users of a role, when you pick a role as verifier. If the list is empty, that role has no active users.

A loading animation covers the page while settings load. If your session has expired you are sent to the sign-in page.

## Registration page: who appears in the role and user lists

- **Verifier role dropdowns** (Verification, Pair Request, Entry Format) list the active roles of your organisation. A role that has been deactivated is not offered.
- **Select User** (next to a verifier role) lists users of that role whose account is active and already approved. A user who is still waiting for approval, was rejected, or was deactivated does not appear. The list shows 25 names at a time and loads more as you scroll.
- **A person is missing from Select User?** Check that their account has that exact role, is approved and is active. If they hold a different role, choose that role first.
- **Allow Registrations** lists only the roles your organisation has given permission to register for events. If a role is missing there, an administrator must enable registration for that role in role management. If no role has that permission, the list is empty and nobody can be allowed to register.
- **Entry Restriction** lists the roles ticked in Allow Registrations, without the administrator role. The users offered for exceptions follow the same rule as Select User.

## Registration page: sign-in sessions and permissions

- A sign-in lasts a limited time (two days by default). After it ends, any save fails with "Unauthorized Access" and you are sent to the sign-in page. Sign in again; unsaved changes in an open panel are lost.
- "Unauthorized Access" also appears when the account was deleted or restricted, or when the sign-in belongs to another organisation than the site you are on.
- Edit permissions are given per event. Having Edit on one event does not give it on another.
- The person who creates an event receives its permissions automatically. Other users must be given access on the event's **Access-Control** step.
- A permission can be limited to a period. Outside that period the same action fails with "Access Denied".
- Users with Live Match Centre access to the event are also allowed to change these settings.

## How registration settings are checked when someone registers

When a player or entity opens the event to register, each category is marked eligible or not eligible. A category is **not eligible** when any of these is true, and the reason is shown:

1. The **Registration** toggle is off – "Registration is not active for this category".
2. It is before the opening time – "Registration has not started yet for this category".
3. It is after the closing time – "Registration is closed for this category".
4. Their role is not ticked in **Allow Registrations** – "Role does not have access to register for this category".
5. Date of birth outside the age restriction – "Born before …" or "Born after …".
6. Gender does not match – "Gender requirement: Male/Female".
7. Points outside the point restriction – "Points below minimum required" or "Points above maximum allowed".

At the moment of registering the server also applies: the registration dates again, entry limits per role, multiple-entry rules, team size and bifurcation, and the category maximum (overflow goes to the Queue).

## Frequently asked questions about the Registration page

**How do I open registration for a category?** Select the category, make sure the Registration toggle is on, set Open and Close dates in the Date and Time card, and tick at least one role in Allow Registrations.

**Why can't players register for this category?** Check, in order: the Registration toggle is on, the current time is between the Open and Close dates, the player's role is ticked in Allow Registrations, and the gender, age and point restrictions fit the player.

**Why are all the Edit buttons disabled?** The Registration toggle is off for this category. Turn it on to edit.

**Why don't I see any Edit buttons?** Your role has no Edit permission for Player Registration Settings.

**What happens when a category is full?** New registrations go to the Queue instead of being rejected. Set the limit in Queue Settings.

**How do I limit how many entries a club can make?** Use the Entry Restriction card: enable it, open the role and set its Default Value, with exceptions per user if needed.

**How do I let a player enter more than one category?** Choose the participant type in the dropdown and turn on Multiple Entry. For Singles choose 2, 3 or all categories.

**How do I copy settings to other categories?** In the panel, open Apply to all classes, tick the categories and click Update. Ticking "Apply to all classes" itself copies to every category of the event.

**Can I use decimals in the fee?** No. The fee is saved as a whole number.

**Why can't I pick a later Withdraw Before date?** The latest allowed date is the day before the event starts.

**Why does the page say "No participant types found for this event"?** The event has no categories. Add them on the Details step.

**Why can't I open Player Bifurcation?** Set Maximum Players in the Players in Team card first.

**Why is Additional Settings for Self Registration greyed out?** The Player role is not ticked in Allow Registrations.

**Why is the Pair Request card missing?** It only appears for Doubles and Mixed Doubles categories.

**Why is the Multiple Entry toggle missing?** It is hidden while All is selected in the participant type dropdown. Choose a specific type.

**Why does the event not show as Registration Open?** In Auto status mode at least one category must be inside its Open and Close dates.

**Can participants withdraw themselves?** Only if Deregistration is set to Yes for the category. Otherwise they see "De-registration Not available".

**Why does a player with no ranking fail the point restriction?** A player without points counts as 0, which is below any minimum above 0.

**What does "Category registration settings not found" mean?** The selected category is no longer part of this event, so it has no registration settings. Reload the page. If the message stays, add the category again in the Add Class/Category panel of the Details step.

**What does "Registration Setting Create" mean?** It is the success message. The setting was saved, whether it was new or a change to an existing setting.

**What does "Access Denied" mean on the Registration page?** Your role may not change registration settings for this event. Ask an administrator for Edit permission on "Player Screen" and "Edit Registration Settings".

**What does "Unauthorized Access" mean on the Registration page?** Your session expired or is not valid for this organisation. Sign in again.

**Why does the Multiple Entry toggle show "Some Error Occured"?** The change was not saved. The usual causes are a missing "Edit Registration Settings" permission or an expired session.

**Why do I get an "Invalid" error when saving points?** Minimum Points and Maximum Points cannot be negative. Enter 0 or a positive whole number.

**Why is a user missing from the Select User list for a verifier?** Only active, approved users of the chosen role are listed. Check the person's role, approval and active state.

**Why is a role missing from Allow Registrations?** Only roles that your organisation has given permission to register are listed. An administrator must enable it for that role.

**How long does my session last on this page?** Two days by default. After that, saving shows "Unauthorized Access" and you must sign in again.
