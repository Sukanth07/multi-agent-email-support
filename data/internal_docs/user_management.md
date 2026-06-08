# User Management

## Roles
Nimbus uses four workspace roles:

| Role | Capabilities |
| --- | --- |
| Workspace Owner | Full control, including billing, SSO, and deletion of the workspace |
| Admin | Manage members, roles, and workspace settings; no billing deletion |
| Member | Standard access to projects and content |
| Guest | Limited access to specifically shared projects only |

There can be multiple Owners. The last remaining Owner cannot be demoted or
removed until another Owner is assigned.

## Inviting members
Admins invite members from **Admin → Members → Invite**. Invitations are sent by
email and expire after 7 days. Invited users join with the **Member** role unless
a different role is selected. Pending invitations can be revoked or resent.

## Deactivating vs. deleting
- **Deactivate** — removes access and stops billing for that member while
  preserving their content and history. Reversible.
- **Delete** — permanently removes the member; their owned content must first be
  transferred to another member. Irreversible.

## Transferring ownership of content
Before deleting a member, an Admin reassigns their projects via
**Admin → Members → ⋯ → Reassign content**. Unassigned content defaults to the
acting Admin.

## Guest access
Guests do not count toward billed seats. They can only view or edit the specific
projects shared with them and cannot see the member directory.

## Bulk management
Business and Enterprise plans support CSV import for bulk invitations and, on
Enterprise, SCIM-based automated provisioning (see the SSO article).
