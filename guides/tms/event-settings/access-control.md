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
---

# Managing Event Access and Permissions

## What is Event Access Control?

Event Access Control lets an event organiser decide who can view information and who can make changes in a particular event.

For example:
- You want a colleague to update match information.
- You want a staff member to view event details without changing them.
- You want to allow someone to manage a particular part of the event for three days.
- You want to remove access from someone who is no longer working on the event.

You can manage access for an individual person or for a group of people who share the same role.

**Important:** Access is specific to each event. Giving someone access to one event does not automatically give them access to another event.

## How do I give someone access to my event?

Follow these steps:

1. Open the required event from the Event section.
2. Open the Access-Control step at the top of the event setup page.
3. Select the Users tab.
4. Click User Accesses.
5. Select the person's role and then select the person.
6. Choose which parts of the event the person can access.
7. Choose whether they can view information, make changes, or both, using the available permission options.
8. Set the dates during which they can make changes.
9. Click Save.

You should see "Resource Permissions Updated Successfully" when the update succeeds.

If the person is not available in the user list, check the role selection and search the list. If you still cannot find them, ask your administrator to check their account and role.

## How do I let someone change event or match details?

Give the person Write permission for the relevant event module.

For example, if they need to make changes to a particular part of the event, select Write for that module and save the permissions.

Giving Write permission to one module does not automatically give Write permission to every other module.

## What is the difference between Read and Write?

- **Read:** The person can view information but cannot make changes using that permission.
- **Write:** The person can make changes in the relevant module, subject to other system rules.
- **Delete:** The permission table may show Delete where that permission is available. Do not assume that Read or Write includes Delete.

If you want someone to view information without changing it, give them Read access rather than Write access.

## Why can someone view the event but not edit it?

This can happen for several reasons:

1. **Their access dates have expired or have not started yet.** Check the From and To dates.
2. **They have Read permission but not Write permission.** Open their access settings and check the relevant module.
3. **They have permission for a different part of the event.** Access to one module does not automatically allow changes in another.
4. **They are relying on a role permission that does not provide the required access.** Check the person's effective permissions and the role they belong to.

Correct the relevant setting, save it, and ask the person to try again.

## How do I give access for only a few days?

When setting up the person's access, use the Access Date fields:

- From: the date access begins.
- To: the date access ends.

You can also use the available quick selections: Event Start - End, 3 Days, 7 Days, or 10 Days.

For example, if a staff member needs temporary editing access, select the appropriate period and save the permissions.

Outside the permitted access dates, the permission table shows Read instead of Edit. Check the actual dates if the person can view information but cannot make changes.

## How do I give access to several people with the same role?

Use the Roles tab when you want to manage permissions for a role rather than setting up each person separately.

1. Open Access-Control and select Roles.
2. Click Role Accesses.
3. Select the role you want to manage.
4. Under Manager Permission, select Access for the relevant modules.
5. Click Save.

These permissions apply to people with that role in the current event. Use the Users tab when you need to manage one person's access individually.

## Why can't I open Playing Order or Umpire Settings?

If another event page shows "Access Denied", the user may not have the required permission for that module in the current event.

Open Access-Control and check the user's permissions for the relevant module. Make sure they have the necessary Edit permission if the task requires editing.

If you cannot grant the required permission yourself, contact an administrator.

## Why do I get "You can only grant or revoke permissions you already have"?

This message means that your account is trying to grant or remove a permission that you are not authorised to manage.

Users who are not administrators can only grant or revoke permissions they themselves hold for the current event.

Ask an administrator who has the necessary authority to make the change.

## How do I remove someone's access?

1. Open Access-Control and find the person or role.
2. Click the edit icon in the Action column.
3. Click Delete in the side panel and confirm the intended action.

To remove several entries, select their rows in the table and use Delete. Read the confirmation carefully before proceeding.

Removing an access entry removes that user's or role's configured access for this event. Do not assume that it deletes the person's account or removes their access to other events.

## Common errors

**"Unauthorized Access"**

Your sign-in session may have expired. Sign in again and retry. If the error continues, contact your administrator.

**"Access Denied"**

Your account may not have the required permission for the page or action. Check the relevant event permissions or ask an administrator.

**"Please select user or role for update score for team matches."**

The system requires a user or role selection for this operation. Check that you have selected the required user or role before saving.

## Does event access apply to all events?

No. Event permissions are managed separately for each event. A person may have editing rights in one event and only viewing rights, or no configured access, in another.

## Who always has full access?

The main administrator account has full access according to the current system behaviour.

If you are unsure whether you have enough authority to grant a permission, ask your administrator to review it.

## Frequently asked questions

**How can I let someone manage my event?** Give them access on the **Access-Control** step: open **Event** from the sidebar, click **Access-Control**, select the **Users** tab and click **User Accesses**. Choose the person's role and the person, the parts of the event, Read or Write, and the access dates, then click **Save**.

**How do I allow my colleague to edit match details?** Give them **Write** permission for the module they need on the **Access-Control** step and save. Write on one module does not give Write on the others.

**How can I give someone access for just three days?** When setting their access, choose **3 Days** in the quick selections of the **Access Date** fields (or set **From** and **To**), then save. Outside those dates the permission shows Read instead of Edit.

**Why can't my staff open Playing Order?** They may not have permission for that module in this event. On **Access-Control**, check their permissions for Playing Order and give Edit if they need to change it.

**How do I remove a person's event access?** On **Access-Control**, click the edit icon of the person or role in the **Action** column, then **Delete** in the side panel and confirm. To remove several entries, select their rows and use **Delete**. This removes their access to this event only.

**Why can't I give someone permission?** You may not have the right to manage this event's access. If you cannot grant the permission yourself, ask an administrator.
