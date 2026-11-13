---
doc_id: tms.event-settings.access-control
title: Managing Event Access and Permissions
routes:
  - tms/event-settings/access-control/:event_id
aliases:
  - access control
  - event permissions
  - user access
  - give someone access
  - allow someone to edit an event
  - manage event users
  - event staff permissions
  - read only access
  - event access denied
tenants: all
exclude_tenants: []
suggested_questions:
  - How can I let someone manage my event?
  - How do I allow my colleague to edit match details?
  - How can I give someone access for just three days?
  - Why can someone view the event but not change anything?
  - Why can't my staff open Playing Order?
  - How do I remove a person's event access?
  - Why can't I give someone permission?
backend_sources:
  - gateway/src/routers/resource_permissions_router.py (bulk upsert and revoke; "Edit Event Access Control" permission)
  - user_role_service/src/service/resource_permissions_service.py (non-admin authority cap)
source_files:
  - src/app/modules/tms/event-access-control/event-access-control.component.ts
  - src/app/modules/tms/event-access-control/event-access-control.component.html
---

# Managing Event Access and Permissions

## Access-Control page: what is Event Access Control?
Event Access Control lets an event organiser decide who can view information and who can make changes in a particular event. Open it from the **Access-Control** step at the top of the event setup pages.

For example:
- You want a colleague to update match information.
- You want a staff member to view event details without changing them.
- You want to allow someone to manage a particular part of the event for three days.
- You want to remove access from someone who is no longer working on the event.

You can manage access for an individual person (**Users** tab) or for everyone who shares a role (**Roles** tab).

**Important:** Access is specific to each event. Giving someone access to one event does not automatically give them access to another event.

## Access-Control page: the access table
Both tabs show a table with a tick box per row, **S.No**, **Name** (the person or role), one column per event module, and **Action** (edit icon).

- Each module cell shows **Edit**, **Read** or **Delete** for that person or role. A cell shows **Read** when the access dates have not started yet or have ended, even if Write was given.
- **Search** filters the table; the × in the box clears it.
- Rows per page: 10, 20, 30, 40, 50 or 100. "No record found" means nobody has access entries yet (or nothing matches the search).
- On the **Users** tab the button is **User Accesses**; on the **Roles** tab it is **Role Accesses**.

## Access-Control page: how do I give someone access to my event?
1. Open the required event from the Event section.
2. Open the **Access-Control** step at the top of the event setup page.
3. Select the **Users** tab and click **User Accesses**. The **Settings** side panel opens.
4. Choose a role in **Roles** (**Select Role**). The **Admin** role is not in this list.
5. Choose the person in **Users** (**Select User**). This list stays disabled until a role is chosen; type in its search box to find a person, and more names load as you scroll ("Loading more data...").
6. Once a person is chosen, the **Permissions** and **Access Date** panels appear. In **Permissions**, tick **Write** and/or **Read** for each module.
7. Set the dates in **Access Date** (see the access dates section).
8. Click **Save**.

When it succeeds, the side panel closes and the table refreshes with the new entry. If the person already has an entry, use the edit icon on their row instead.

If the person is not in the user list, check the role selection and search the list. If you still cannot find them, ask your administrator to check their account and role.

## Access-Control page: editing an existing person's or role's access
- Click the edit icon in the **Action** column. The side panel opens with the current permissions and dates filled in.
- When editing a person, **Roles** and **Users** cannot be changed; only the permissions and dates.
- **Save** saves the permissions of **all** modules shown in the panel, not only the ones you changed.
- On the **Roles** tab, picking a role in **Role Accesses** that already has an entry opens that entry for editing.

## Access-Control page: how do I let someone change event or match details?
Give the person **Write** permission for the relevant event module.

For example, if they need to make changes to a particular part of the event, tick **Write** for that module and save the permissions.

Giving Write permission to one module does not automatically give Write permission to every other module.

## Access-Control page: what is the difference between Read and Write?
- **Read:** The person can view information but cannot make changes using that permission.
- **Write:** The person can make changes in the relevant module, subject to other system rules. The table shows it as **Edit**.
- **Delete:** The table may show Delete where that permission exists. Saving from this screen never grants Delete; it only sets Read and Write. Do not assume that Read or Write includes Delete.

If you want someone to view information without changing it, give them Read access rather than Write access.

## Access-Control page: why can someone view the event but not edit it?
This can happen for several reasons:

1. **Their access dates have expired or have not started yet.** Check the From and To dates.
2. **They have Read permission but not Write permission.** Open their access settings and check the relevant module.
3. **They have permission for a different part of the event.** Access to one module does not automatically allow changes in another.
4. **They are relying on a role permission that does not provide the required access.** Check the person's effective permissions and the role they belong to.

Correct the relevant setting, save it, and ask the person to try again.

## Access-Control page: how do I give access for only a few days?
In the person's side panel, open **Access Date**:

- **From**: the date access begins.
- **To**: the date access ends.
- Dates are shown as day/month/year.

**Quick Selections** fill both dates for you:
- **3 Days**, **7 Days**, **10 Days**: from now until that many days later.
- **Event Start - End**: the event's own start and end dates.

If you do not set an end date for a new entry, it is saved with no practical end date (31/12/2099).

Outside the permitted access dates, the permission table shows Read instead of Edit. Check the actual dates if the person can view information but cannot make changes.

## Access-Control page: how do I give access to several people with the same role?
Use the **Roles** tab when you want to manage permissions for a role rather than setting up each person separately.

1. Open **Access-Control** and select **Roles**.
2. Click **Role Accesses**.
3. Under "Pick a role you wish to manage:", choose the role. Each role shows its number of **Members**, "No permission yet" if it has none, or the modules it can access.
4. Under **Manager Permission**, tick **Access** for each module the role should be able to change.
5. Click **Save**.

Click **Role Accesses** at the top of the side panel to go back to the role list. These permissions apply to people with that role in the current event. Use the **Users** tab when you need to manage one person's access individually.

## Access-Control page: why can't someone open Playing Order or Umpire Settings?
If another event page shows "Access Denied", the user may not have the required permission for that module in the current event.

Open **Access-Control** and check the user's permissions for the relevant module. Make sure they have **Write** (shown as Edit) if the task requires editing.

If you cannot grant the required permission yourself, contact an administrator.

## Access-Control page: "You can only grant or revoke permissions you already have"
This message means that your account is trying to grant or remove a permission that you are not authorised to manage.

- Users who are not administrators can only grant permissions they themselves hold for the current event. Because **Save** sends every module, you need your own permission on each module listed, and you cannot tick Write or Read where you only lack it yourself.
- Removing access entries from this screen is also refused with this message for users who are not administrators.
- Managing this screen at all needs the **Edit Event Access Control** permission; without it the save is refused.

Ask an administrator who has the necessary authority to make the change.

## Access-Control page: how do I remove someone's access?
One entry:
1. Click the edit icon of the person or role in the **Action** column.
2. Click **Delete** at the bottom of the side panel. The entry is removed at once (no confirmation).

Opening a row with the edit icon also ticks that row, and the panel's **Delete** removes every ticked row. Untick other rows first if you only want to remove one.

Several entries:
1. Tick their rows in the table (the top tick box selects the whole page).
2. Click **Delete** next to the search box.
3. Confirm "Reset?" – "Are you sure you want to reset all the entries? All changes will be lost!" with **Yes, Reset**.

Removing an access entry removes that user's or role's configured access for this event. It does not delete the person's account or remove their access to other events.

## Access-Control page: common errors
**"Please select user or role for update score for team matches."**

Shown when you click **Save** without choosing a person (Users tab) or a role (Roles tab). Choose one and save again.

**"Unauthorized Access"**

Your sign-in session may have expired. Sign in again and retry. If the error continues, contact your administrator.

**"Access Denied"**

Your account may not have the required permission for the page or action. Check the relevant event permissions or ask an administrator.

**"You can only grant or revoke permissions you already have"**

See the section about this message.

## Access-Control page: does event access apply to all events?
No. Event permissions are managed separately for each event. A person may have editing rights in one event and only viewing rights, or no configured access, in another.

## Access-Control page: who always has full access?
The main administrator account has full access according to the current system behaviour. Administrators are also not limited by their own permissions when granting or removing access.

If you are unsure whether you have enough authority to grant a permission, ask your administrator to review it.

## Frequently asked questions: Access-Control page
**How can I let someone manage my event?** Give them access on the **Access-Control** step: open **Event** from the sidebar, click **Access-Control**, select the **Users** tab and click **User Accesses**. Choose the person's role and the person, the parts of the event, Read or Write, and the access dates, then click **Save**.

**How do I allow my colleague to edit match details?** Give them **Write** permission for the module they need on the **Access-Control** step and save. Write on one module does not give Write on the others.

**How can I give someone access for just three days?** When setting their access, choose **3 Days** in the **Quick Selections** of **Access Date** (or set **From** and **To**), then save. Outside those dates the permission shows Read instead of Edit.

**Why can't my staff open Playing Order?** They may not have permission for that module in this event. On **Access-Control**, check their permissions for Playing Order and give Write if they need to change it.

**How do I remove a person's event access?** On **Access-Control**, click the edit icon of the person or role in the **Action** column, then **Delete** in the side panel. To remove several entries, tick their rows, click **Delete** and confirm **Yes, Reset**. This removes their access to this event only.

**Why can't I give someone permission?** You may not have the right to manage this event's access, or you are trying to give a permission you do not hold yourself. Ask an administrator.

**Why is the Users list greyed out?** Choose a role in **Roles** first. When editing an existing entry, the role and user cannot be changed.

**Can I give the Admin role access here?** No. The Admin role is not offered in the role list.

**Do I get a success message after saving?** The side panel closes and the table refreshes with the new permissions.

**Why can someone view the event but not change anything?** They have **Read** (not Write) for that module, or their access dates have not started yet or have ended: a cell then shows **Read** even if Write was given. On **Access-Control**, open their entry with the edit icon, tick **Write** for the module and check the **Access Date** range.
