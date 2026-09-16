# Step 9 — Role-Based Access Control

DocuMind AI now has a backend RBAC baseline using the existing authenticated user role.

## Roles

- **Admin** — workspace administration and user-role management.
- **Employee** — normal document-processing workspace user.
- **Auditor** — audit-log access for traceability reviews.

## Implemented controls

1. Reusable `require_roles(...)` dependency returns HTTP 403 for unauthorized roles.
2. `GET /api/v1/users` is restricted to Admin.
3. `PATCH /api/v1/users/{user_id}/role` is restricted to Admin.
4. Admins cannot remove their own Admin role.
5. Role changes create an `USER_ROLE_UPDATED` audit event.
6. `GET /api/v1/audit-logs` is restricted to Admin and Auditor.
7. Existing JWT authentication and active-user checks remain the authentication layer.

## Role assignment

New public registrations continue to default to Employee. An existing Admin can assign Admin, Employee, or Auditor to another account through the protected role-management endpoint.

## Security notes

RBAC is enforced on the API, not only by hiding frontend controls. Frontend visibility can be added as a usability layer, but it is not treated as the security boundary.
