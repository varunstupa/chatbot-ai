---
doc_id: tms.event-settings.print-settings
title: Print Settings page
routes:
  - tms/event-settings/print-settings/:event_id
aliases:
  - print settings
  - print
  - score sheet
  - scoresheet
  - print preferences
  - print layout
  - back number
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I print a score sheet?
  - How do I get a print prompt for every new match?
  - How do I add logos to the score sheet?
  - Why is the Print button missing?
backend_sources:
  - gateway/src/routers/print_router.py (update_print_settings, update/reset_print_alert_settings; Print Settings permission)
source_files:
  - src/app/modules/tms/print-settings/print-settings.component.ts
  - src/app/modules/tms/print-settings/print-settings.component.html
  - src/app/modules/admin/print-alert/print-alert.component.html
  - src/app/modules/admin/print-alert/print-alert.component.ts
---
# Print Settings page – user guide

This guide describes the **Print Settings** step of an event in the Stupa Event Management System (admin panel). Here the organiser decides when print prompts appear and how printed score sheets and back numbers look. What a score sheet contains depends on the sport; see the score sheet guide for your sport.

## Where to find it

Open **Event** from the sidebar, then click **Print Settings** in the row of setup steps at the top of the page.

## Print Settings page: where it is and what it is for

- Page address: `/tms/event-settings/print-settings/<event id>`, for example `/tms/event-settings/print-settings/534`.
- It is the **Print Settings** step in the row of event setup steps. The step is only shown for organisations that use it.
- Two top tabs:
  - **Print Preferences** – print prompts and alert sounds for this event.
  - **Print Layout** – the layout of the printed **Score Sheet** and **Back No.** (back numbers).

## Print Preferences: print mode and alerts

"Print Preferences let you customize how you want to print a match once it's created. You can print manually anytime or enable automatic prompts to ensure nothing gets missed."

- **Print Mode** ("Disable / Enable print mode"):
  - Off – "Do not show alerts. Print manually according to your own preferences."
  - On – "Automatically show a print prompt every time a new match is created in knockout stage."
- **Alert Settings** (only usable when Print Mode is on):
  - "Play sound notification when a new match is ready" – toggle.
  - **Select notification sound** – choose a tone (for example Coin Collect, Graphic Beeps, Metallic Beeps, Positive Click, Table Tennis Hit). Use the play button to hear it.
  - **Auto-dismiss alerts after** – 15 seconds, 30 seconds, 60 seconds or Never.
- Click **Update** (greyed out while Print Mode is off). "Print alert settings saved." confirms it; "Failed to save print alert settings." means it failed.

## Print Preferences: event settings versus global defaults

- The organisation sets global print defaults in the Admin Panel. This page changes them for **this event only**.
- When a setting differs from the global default, the page shows "Some settings differ from Admin Panel global defaults. Changes apply to this event only." and marks the setting "Overriding global default".
- **Reset to Global Defaults** (shown only when something differs) asks "Reset to global defaults?" – "This will revert all print settings for this event back to the current Admin Panel global defaults. Any custom changes you have made will be lost." Click **Yes, reset to defaults**. Messages: "Reverted to global defaults." or "Failed to reset to global defaults."

## Print Layout: saving and printing a score sheet

- Choose the participant type in **Print Settings** (Singles, Teams or Doubles). Each type has its own layout.
- Set the options in the panels (see the score sheet guide for your sport), then click **Save**. "Settings updated successfully" confirms it; "Error updating settings" means it failed.
- The preview on the right shows the sheet as it will print.
- **Save Settings to Print Sheet** is shown until the layout of that participant type is saved. After saving, the **Print** button appears.
- **Preview** opens a print preview; click **Print** there to print.
- For Teams there is a choice of sheet: **Preview**, **Scoresheet** or **Toss Sheet**. "Print section not found, please select a sheet type" means no sheet was chosen.

## Print Layout: logos on the sheet

- In **Logo(s)**, turn on the logo toggle and choose how many logos (1 to 6).
- Upload each logo (**Logo 1**, **Logo 2**, …). An uploaded logo shows "Uploaded"; click its × to remove it.
- Maximum file size 15 MB: "Logo size is greater than 15MB". "Logo Uploaded" confirms the upload.
- Logos appear at the top and bottom of the sheet. Click **Save** to keep them.

## Print Layout: Back No. (back numbers)

- The **Back No.** tab sets the layout of printed back numbers (bibs).
- In **Logo(s)** choose the number of logos and upload them; an uploaded logo shows "Uploaded" and can be removed.
- Click **Save**.

## Print Settings page: permissions

- Saving the layout and the print preferences needs **Edit** permission on **Print Settings**. Without it the save fails with "Access Denied".
- An expired sign-in gives "Unauthorized Access". Sign in again.

## Frequently asked questions about the Print Settings page

**How do I get a print prompt for every new match?** In **Print Preferences** turn on **Print Mode** and click **Update**. Prompts appear when new knockout matches are created.

**How do I change the alert sound?** Turn on the sound toggle, choose a tone in **Select notification sound**, click **Update**.

**Why is the Update button greyed out in Print Preferences?** Print Mode is off.

**How do I undo my event print changes?** Click **Reset to Global Defaults** and confirm.

**Why is the Print button missing?** The layout of that participant type is not saved yet ("Save Settings to Print Sheet"). Click **Save** first.

**How many logos can a score sheet have?** Up to 6, each up to 15 MB.

**Are the layouts for Singles, Doubles and Teams shared?** No. Each participant type has its own layout; save each one.

**Where do I set back number logos?** **Print Layout** → **Back No.** tab.

**How do I print a score sheet?** Choose the participant type in **Print Settings**, set the options and click **Save**. The **Print** button then appears; **Preview** opens a print preview, where **Print** prints the sheet.

**How do I add logos to the score sheet?** In **Logo(s)**, turn on the logo toggle, choose how many logos (1 to 6) and upload each one (up to 15 MB each). Logos appear at the top and bottom of the sheet. Click **Save** to keep them.
