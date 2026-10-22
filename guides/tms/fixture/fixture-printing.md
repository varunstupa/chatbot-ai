---
doc_id: tms.fixture.printing
title: Printing matches – match print popup, day-wise print, Badminton sheet and print queue
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - print match
  - match print popup
  - print now
  - print all matches
  - queue all
  - new match ready
  - day wise print
  - daywise print
  - badminton print sheet
  - print without score
  - print queue
  - auto dismiss print popup
  - print logos
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I print a match?
  - What is the difference between Print Now and Queue?
  - How do I print all matches of a category?
  - What does "New Match Ready" mean?
  - Why does the print popup close by itself?
  - How do I print the day-wise sheet?
  - What is the Badminton print sheet?
  - How do I print a match without the score?
backend_sources:
  - gateway/src/routers/print_router.py (get_print_settings, get_print_alert_settings, get_print_queue, update_print_status, update_queue_status)
  - gateway/src/routers/match_router.py (matches; print data)
source_files:
  - src/app/shared/match-print-popup/match-print-popup.component.html
  - src/app/shared/match-print-popup/match-print-popup.component.ts
  - src/app/modules/tms/day-wise-print/day-wise-print.component.html
  - src/app/modules/tms/daywise-badminton/daywise-badminton.component.html
  - src/app/modules/tms/tms-fixture/tms-fixture.component.html
  - src/assets/i18n/en.json
---
# Printing matches

Printing on the fixtures page works in three ways: the **match print popup** (shown when a match is ready), the **print queue** (matches waiting to be printed, opened from the print queue sidebar), and the **day-wise print sheet** (one sheet per day, with a separate Badminton sheet). The print queue sidebar itself is described in the fixtures page guide.

## Match print popup

- The popup opens when a match is ready for printing. Its header is "{{round}} Ready" (for example "Round 1 Ready") and the title line is "New Match Ready" when the match was just added.
- For one match, the popup shows the stage, the round, **Match #** with the match order, the category, the two participants with **VS** between them, and the text "Is now available for printing".
- For several matches, it shows "{{count}} matches created in this category", then a list of the matches as "Match #n: <participants>".
- Only the first few matches are shown. **+ {{count}} more matches** shows the rest.
- **Print Now** (single match) or **Print All matches** (several matches) prints the matches that can be printed.
- **Queue** (single match) or **Queue All** adds the matches to the print queue without printing them.
- If a participant has no name yet, the name is shown as "TBD".
- **Close** (the close icon) queues the matches first and then closes the popup, so a match is not lost.

## Auto dismiss

- The print alert settings can set a time after which the popup closes by itself. The popup then shows "Auto-dismissing in {{seconds}}s" with a progress bar.
- When it closes automatically the matches are queued first, the same as **Close**.
- If there is no setting, the popup stays open until you close it.

## Print queue sidebar

- Lists the matches that were queued (for example by **Queue** or **Queue All**). Printing the queue prints every match in it.
- The queue is kept on the server, and the status of an item is updated when it is printed or removed.
- Full details of the sidebar are in the fixtures page guide (print queue).

## Day-wise print sheet

- The day-wise sheet prints the matches of one day, with the logos (**Logo 1** to **Logo 6**) when logos are enabled for the participants.
- Each match row shows the back number, the player or team name, the **Club** and **Member Association** in brackets, and the games: the points of each game (**Games**), the **Result** (sets won) and the games columns.
- For doubles, each pair shows both players with their back numbers, Member Association and Club.
- A match without a score is printed as a blank result when **print without score** is on.
- Unscored matches are hidden from the queue print (**Hide unscored matches**).

## Badminton print sheet

- For Badminton the sheet is a separate layout (the Badminton day-wise sheet).
- It uses the team logos and the team settings of the event; the Logo labels are the same as the day-wise sheet.
- Use **Print without score** to print the blank sheet of a match.

## Print without score

- When **print without score** is on, the match sheets print with empty score boxes, so the sheet can be filled in by hand.
- The same option applies to the print queue.

## Messages

- "New Match Ready" – a match was just added and is ready to print.
- "TBD" – the participant has no name yet.
- "Something went wrong" – a print or queue request failed with no message from the server.

## Permissions

- If the server refuses a print or queue request, the server message is shown on the screen.

## Frequently asked questions

**How do I print a match?** When a match is ready, the print popup offers **Print Now** to print it at once or **Queue** to add it to the print queue. Matches in the print queue are printed from the print queue sidebar.

**What is the difference between Print Now and Queue?** **Print Now** prints the match at once. **Queue** adds it to the print queue without printing; the queue is printed later from the print queue sidebar.

**How do I print all matches of a category?** When several matches of a category are created, the print popup shows them together. Click **Print All matches** to print them, or **Queue All** to add them all to the print queue.

**What does "New Match Ready" mean?** A match was just added and is ready to print. The popup offers **Print Now** or **Queue** for it.

**Why does the print popup close by itself?** The print alert settings set a time after which the popup closes itself (it shows "Auto-dismissing in …s"). The matches are queued first, the same as **Close**.

**How do I print the day-wise sheet?** The day-wise sheet prints the matches of one day, with back numbers, names, club and member association, and the games and result. Turn on **print without score** to print empty score boxes for filling in by hand.

**What is the Badminton print sheet?** Badminton uses its own day-wise sheet layout, with the team logos and team settings of the event. **Print without score** prints a blank sheet for a match.

**How do I print a match without the score?** Turn on **print without score**. The match sheets then print with empty score boxes, so they can be filled in by hand. The same option applies to the print queue.
