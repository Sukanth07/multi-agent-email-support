# Authentication

## Overview
Nimbus accounts authenticate with an email address and password by default.
Passwords must be at least 12 characters and include one number and one symbol.
Sessions remain valid for 30 days unless the user signs out or an administrator
revokes the session.

## Password reset
Users reset a forgotten password from the **Sign in** page by selecting
"Forgot password". A reset link is emailed and expires after 60 minutes. The link
can be used only once. If the email does not arrive within 10 minutes, the user
should check spam and confirm the address matches an active Nimbus account.

## Multi-factor authentication (MFA)
MFA is available on all plans and required by default on Business and Enterprise.
Supported second factors:
- Authenticator app (TOTP) — recommended
- SMS one-time code
- Hardware security keys (WebAuthn / FIDO2)

Users enroll under **Settings → Security → Two-factor authentication**.
Recovery codes are generated at enrollment and shown only once; they should be
stored securely. If a user loses all factors and recovery codes, a workspace
administrator can reset MFA from the Admin Console.

## Account lockout
After 10 consecutive failed sign-in attempts, the account is locked for 15
minutes. Repeated lockouts trigger a security email to the account owner.
Administrators can unlock an account immediately from **Admin → Members**.

## Service accounts
Automated systems should use API keys or service accounts rather than user
credentials. See the API Documentation article for token creation.
