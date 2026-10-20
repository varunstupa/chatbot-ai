---
doc_id: tms.fixture.api-schedule-access
title: Backend logic of the scheduling and match access APIs – planner slots, venues, roles and permissions
routes:
  - tms/fixture/:participant_id/:category_id/:event_id/:event_category_id/:stage_id
aliases:
  - schedule api
  - bulk schedule rules
  - why were the matches not scheduled
  - scheduling conflict backend
  - remove slots rules
  - day plan api
  - match access api
  - grant access rules
  - revoke access rules
  - permission authority rules
  - why can I not give access
  - auto access api
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - What does the backend check before it schedules the matches?
  - Why does the schedule say "Scheduling failed due to conflicts"?
  - What does "No Matches Found For Stage Id" mean?
  - Why does the server say "You can only grant or revoke permissions you already have"?
  - What does the backend return for the day plan when the venue is missing?
backend_sources:
  - gateway/src/routers/fixture_scheduling_router.py (bulk_schedule_matches_from_fixture, get_matches_scheduling_details)
  - gateway/src/routers/planner_router.py (get_day_plan, remove_match_slots)
  - gateway/src/routers/resource_permissions_router.py (grant_auto_access_to_parents, revoke, bulk upsert, get)
  - gateway/src/routers/user_router.py (list_all_users)
  - tms/src/router/fixture_scheduling_router.py (bulk_schedule_matches_from_fixture)
  - tms/src/service/fixture_scheduling_service.py (bulk_schedule_matches)
  - tms/src/service/planner.py (get_day_plan, remove_match_slots)
  - user_role_service/src/service/resource_permissions_service.py (get, bulk upsert, revoke)
source_files:
  - src/app/shared/schedule-popup/schedule-popup.component.ts
  - src/app/shared/match-access-sidebar/match-access-sidebar.component.ts
---
# Backend logic – scheduling and match access APIs

Each section gives the gateway step, the checks in order, and the message shown. The gateway checks the login and the permission before it forwards each call. Access calls that change permissions are served by the user-role service, not by the TMS.

## Bulk schedule matches (POST planner/v1/bulk_schedule_matches_from_fixture)

- Gateway: needs Edit and Add Time Slot.
- TMS checks all matches first. The first conflict stops the request. A conflict is a participant already playing in the same time slot or a table already taken.
- Refused with "Scheduling failed due to conflicts. No matches were scheduled." (code 400). Nothing is saved in that case.
- Otherwise the venue dates are added where needed, the planner slots are found or created, and the match times and tables are saved.
- Success: "All matches scheduled successfully" (200).
- An unexpected error returns code 500 with the error text.

## Matches scheduling details (GET planner/v1/get_matches_scheduling_details)

- No match IDs sent: "No match IDs provided" (code 200 with an empty result).
- For each match: a match that is not found is skipped; a match with no slot is reported as not scheduled; a match with a slot shows its venue, start time and end time.
- Success: "Matches scheduling details retrieved successfully" (200).
- An unexpected error returns code 500 with the error text.

## Day plan (GET planner/v1/get_day_plan)

- A venue that is not found: "Event Venue Not Found" (404).
- Success: "Success" (200), with the time intervals and the planner entries of the day.

## Remove match slots (POST planner/v1/remove_match_slots)

- The gateway forwards the request to the planner. The matches lose their slots and the schedule visibility is updated. The planner rules are read here in brief; the success text is not traced in this pass.

## Venues (GET and POST event/v1/event_venues)

- The venue rules are in the shell API guide (fixture-api-shell).

## Access: read the permissions of a user role (GET resource_permissions/v1/get_resource_user_roles_feature_permissions)

- Served by the user-role service. Read only; the permission list for the chosen roles and matches is returned.

## Access: give or change permissions for chosen users (POST resource_permissions/v1/bulk_upsert_resource_user_roles_feature_permissions)

- Gateway: needs Edit on Edit Event Access Control.
- User-role service: a request that gives or removes a permission the caller does not have is refused with "You can only grant or revoke permissions you already have" (code 403).
- Success: "Resource Permissions Updated Successfully".

## Access: auto access for parent roles (POST resource_permissions/v1/grant_auto_access_to_parents)

- Gateway: needs a login and Edit on Edit Event Access Control.
- The stage matches are read from the TMS. No match data: "Failed To Fetch Matches From Tms" (400). No matches for the stage: "No Matches Found For Stage Id" (404).
- The parent role IDs of the participants are read from the TMS. A bad ID list: "Invalid participant IDs format" (400). An empty list: "Participant Ids Required" (400).
- The permissions are then saved through the same bulk save as above.

## Access: revoke permissions (POST resource_permissions/v1/revoke_resource_user_roles_feature_permissions)

- Served by the user-role service. The same authority check applies: the caller can only revoke permissions it already has.
- Success: "Permissions Revoked Successfully".

## Access: roles and users (GET role/v1/get_roles, user/v1/list_all_users)

- Roles: the role list is returned by the user-role service. The roles of the parents are in the role parents call.
- Users: list_all_users returns the users, and for the referee and umpire lists it reads the event to choose the right users. The full rules of the user list are not traced in this pass.
