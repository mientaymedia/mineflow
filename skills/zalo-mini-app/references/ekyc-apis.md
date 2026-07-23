# eKYC APIs

Official docs: https://miniapp.zaloplatforms.com/documents/ekyc/

Use eKYC APIs only from backend services. They handle sensitive identity data.

## Docs Areas

- Credentials
- Signature
- Encryption
- IP whitelist policy
- Appendix

API groups include:

- `generateSessionID`
- `getStatusInfo`
- `imageUpload`
- `imageSanityCheck`
- `ocrResult`
- `selfieFaceMatchingResult`
- `faceMatchingResult`
- `faceSearchUpload`
- `faceSearchResult`
- `faceRetrievalResult`
- `fraudCheckingResult`
- `logicStatusCheckingResult`

## Integration Shape

```text
Mini App
  -> backend creates eKYC session
  -> frontend uploads/captures required docs via approved flow
  -> backend calls eKYC APIs with credentials/signature/encryption
  -> backend stores status/result with retention controls
  -> frontend shows safe progress/result messages
```

## Security Requirements

- Never expose eKYC credentials in frontend.
- Follow signature and encryption docs exactly.
- Restrict source IPs when using IP whitelist policy.
- Avoid logging face images, ID images, OCR raw data, access tokens.
- Define retention/deletion policy before launch.
- Minimize frontend display of sensitive identity fields.
- Add manual review states for inconclusive/fraud signals.
