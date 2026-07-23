# Open APIs, Partner APIs & KYB

Official Open APIs docs: https://miniapp.zaloplatforms.com/documents/open-apis/

Use Open APIs from backend services, not directly from the Mini App frontend.

## Open API Topics

Docs include:

- Integration process
- Client setup
- Signature verification
- Webhook URL
- Stats
- Revoke and remove user data
- Notifications send API
- Error codes

## Signature Verification

Use signature verification for inbound webhooks and sensitive callbacks.

Implementation guidance:

- Read raw request body where signature depends on raw bytes.
- Compare signatures with timing-safe compare.
- Reject stale timestamps/nonces if docs provide them.
- Log verification failures without leaking secrets.

Docs: https://miniapp.zaloplatforms.com/documents/open-apis/open/verify-signature/

## Webhook URL

Webhook handler should:

- Validate method and content type.
- Verify signature.
- Be idempotent.
- Return quickly; offload slow processing to queue/job.
- Store event id/provider timestamp.

Docs: https://miniapp.zaloplatforms.com/documents/open-apis/open/webhook-url/

## Partner APIs

Partner API docs include:

- Setup client
- List categories
- Create Mini App
- Deploy Mini App
- List versions
- Request publish / publish Mini App
- Update app category
- QR code short link
- Payment channel
- Stats
- Revoke/remove user data

Use these for agency/platform automation. Keep credentials in backend/CI secrets.

Docs root: https://miniapp.zaloplatforms.com/documents/open-apis/partner/

## KYB APIs

KYB docs include:

- Submit business documents
- Submit owner documents
- Upload document file
- Get documents
- List permits

Implementation guidance:

- Treat KYB files as sensitive PII/business documents.
- Encrypt at rest where stored.
- Use least-privilege access.
- Avoid logging document URLs, tokens, identity numbers.
- Build review/retry states for rejected/incomplete documents.

Docs: https://miniapp.zaloplatforms.com/documents/open-apis/partner/kyb/intro/
