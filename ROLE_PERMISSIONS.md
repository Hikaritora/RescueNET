# RescueNet Role Permissions

This document summarizes the current application permissions.

## Authentication

- The application requires login for all functional pages.
- The only public page is the login page.
- After login, users are redirected to the dashboard.

## Roles

### Rescuer

Read-only access.

Can:
- View the dashboard after login
- View incident list
- View incident details
- View resource list
- View archived reports

Cannot:
- Create incidents
- Assign resources to incidents
- Unassign resources from incidents
- Close incidents
- Add, delete, or change resource availability
- Drag resources on the incident map
- Use incident management buttons

### Dispatcher

Incident-management role.

Can:
- View the dashboard
- Create incidents
- Assign resources to incidents
- Unassign resources from incidents
- Close incidents
- View incident and resource pages

Cannot:
- Add, delete, or change resource availability
- Use admin-only resource management actions

### Admin

Full operational access.

Can:
- Do everything a dispatcher can do
- Add resources
- Delete resources
- Mark resources unavailable
- Mark resources available again
- Access the admin-related resource controls in the UI

## Superuser

Superusers are treated as having both admin and dispatcher capabilities.

## Notes

- Permission checks are enforced server-side.
- The UI hides actions that the current user should not use, but server-side checks still protect every modifying endpoint.
- Unauthorized actions return a user-facing message instead of sending the user to the login page.

