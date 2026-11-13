---
doc_id: tms.schedular.call-out
title: Match Call Out scheduler – call matches to free tables, auto-queuing and the table board
routes:
  - tms/schedular/call-out/:event_id
aliases:
  - match call out
  - call out scheduler
  - auto-queuing
  - dispatch next
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How does the Match Call Out scheduler work?
  - How do I start auto-queuing?
  - Why is a match shown as Waiting?
  - How do I call a match to a free table?
source_files:
  - src/app/modules/tms/tms.module.ts
  - src/app/modules/tms/schedular/call-out-scheduler.guard.ts
  - src/app/modules/tms/schedular/call-out-scheduler/call-out-scheduler.component.html
  - src/app/modules/tms/schedular/call-out-scheduler/call-out-scheduler.component.ts
  - src/app/modules/tms/schedular/call-out-scheduler/call-out-auto-queue-bar/call-out-auto-queue-bar.component.html
  - src/app/modules/tms/schedular/call-out-scheduler/call-out-auto-queue-bar/call-out-auto-queue-bar.component.ts
  - src/app/modules/tms/schedular/call-out-scheduler/call-out-match-table/call-out-match-table.component.html
  - src/app/modules/tms/schedular/call-out-scheduler/call-out-match-table/call-out-match-table.component.ts
  - src/app/modules/tms/schedular/call-out-scheduler/call-out-table-board/call-out-table-board.component.html
  - src/app/modules/tms/schedular/call-out-scheduler/call-out-umpire-dialog/call-out-umpire-dialog.component.html
  - src/app/models/call-out/match-call-out.model.ts
  - src/assets/i18n/en.json
---

# Match Call Out scheduler

## Match Call Out scheduler: scope and where to find it
The Match Call Out scheduler is the **Scheduler** page for tournaments whose scheduling method is Match Call Out. Instead of placing matches on fixed times, matches are called out to free tables during the playing day, by hand or automatically (auto-queuing).

Open **Schedule** from the sidebar. For a Match Call Out tournament it opens this screen (route `tms/schedular/call-out/:event_id`). League events never use it; they always open the normal Scheduler, and an event using manual (drag and drop) scheduling is sent back to the normal Scheduler.

## Match Call Out scheduler: hall and day selection
- **Hall** dropdown: choose the hall (venue).
- **Year** and **Month**: narrow the day strip.
- **Days**: click a day ("Day {n}"); use the arrows to scroll through the dates.
- **Open Day Planner**: opens the event's Day Planner, where the categories of each day are set.
- The board header shows "{hall} · Tables 1–{count}".

If no days are set up: "No playing days are set for this event's halls yet."

Calling matches and auto-queuing work only on the current day: "Calling matches and auto-queuing work only on the current day." On other days the buttons are disabled.

## Match Call Out scheduler: auto-queuing bar
The bar shows the auto-queuing state:
- **Auto-Queuing is off**: "Queued matches are called out automatically from {time} at {hall}." (or "Add categories for this day in the Day Planner to start auto-queuing."). Button **Start Auto-Queuing** (disabled when there are no active matches).
- **Auto-Queuing running**: "Matches are called to free tables automatically. {count} called today." Button **Pause**.
- **Auto-Queuing paused · Manual mode**: "Matches already queued are running. Dispatch the next match to the first free table." Button **Dispatch Next**.

While running or paused, the stop button asks "Stop auto-queuing?": "No more matches will be called automatically for this day. Matches already on tables keep running." (**Stop auto-queuing** / **Cancel**). During a break: "Break in progress — no new matches are called." Messages: "Auto-queuing started", "Auto-queuing paused", "Auto-queuing stopped". The bar can be collapsed.

## Match Call Out scheduler: table board
The board shows each table, with counts "{count} Free", "{count} Called", "{count} Live" and the number of **Categories** for the day. Switch between **Table View** and **Match View**; the board can be collapsed.

- A **Free** table ("Table available") has **Call Next**, which calls the next match to that table.
- A table with a match shows it as **Called** or "Live · {minutes}m", with the players (or "Players to be decided"), category, round and umpire.
- **Record score** opens the same score **Edit** popup as the Scoring and Streaming page.
- **Remove from table** asks "Remove match from table?": "Take {match} off table {table}? It goes back to the queue." (**Remove** / **Cancel**).

After a call, a message "{match} called to table {table}" offers **Undo** for about 15 seconds. A removal ("Match removed from table {table}") can also be undone from its message.

## Match Call Out scheduler: Matches list
The list has **Active** and **Completed** tabs. Columns: **No.**, **Match ID**, **Time**, **Table** (T-{n}), **Match**, **Category**, **Umpire**, **Status**, **Result** and **Actions**.

On the Active tab the order is the system priority: "Ordered by system priority — 1 point per event each player is entered in. Matches with a player already on a table move down until they're free."

Statuses: **Waiting**, **Ready**, **Called**, **Live**, **Completed**. Hover over **Waiting** to see why: "Players are not decided yet" or "Waiting for the previous round to finish". The server also holds a match back when its category's start time today has not come yet, a player is on another table, a player is still resting after their last match, or a break is running; for these the page shows the general text "Waiting to become ready".

Actions:
- **Score**: for Called or Live matches; opens the score Edit popup.
- **Dispatch**: for Ready or Waiting matches, shown only when auto-queuing is not running; calls the match to the first free table.
- **Assign** (in the Umpire column): for a match without an umpire that is not completed.

Empty tabs: "No active matches for this day" / "No completed matches for this day yet".

## Match Call Out scheduler: Filter
**Filter** opens one choice each for **Table**, **Category**, **Stage**, **Round**, **Group** and, on the Active tab, **Status**. **Clear All** clears them.

## Match Call Out scheduler: Assign Umpire popup
"Assign umpire for" the match shows the day's officials with **Umpire Name**, **Matches Assigned** and **Action**. A **Player** tag marks a player umpire and **Busy** marks an official who is busy right now. Click **Assign**: "{name} assigned". Close with **Close**.

Errors from the server are shown as is, otherwise "Something went wrong. Please try again."

## Match Call Out scheduler: how the server picks the next match

The server calls matches in this order:
1. Matches you dragged to a position, in your order.
2. If switched on in the Day Planner: finals last, doubles first.
3. The priority mode (Round Progress, Category Elapsed or Category Block), then stage and round order.
4. Doubles before singles, then the players' total entries (highest first), then the draw order.

A match is only called when its category has started today, both players are known, the earlier round of its group is finished for its players, no player is on another table, the players have rested at least the minimum rest time (default 5 minutes) and no break is running. Each free table, lowest number first, gets the next such match.

## Match Call Out scheduler: server messages

- "This action is only possible for today" — calling, dispatching and starting or pausing auto-queuing work only on the hall's current date (stopping works any day).
- "No match is ready to be called" — **Call Next** or **Dispatch Next** found no callable match.
- "No table is free" / "This table is already in use".
- "This match cannot be called now" — the dispatched match is not callable yet (for example a Waiting match).
- "The match has started and cannot be taken off its table" — scoring has begun.
- "This match is not on a table".
- After **Remove from table**, the freed table is refilled only after the 15-second undo window.
- Assign umpire: "This official is registered for another day ({date})", or "Assignment would exceed per_match_limit for one or more matches". **Busy** is only a warning; there is no time-overlap check.
- Placing matches on time slots in this event is refused: "This event uses Match Call Out: time slots cannot be assigned".

## Frequently asked questions: Match Call Out scheduler
**How does the Match Call Out scheduler work?** Matches are called to free tables during the day, in priority order, either automatically (auto-queuing) or by hand with **Call Next**, **Dispatch** or **Dispatch Next**.

**How do I call a match to a free table?** On the table board, click **Call Next** on a **Free** table to call the next match to it. Or, while auto-queuing is not running, click **Dispatch** on a Ready or Waiting match in the Matches list to call it to the first free table. A message "{match} called to table {table}" offers **Undo** for about 15 seconds.

**How do I start auto-queuing?** Select today's date and the hall, then click **Start Auto-Queuing**. The day needs categories in the Day Planner and at least one active match.

**Why are the buttons disabled?** Calling matches and auto-queuing only work on the current day.

**Why is a match shown as Waiting?** Hover over the status: its players may not be decided, or the previous round may still be running. "Waiting to become ready" can also mean the category has not started yet today, a player is on another table or still resting, or a break is running.

**How do I take a match off a table?** Use **Remove from table** on the board; the match goes back to the queue.

**Why does my league open the normal Scheduler?** League events always use the normal Scheduler; only tournaments set to Match Call Out use this screen.
