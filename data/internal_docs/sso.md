# Single Sign-On (SSO)

## Availability
SSO is included on the **Business** and **Enterprise** plans. It is not available
on Starter or Pro. Enabling SSO requires the **Workspace Owner** role.

## Supported protocols
- **SAML 2.0** — Okta, Microsoft Entra ID (Azure AD), Google Workspace, OneLogin, Ping
- **OIDC** — any OpenID Connect compliant identity provider

## Setup (SAML)
1. In Nimbus, go to **Admin → Authentication → SSO** and copy the **ACS URL** and
   **Entity ID**.
2. In your identity provider, create a new SAML application using those values.
3. Map the SAML attributes `email`, `firstName`, and `lastName`.
4. Paste the IdP **metadata URL** or upload the metadata XML into Nimbus.
5. Use **Test connection** before enforcing.

## Just-in-time (JIT) provisioning
When enabled, a Nimbus account is created automatically the first time a user
authenticates through the IdP. Default role for JIT users is **Member**.

## Enforcing SSO
Once SSO is verified, administrators can enable **Require SSO** to disable
password sign-in for all members. Workspace Owners retain a password-based
break-glass login in case the IdP is unavailable.

## SCIM provisioning
Enterprise plans support SCIM 2.0 for automated user provisioning and
deprovisioning. Deprovisioning through SCIM immediately revokes active sessions.

## Common issues
- **"SAML response rejected"** — clock skew over 5 minutes or a mismatched Entity
  ID. Confirm the IdP and Nimbus values match exactly.
- **User lands in the wrong workspace** — the IdP is sending an incorrect
  RelayState; reconfigure the default relay in the IdP app.
