# API Documentation

## Base URL and versioning
All requests go to `https://api.nimbus.com/v1`. The API is versioned in the path;
breaking changes ship under a new version and the previous version is supported
for at least 12 months after deprecation notice.

## Authentication
The API uses bearer tokens. Create a token under **Settings → Developer → API
keys**. Include it on every request:

```
Authorization: Bearer <YOUR_API_KEY>
```

Tokens inherit the permissions of the role that created them. Store tokens
securely; they are shown only once at creation. Tokens can be revoked at any time
from the same screen.

## Rate limits
- Pro: 60 requests/minute
- Business: 300 requests/minute
- Enterprise: 1000 requests/minute (negotiable)

Responses include `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers. When
the limit is exceeded the API returns `429 Too Many Requests`; clients should back
off using the `Retry-After` header.

## Pagination
List endpoints return up to 50 items by default (max 200 via `limit`). Use the
`cursor` parameter from the `next_cursor` field to page forward.

## Errors
Errors return standard HTTP status codes and a JSON body:

```json
{ "error": { "code": "invalid_request", "message": "Field 'email' is required" } }
```

Common codes: `400 invalid_request`, `401 unauthorized`, `403 forbidden`,
`404 not_found`, `429 rate_limited`, `500 server_error`.

## Webhooks
Subscribe to events (e.g. `project.created`, `member.invited`) under
**Settings → Developer → Webhooks**. Payloads are signed with an HMAC-SHA256
signature in the `X-Nimbus-Signature` header; verify it against your signing
secret to confirm authenticity. Failed deliveries retry for up to 24 hours.
