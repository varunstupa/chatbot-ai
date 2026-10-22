---
doc_id: tms.event-settings.payment-invoice
title: Payment & Invoice page
routes:
  - tms/event-settings/payment-invoice/:event_id
aliases:
  - payment and invoice
  - payment & invoice
  - payment and invoices
  - payment settings
  - invoice settings
  - invoice history
  - financial report
  - merged invoice
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I choose who the invoice is raised to?
  - Why is the Save button disabled?
  - How do I accept online payments for this event?
  - How do I send invoices for registrations?
backend_sources:
  - gateway/src/routers/events_router.py (get/update_event_finance_settings, seed_event_payment_settings)
  - gateway/src/routers/invoice_router.py (templates, create_invoice, create_bulk_invoice, copy_invoice_template)
  - gateway/src/routers/user_role_account_router.py (get_accounts)
  - gateway/src/routers/ctms_router.py (tenant payment gateways)
  - gateway/src/routers/payments_router.py (verification before payment)
  - gateway/src/routers/financial_summary_router.py
  - gateway/src/handlers/registration/helpers.py (validate_event_payment_settings)
  - gateway/src/services/membership_order_service.py (Raised To priority when an order is created)
  - tms/src/service/events_service.py (update/get_event_finance_settings)
  - tms/src/schema/events_schema.py (EventFinanceSettings)
source_files:
  - src/app/modules/tms/events-settings/payment-invoice/payment-invoices/payment-invoices.component.ts
  - src/app/modules/tms/events-settings/payment-invoice/payment-invoices/payment-invoices.component.html
  - src/app/core/store/invoice/invoice.reducer.ts
  - src/app/core/store/invoice/invoice.effects.ts
  - src/app/modules/tms/events-settings/payment-invoice/payment-invoices-history/payment-invoices-history.component.ts
  - src/app/modules/tms/events-settings/payment-invoice/payment-invoices-history/payment-invoices-history.component.html
  - src/app/modules/tms/events-settings/payment-invoice/merge-invoice-dialog/merge-invoice-dialog.component.ts
  - src/app/modules/tms/events-settings/payment-invoice/financial-report/financial-report.component.ts
  - src/app/modules/tms/events-settings/payment-invoice/order-details-dialog/order-details-dialog.component.ts
---
# Payment & Invoice page – user guide

This guide describes the **Payment & Invoice** step of an event in the Stupa Event Management System (admin panel). On this page the organiser decides how registration fees are paid (cash or online), who invoices are raised to, and which invoice templates are used. The page also lists the event's orders and invoices and produces the event's financial report.

## Where to find it

Open **Event** from the sidebar, then click **Payment & Invoice** in the row of setup steps at the top of the page.

## Payment & Invoice page: where it is and what it is for

Open the event, then choose **Payment & Invoice** in the event setup steps. The page has three buttons at the top:

- **Payment and Invoices** – the settings: **Raised To**, **Payment Type**, **VERIFICATION SETTINGS** and the receiving account (Online only), **Enable Invoicing for this Event?**, the invoice templates, and **Save**.
- **Invoice History** – the event's orders, invoices and merged invoices, where invoices are sent, merged and marked as paid.
- **Financial Report** – the event's income per class or per entity, with refunds and totals, downloadable as PDF or XLS.

The registration fee itself is set per category on the **Registration** page (Fee & Refund Information card). This page decides how that fee is collected and invoiced.

## Payment & Invoice page: what loads when you open it

When the page opens it loads, in this order:

1. The role list for **Raised To**: the roles above the **Player** role in your organisation's role hierarchy (for example club or association roles). The **Admin** role is never listed.
2. The event's saved settings: selected roles and their order, payment type, verification setting, receiving account, invoicing Yes/No and the selected templates.
3. The invoice templates for the selected template tab.

When an event is created, its payment type, verification setting and **Raised To** roles are pre-filled from the organisation's payment setup (Payments in the admin menu). So a new event may already show selections; change them here for this event only.

If the role list is empty, the Player role or its parent roles could not be loaded for your organisation. Reload the page; if it stays empty, the role hierarchy has to be set up by an administrator.

## Raised To: choosing who invoices are raised to

**Raised To** – "Select User Role(s) whom invoice has to be raised". Each card is a role. Click a card to select it; click it again to remove it.

- Selected cards show a number: the order in which you selected them (1, 2, 3 …). Removing a card renumbers the remaining ones so there are no gaps.
- To change the order, remove the cards and select them again in the order you want.
- At least one role must be selected before **Save** is enabled.

When someone registers, the order is billed to the participant's parent entity (for example their club) whose role is in this list, following this order: role 1 is used first. If none of the participant's parents has one of the selected roles, the order is billed to the event organiser.

If the organiser registers participants themselves, registration is refused with "Event payment settings are required" until at least one **Raised To** role is selected and saved.

## Payment Type: Cash or Online

**Payment Type** has two cards. Only one can be active at a time:

- **Cash** – "Traditional cash payment method. The payment shall be received through cash offline by the organizer." Players register without paying online; the organiser collects the money and marks orders as paid in **Invoice History**.
- **Online** – "Hassle-free cashless payment method. The payment shall be received digitally through online methods such as net-banking, credit card, debit card, etc." Players pay through the organisation's payment gateway.

Clicking the inactive card togglees to it. Clicking the active card turns it off, and then no payment type is selected, which disables **Save**.

Choosing **Online** shows two more sections: **VERIFICATION SETTINGS** and the account picker ("Select Account you want to receive payments in"). Choosing **Cash** hides them and the saved account is removed from the event when you save.

## VERIFICATION SETTINGS (Online only): pay before or after verification

Shown only when **Payment Type** is **Online**. It decides the order of payment and verification for categories that require verification (set on the **Registration** page, Verification card).

- **Pay Before Verification** – the player pays first; verification happens after the payment.
- **Pay After Verification** – verification happens first. Payment can only be made once verification is complete. Until then, starting the payment fails with "Verification is in progress. Payment will be initiated after verification is complete."

Go by the option title. The small description under each option currently reads the other way round.

If nothing was saved before, **Pay After Verification** is selected. The setting is saved only when **Online** is the payment type.

## Receiving account for online payments

Shown only when **Payment Type** is **Online**: "Select Account you want to receive payments in". Click an account card to select it; a tick marks the selected one, and the organisation's default account has a green badge. The card shows the gateway name and the gateway account ID.

- The list shows your own **active** accounts on the organisation's payment gateway. An account that is not active (for example onboarding not finished) is not listed.
- "No verified accounts available. Please onboard an account first." – you have no active account. Add and complete one in Payments (admin menu), then come back.
- An error message above the list means the payment gateway or the accounts could not be loaded. Reload the page.
- No account is chosen automatically. If the event already has a saved account, it is shown as selected.

**Save** stays disabled with **Online** until an account is selected. Registration for an Online event without a saved account is refused with "Event payment settings are required".

## Enable Invoicing for this Event?

**Enable Invoicing for this Event?** – **Yes** or **No**. One of the two must be chosen before **Save** is enabled.

- **Yes** – invoices can be generated for the event's orders. The template section appears: **Create your own Template**, the **Registration Invoice** / **Merged Invoice** tabs and the template list.
- **No** – no invoices are generated. Sending an invoice from **Invoice History** fails with "Invoice is not enabled for this event".

Changing Yes/No only takes effect after **Save**.

## Invoice templates: Registration Invoice and Merged Invoice

Shown when **Enable Invoicing for this Event?** is **Yes**. There are two kinds of template:

- **Registration Invoice** – used for the invoice of each registration order.
- **Merged Invoice** – used when several invoices of the same payer are merged into one (see Merging invoices).

Under each, choose **Global Template** (templates shared by all events of the organisation) or **Event Template** (templates made only for this event). Click a template card to select it; click it again to unselect. One Registration Invoice template and one Merged Invoice template can be selected; switching tabs keeps both selections. If none was saved, the organisation's active global template is pre-selected.

"No data found" means there are no templates on that tab yet.

Once the first registration invoice of the event has been generated, the Registration Invoice template is fixed and a different selection is not saved. The same applies to the Merged Invoice template after the first merged invoice. **Save** still succeeds; only the template stays as it was.

## Creating, copying, editing and previewing invoice templates

- **Create Template** (in the **Create your own Template** banner): opens the template editor in Invoice Management for the current tab (Registration or Merged), linked to this event. "Event organizers can also create their own unique invoice associated with the Event. The template would not be visible in other Events." If you have unsaved changes, "Are You Sure?" – "These changes will not be reflected unless saved" asks first; **Continue** leaves without saving.
- **Copy** icon (only on **Global Template**): "Copy Template" – "Do you want to copy "<name>"?" → **Yes, copy it** makes a copy for this event and togglees to **Event Template**. Success: the server's message or "Template copied successfully". Failure: the server's message or "Failed to copy template".
- **Edit** icon (only on **Event Template**): opens the template in the editor.
- **Eye** icon: preview the template without editing.

## Save button: when it is enabled and what it saves

**Save** is at the bottom of the **Payment and Invoices** tab. It is greyed out until all of these are true:

1. At least one **Raised To** role is selected.
2. **Enable Invoicing for this Event?** has **Yes** or **No** chosen.
3. A **Payment Type** is selected.
4. With **Online**: a receiving account is selected.

Save stores, for this event: the Raised To roles and their order, invoicing Yes/No, the Registration and Merged Invoice templates, the payment type, and for Online the account and verification setting. After saving, the page reloads the saved settings.

- Success: "Success" (or "Finance settings saved successfully!").
- "Please select a payment account for online payments." – Online without an account.
- "No Event Found" – the event no longer exists.
- "Error updating event finance settings: …" or "Failed to save finance settings. Please try again." – the save failed; try again.

## How payment settings are checked when someone registers

- Registration is refused with "Event payment settings are required" when the event has no saved payment settings, or the payment type is **Online** without a saved receiving account.
- When the event organiser registers participants, at least one **Raised To** role must also be selected and saved, otherwise the same message appears.
- For a **Cash** event, other users can register without further payment checks.
- With **Online** and **Pay After Verification**, payment is blocked until verification is complete ("Verification is in progress. Payment will be initiated after verification is complete.").

Fix any of these by completing this page and clicking **Save**.

## Invoice History tab: Orders

**Invoice History** has three tabs: **Orders**, **Invoices** and **Merged Invoices**. **Orders** lists the event's registration orders:

**S.No**, **Order ID**, **Registered By** (entity and role), **Registered Qty**, **Verification Status** (✔ verified / ❌ rejected counts), **Withdrawn**, **Amount**, **Refund Status** (with refund amount), **Payment Mode** (Online/Offline), **Payment Status**, **Invoice Status** (Generated/Pending) and **Action** (eye = order details, send = generate invoice).

Filters: **Invoice Status** (generated, pending), **Refund Status** (initiated, completed, cancelled), **Payment Status** (paid, unpaid, overdue), and **Search** by name. Results are paginated (10 to 100 per page).

The eye icon opens **Order Details**: Order ID, registered by/for, date and time, categories, amounts, withdrawn and refund status per player ("Order details not found." if it cannot be loaded).

If the event is **Online** but some orders are cash, a warning explains that these came from adding participants directly in the fixture with the Replacement feature, and that the organiser must collect those payments. Such rows are highlighted.

## Invoice History: marking an order as paid

The **Payment Status** dropdown on an order can be set to **Paid**, **Unpaid** or **Overdue**, with these limits:

- Only **cash (offline)** orders can be changed. Online orders get their status from the payment gateway, so the dropdown is disabled.
- Once an order is **Paid**, its status is locked.

Messages: "Payment status updated successfully." or the server's message / "Failed to update payment status. Please try again.". "Invalid order. Order ID is missing." means the row has no order ID; reload the list.

## Invoice History: sending invoices for orders

- **Send** icon on an order: generates the registration invoice for that order. "Invoice has been created successfully." The icon is disabled once the order's invoice is **Generated**.
- **Bulk**: tick the checkboxes of several orders (or the header checkbox for all). Orders whose invoice is already generated cannot be ticked. **Send Invoice** appears when more than one order is ticked; it generates the invoices, grouped per payer. "Bulk invoices have been created successfully." or "Failed to create bulk invoices.".

Errors: "Invoice is not enabled for this event" – set **Enable Invoicing for this Event?** to **Yes** and save. Otherwise the server's message or "Failed to create invoice. Please try again.". "Please select at least one order to send." – nothing ticked.

## Invoice History tab: Invoices

Lists the generated registration invoices: **S.No**, **Invoice No.**, **Raised To**, **Qty**, **Amount**, **Invoice Date**, **Due Date**, **Payment Status**, **Payment Type** and **Action**.

- Eye icon: opens the invoice.
- Print icon: opens the invoice and downloads it as PDF.
- Filters: **Role** and **Payment Status**, plus **Search**.
- **Merge Invoice** button: opens the merge dialog (see Merging invoices).

"Failed to load invoices. Please try again." – the list could not be loaded; reload. "No data found" – no invoices match, or none have been generated yet.

## Merging invoices into one per payer

**Merge Invoice** (on the **Invoices** tab) opens **Merging by User**: "You are consolidating multiple invoices from these users into a single file." Each row is a payer (**Raised To**) with **T. Invoices** (number of invoices), **Qty**, **Amount**, **Refund** and **Status** (**To Generate** or **Generated**).

1. Tick the payers to merge – at most 10 at a time. Payers with status **Generated** cannot be ticked.
2. Click **Yes, Merge**. One merged invoice per payer is created with the **Merged Invoice** template selected on the settings tab. "Invoice summary created successfully." (toast "Merging Successful") and the page togglees to **Merged Invoices**.

A **+N** badge means N invoices were created after the merged invoice. The **Regenerate** icon then rebuilds that payer's merged invoice to include them ("Invoice summary regenerated successfully.").

Errors: "Please select at least one club to merge.", "Failed to create invoice summary.", "Failed to regenerate invoice summary.", "No invoice users found" (nothing to merge).

## Invoice History tab: Merged Invoices

Lists merged invoices: **S.No**, **Invoice No.**, **Raised To**, **Qty**, **Amount**, **Refund**, **Payment Status**, **Payment Type** and **Action**. Filters: **Role**, **Payment Status**, **Search**.

- **Payment Status** can be changed (Paid, Unpaid, Overdue) until it is **Paid**; then it is locked. "Payment status updated successfully." / "Failed to update payment status. Please try again.".
- Eye icon: view; Print icon: download as PDF.
- **Regenerate** icon: rebuilds the merged invoice with the current Merged Invoice template and any newer invoices ("Invoice summary regenerated successfully." / "Failed to regenerate invoice summary."). "Invoice Data not found." or "Required invoice data is missing." – reload the list and try again.

## Financial Report tab

Shows the event's income. If no report exists yet: "No record found" and a **Generate financial report** button, which builds the report (per class and per entity).

When a report exists:

- Header: event name, **Competition Dates**, **Venue** and **Organizer Name** (venue and organiser are not shown for leagues).
- **Filter by**: **Class** (one row per class/category) or **Entity** (one row per paying entity).
- Columns include **Entries**, **Price**, **Total**, **Amount received from Entries** (Entity view), **Adjusted Amt**, **Refund** and **Amount**. Some report formats show an info icon on **Amount** with the breakdown (entries × amount, refund, line total, **Total Amount**).
- A summary below lists the totals, fees and the final total as calculated by the server.
- **Refresh** rebuilds the report with the latest orders and refunds.
- **Download**: **PDF** (print) or **XLS** (spreadsheet with the same rows and totals).

Messages after **Refresh** or **Generate financial report** come from the server.

## Payment & Invoice page: loading problems

- Templates fail to load: the list stays empty with "No data found"; toggle tabs or reload.
- "Failed to Load Orders. Please try again." / "Failed to load invoices. Please try again." / "Failed to load merged invoices. Please try again." – reload the tab.
- Account list errors: see Receiving account for online payments.
- If settings look different from what you saved, reload the page; saved settings are always read again from the server when the page opens and after saving.

## Frequently asked questions about the Payment & Invoice page

**Why is the Save button disabled?** All four must be set: at least one Raised To role, Enable Invoicing Yes or No, a Payment Type, and with Online a receiving account.

**How do I accept online payments?** Select Online, choose the verification setting, select your receiving account and click Save. If no account is listed, add and activate one in Payments (admin menu) first.

**Why does registration say "Event payment settings are required"?** The event's payment settings were never saved, Online is selected without an account, or (for the organiser) no Raised To role is saved. Complete this page and click Save.

**Can I change the Raised To order?** Yes. Remove the role cards and select them again in the order you want, then Save. Role 1 is used first.

**Why can't I change the payment status of an order?** Online orders are updated by the payment gateway, and Paid orders are locked. Only unpaid cash orders can be changed.

**Why is the send icon disabled on an order?** Its invoice has already been generated.

**Why does sending an invoice say "Invoice is not enabled for this event"?** Set Enable Invoicing for this Event? to Yes and click Save.

**Why didn't my new template get used?** After the first invoice is generated the Registration Invoice template is fixed; after the first merged invoice the Merged Invoice template is fixed.

**How many payers can I merge at once?** Up to 10 per merge.

**What does +N next to a merged payer mean?** N invoices were created after the merge. Use Regenerate to include them.

**What is the difference between Pay Before and Pay After Verification?** Pay Before: the player pays first, then is verified. Pay After: verification must be complete before the player can pay.

**How do I choose who the invoice is raised to?** In **Raised To**, click the role cards in the order invoices should be raised; the number on a card is its order. A registration is billed to the participant's parent (for example their club) with the first matching role, otherwise to the event organiser. Select at least one role, then **Save**.

**How do I send invoices for registrations?** Open **Invoice History**. Click the **Send** icon on an order to generate its invoice, or tick several orders and click **Send Invoice** to generate them grouped per payer. Invoicing must be on: set **Enable Invoicing for this Event?** to **Yes** and save.
