# Integrations

## Available integrations
Nimbus connects with common workplace tools:
- **Slack** — post project updates and notifications to channels
- **Microsoft Teams** — notifications and link unfurling
- **Google Drive** and **OneDrive** — attach and preview files
- **GitHub** and **GitLab** — link commits and pull requests to projects
- **Jira** — two-way issue sync
- **Zapier** — connect to 5000+ apps without code

## Connecting an integration
Admins enable integrations under **Admin → Integrations**. Individual members
authorize their own accounts the first time they use a connected feature.
Connecting requires granting OAuth permissions in the third-party tool; Nimbus
requests the minimum scopes needed.

## Slack setup
1. Go to **Admin → Integrations → Slack → Connect**.
2. Approve the requested scopes in Slack.
3. Choose a default channel for workspace notifications.
4. Members can route specific projects to channels with `/nimbus link` in Slack.

## Permissions and data
Integrations respect Nimbus permissions: a user only sees data through an
integration that they could see in Nimbus directly. Disconnecting an integration
immediately revokes its access tokens.

## Jira two-way sync
Status and comments sync both directions every 5 minutes. Field mapping is
configured per project. Conflicts resolve to the most recent change.

## Troubleshooting
- **Notifications stopped** — the OAuth token may have expired; reconnect from
  **Admin → Integrations**.
- **Duplicate items** — disable and re-enable sync to reset the mapping cursor.
- Integrations are available on Pro and above; Enterprise adds Jira and SCIM.
