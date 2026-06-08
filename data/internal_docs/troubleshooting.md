# Troubleshooting Guides

## Cannot sign in
1. Confirm the email matches an active account.
2. If using SSO, sign in through your identity provider, not the password form.
3. Reset the password if needed (link expires in 60 minutes).
4. If the account is locked after failed attempts, wait 15 minutes or ask an
   admin to unlock it.
5. Clear cookies for `nimbus.com` or try a private browser window.

## Email notifications not arriving
- Check **Settings → Notifications** to confirm the type is enabled.
- Verify the address and check spam/quarantine.
- Corporate mail filters sometimes block `notifications@nimbus.com`;
  ask IT to allowlist the domain.

## Slow performance or loading errors
- Check the status page at `status.nimbus.com` for ongoing incidents.
- Hard refresh (Ctrl/Cmd+Shift+R) to clear cached assets.
- Disable browser extensions that may interfere.
- Supported browsers: latest Chrome, Edge, Firefox, and Safari.

## File upload fails
- Maximum file size is 100 MB on Pro and 5 GB on Business and Enterprise.
- Confirm the file type is allowed; executables are blocked for security.
- A stalled upload usually indicates a network timeout; retry on a stable
  connection.

## Integration not syncing
- Reconnect the integration if its OAuth token expired.
- See the Integrations article for tool-specific steps.

## Still stuck
Collect the error message, the time it occurred, your browser/OS, and the
affected workspace URL, then contact support. Enterprise customers can use
priority channels described in the Enterprise Support article.
