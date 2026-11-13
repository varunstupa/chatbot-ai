---
doc_id: tms.navigation
title: Sidebar and navigation – the event modules in the left sidebar and where each feature is
routes: []
aliases:
  - sidebar
  - side bar
  - left menu
  - side menu
  - main menu
  - navigation
  - where is
  - how to go to
  - how do i open
  - event modules
  - module list
  - where can i find
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - Which modules are in the sidebar?
  - Where do I find streaming?
  - How do I open the registration settings?
  - Where is the Players page?
  - Why can I not see Rankings in the sidebar?
  - Where do I set up payment and invoices?
backend_sources: []
source_files:
  - src/app/modules/tms/event-org-sidebar/event-org-sidebar.component.ts
  - src/app/modules/tms/event-org-sidebar/event-org-sidebar.component.html
  - src/app/modules/tms/events-settings/events-settings.component.ts
  - src/app/modules/tms/tms.module.ts
  - src/app/modules/tms/schedular/call-out-scheduler.guard.ts
  - src/app/modules/admin/admin-sidebar/admin-sidebar.component.ts
  - src/app/modules/admin/admin-sidebar/admin-sidebar.component.html
  - src/assets/ConstData/adminSidebar.ts
  - src/app/core/services/access-control-service/access-control.service.ts
  - src/app/app.routes.ts
  - src/assets/i18n/en.json
  - src/assets/i18n/tenant-label-overrides.json
---
# Sidebar and navigation

The admin app has two sidebars. Outside an event, the **admin sidebar** lists the organisation's areas (Overview, Competitions, Users & Roles and so on). Inside an event, the **event sidebar** lists the event modules. Click a module to open it. The event sidebar title is **Event Management System** (shortened to **EMS** when the sidebar is collapsed). The modules below are listed in the order the sidebar shows them.

## Sidebar modules
1. **Event** – the event setup. It opens on the Details step; the other setup steps are in the row at the top of the page (see below).
2. **Players** – the players, pairs and teams of each category.
3. **Fixtures/Results** – stages, groups, knockout draws, results and standings.
4. **Schedule** – placing matches on tables and times, and assigning umpires. For a tournament whose scheduling method is Match Call Out, it opens the Match Call Out scheduler instead; league events always open the normal scheduler.
5. **Scoring and Streaming** – entering scores, walkovers, and turning on streaming.
6. **Awards and Standing** – stage and cumulative standings, prizes and awards.
7. **Printing** – score sheets, fixtures, schedules, back numbers and player lists.
8. **Rankings** – ranking and rating points of the categories. The label is **Ratings** when the organisation uses the rating system, and **Rankings and Ratings** when it uses both.
9. **Display Settings** – what appears on table and LED displays.
10. **Leaderboard** – team and player standings.
11. **Export/Share Results** – the downloads of exported files, and the results sync.
12. **Request Management** – venue requests.
13. **Notification** – notifications to users.

## Modules that are not always shown
- **Rankings** shows only when your organisation has rankings turned on.
- **Leaderboard** shows only when your organisation has the leaderboard turned on for that event type (tournament or league).
- **Request Management** shows only for league events.
- **Notification** shows only when your organisation has user notifications turned on.
- The other modules are always in the sidebar.
- Each module opens for the event you are working in. Without an event, a module shows the "No record found" state with a **Go to Event** button.

## Event sidebar: footer buttons
The bottom of the event sidebar has three buttons:

- **Back** (arrow) – leaves the event and returns to the events list you came from (Manage Tournaments or Manage Leagues), keeping the chosen language.
- **Select language** (globe) – opens the language list: English, Norweigan, Slovenian, Swedish, Spanish, Czech, Danish, German, French and Italian. In the Padel app only English, German, French and Italian are offered. The tooltip shows the current language.
- **Collapse sidebar** / **Expand sidebar** – switches between the full sidebar and an icon-only rail. In the rail, hovering an icon shows the module name. The choice is remembered in the browser.

## Event module: the setup steps
Open **Event** from the sidebar. The page shows a row of numbered setup steps at the top. Click a step to open its page. The steps shown depend on your organisation's settings, and Venue Management shows only for league events. The steps are:

- **Details** (the event details, categories and venues)
- **Registration**
- **Playing Order**
- **Draw Settings**
- **Venue Management** (league events)
- **Payment & Invoice**
- **Umpire Settings**
- **Referee Settings**
- **Day Planner**
- **Game Play**
- **Accommodation**
- **Travel**
- **Print Settings**
- **Access-Control**
- **Documents & Sponsors**

## Admin sidebar (outside an event)
Outside an event, the admin sidebar shows **Overview** (a direct link) and these groups. Click a group to open it; only one group is open at a time.

- **Competitions**: **Manage Tournaments**, **Manage Leagues**, **Ranking & Rating**, **Travel & Accommodation**, **Settings** (competition settings).
- **Users & Roles**: **Manage Role & Access**, **Manage Users**, **Memberships**.
- **Finance**: **Invoices**, **Payments**.
- **Live & Streaming**: **OTT**, **Broadcast Matches**.
- **Dashboard & Reports**: **Membership Dashboard**, and **Website Dashboard** (shown only when the organisation has it turned on; otherwise it is not in the list at all).
- **More**: **Request**, **Notifications**, **Season**, **Downloads**.

To work on an event, open **Manage Tournaments** or **Manage Leagues** and open the event; the event sidebar then replaces the admin sidebar.

## Admin sidebar: locked items and account menu
- An item with a lock icon ("Locked") cannot be opened. It is locked when your role has no read permission for that area (set on **Manage Role & Access**), or when the organisation has the feature turned off: **Ranking & Rating** needs rankings, **Memberships** needs memberships, **Invoices** needs invoices and **Notifications** needs user notifications. Permission changes show without a reload.
- The account card at the bottom shows your name and role. Clicking it opens **Switch To Web** (opens the public website in a new tab, signed in), the language list, and **Log out**.
- Some organisations see a different label; for example one organisation sees **Ranking & Elo Points** instead of **Ranking & Rating**.

## How to reach common features
- **Set up registration:** open **Event** from the sidebar, then click **Registration** in the setup steps.
- **Set up payment and invoices:** open **Event** from the sidebar, then click **Payment & Invoice** in the setup steps.
- **Enable streaming for a match:** open **Scoring and Streaming** from the sidebar, click the **Streaming** tab, then click **Enable Streaming** on the match.
- **Enter a score:** open **Scoring and Streaming** from the sidebar and use the **Scoring** tab.
- **Add players:** open **Players** from the sidebar.
- **Create a fixture:** open **Fixtures/Results** from the sidebar.
- **Schedule matches:** open **Schedule** from the sidebar.
- **Print score sheets:** open **Printing** from the sidebar.
- **Set ranking or rating points of a category:** open **Rankings** from the event sidebar.
- **Change the organisation's ranking or rating settings:** open **Ranking & Rating** under **Competitions** in the admin sidebar.
- **Leave the event:** click **Back** at the bottom of the event sidebar.

## Frequently asked questions

**Which modules are in the sidebar?** Event, Players, Fixtures/Results, Schedule, Scoring and Streaming, Awards and Standing, Printing, Rankings, Display Settings, Leaderboard, Export/Share Results, Request Management and Notification. Some are shown only when your organisation or event type uses them.

**Where do I find streaming?** Open Scoring and Streaming from the sidebar, then click the Streaming tab.

**How do I open the registration settings?** Open Event from the sidebar, then click Registration in the setup steps at the top.

**Why can I not see Rankings or Leaderboard?** They show only when your organisation has them turned on. The Leaderboard is turned on separately for tournaments and for leagues.

**Why is Rankings called Ratings in my sidebar?** The label follows your organisation's system: Ratings for the rating system, Rankings and Ratings when both are used.

## Frequently asked questions: Sidebar and navigation – more questions
**Why is a menu item locked in the admin sidebar?** Your role has no read permission for it, or the feature is turned off for your organisation. Ask an administrator to check **Manage Role & Access**.

**How do I go back to the events list from an event?** Click **Back** at the bottom of the event sidebar.

**How do I make the sidebar smaller?** Click **Collapse sidebar** at the bottom of the event sidebar; click **Expand sidebar** to open it again.

**Where is the Players page?** Open **Players** from the sidebar.

**Where do I set up payment and invoices?** Open **Event** from the sidebar, then click **Payment & Invoice** in the setup steps at the top.
