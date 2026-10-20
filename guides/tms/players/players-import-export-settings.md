---
doc_id: tms.players.import-export-settings
title: Players page – import, export and settings
routes:
  - tms/players/:event_id
aliases:
  - import players
  - export participants
  - export players
  - participant export
  - player settings
  - seeding cut off date
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I import players from Excel?
  - How do I export the participant list?
  - How do I show the club column?
  - What is the seeding cut-off date?
  - Why did my import fail?
backend_sources:
  - gateway/src/routers/user_import_export_router.py (import_player)
  - tournament config create_event_categories (category configuration)
  - events seeding settings (seeding_cut_off_date)
source_files:
  - src/app/modules/tms/players/players.component.ts
  - src/app/shared/participant-export-sidebar/participant-export-sidebar.component.html
  - src/app/shared/components/stupa-entity-setting/stupa-entity-setting.component.html
---
# Players page – import, export and settings

This guide explains how to import participants from an Excel file, export the participant list, and use the **Settings** panel of a category on the **Players** page.

## Importing players from an Excel file

1. Select the category and click the import (upload) icon. The window **Import Singles** (or Teams, Doubles, Mix Doubles) opens: "Import users through XLSX files. Download sample to check uploading format".
2. Click **Download Sample** to get the template for this participant type.
3. Fill it in and click **Upload** to choose the file. "Uploading..." is shown.
4. On success the server message is shown and the list refreshes.

- If rows have errors ("Validations failed"), **Download Report** gives a file listing them. Fix the file and upload again.
- Otherwise the error lines are shown in the message.

## Import rules checked by the server

- Only **.xlsx** files are accepted, and the file must have the columns of the sample for this participant type (Singles, Doubles, Mix Doubles or Teams).
- The sample has **one sheet per category** of that type; keep the sheet names, they tell the server the category.
- At most **500 rows per sheet**: "<sheet> has N rows (max allowed 500)".
- Players who do not exist yet are created; points are taken from the file; missing points are filled in by the system (0 if none are found).
- Singles: a player in the file who is already registered in that category is replaced by the imported entry. Doubles: existing pairs are updated.
- The registration checks of adding apply too (for example "Event payment settings are required").
- "No players found or created from the import file." – the file has no usable rows. "Failed to upload Excel file" – try again.
- Import needs **Edit** permission on **Player Screen**.

## Exporting the participant list

Click **Export**. In the side panel:
- **Select Export type:** **Category Wise** ("Export Participant List Category Wise") or **Entity Wise** ("Export Participant List Entity Wise").
- **Select Format** – the organisation's published participant export formats (set up in the export format settings). "Please select a format" if missing.
- Category Wise: **Select Categories** (or **ALL**) – "Please select a category".
- Entity Wise: **Select Entities** – **M.A.**, **Club**, **All** – "Please select at least one entity".
- Click **Download**.

The file is not downloaded at once: the export is prepared in the background. "Export queued successfully. Check Export/Share Results to download when ready." Download it from **Export/Share Results** when it is ready. "Failed to export participants" means the export could not be started.

From the **Deleted** list, **Export** exports the deleted participants of that category (the category is fixed).

## Settings panel: organisation columns and parameters

Click **Settings** for the selected category (or sub category):
- **Select Organisation**: **Club**, **Member Association** or **Both** – which organisation columns the player list shows.
- **Parameter**: **Logo** or **Flag** (only one of the two) and **Abbreviation** – how the organisation is shown. With **Both** selected, Logo, Flag and Abbreviation are all greyed out.
- **Rank Type (Max 2)** – choose up to two of **European Rank** (ER), **National Rank** (NR) and **World Rank** (WR). They are shown for players, for example in the league Player Details panel.
- Click save; the server message confirms it and the list refreshes. The settings apply to the selected category (or sub category) only.
- Saving needs **Edit** permission on **Player Screen** and **Edit Category**.

## Settings panel: seeding cut-off date and league options

- **Seeding Settings** (tournaments, when ranking points are used for seeding): "To finalize ranking points at the specified cut-off after which player rankings are finalized for seeding". Set the **Seeding Cut off Date**. Points earned after this date do not count for seeding.
- **SUB MATCH POP-UP SETTINGS** (leagues): **Show Loan** and **Team Parent**, available only when loan players are enabled in the registration settings.

## Frequently asked questions about import, export and settings

**How do I import players from Excel?** Click the import icon, **Download Sample**, fill it, **Upload**.

**Why did my import fail?** Some rows have errors; click **Download Report**, fix them and upload again.

**How do I export the participant list?** **Export** → choose Category Wise or Entity Wise, the format and categories or entities → **Download**, then get the file from **Export/Share Results**.

**I clicked Download but no file came. Why?** Exports are queued; download the file from **Export/Share Results** when it is ready.

**Why is my export format not in the list?** Only published participant export formats are offered; publish it in the export format settings.

**How many rows can one import sheet have?** 500 per sheet (one sheet per category).

**How do I show the club column?** **Settings** → **Select Organisation** → **Club** or **Both** → save.

**Why can I not tick Logo, Flag or Abbreviation?** With **Both** chosen under **Select Organisation** all three are greyed out. Otherwise Logo and Flag exclude each other: untick one to tick the other.

**What is the seeding cut-off date?** The date after which ranking points no longer change the seeding of the category.
