# Permission & Biometric APIs

## Permission Settings

Use `getSetting` to inspect permissions and `openPermissionSetting` to let users adjust permissions.

```ts
import { getSetting, openPermissionSetting } from "zmp-sdk/apis";

const settings = await getSetting({});
if (!settings["scope.userLocation"]) {
  await openPermissionSetting({});
}
```

Use a clear in-app explanation before opening permission settings.

## requestSendNotification

Ask for permission to send notifications where product flow needs it.

```ts
import { requestSendNotification } from "zmp-sdk/apis";

await requestSendNotification({});
```

Use only after user action. Do not ask on first app load unless app purpose requires it.

## requestUpdateZalo

Prompt user to update Zalo when a required native capability is unavailable.

```ts
import { requestUpdateZalo } from "zmp-sdk/apis";

await requestUpdateZalo({});
```

## Biometric Authentication

Docs include biometric integration APIs:

- `checkStateBioAuthentication`
- `openBioAuthentication`

Biometric authentication is a controlled/partner-sensitive flow. Current `openBioAuthentication` requires one-time `secretData` generated for the authentication event; do not use old examples with `reason`.

```ts
import { checkStateBioAuthentication, openBioAuthentication } from "zmp-sdk/apis";

try {
  const { bioState } = await checkStateBioAuthentication({});
  // Persist bioState and compare on later logins to detect biometric changes.
  const result = await openBioAuthentication({
    secretData: "<one-time-secret-data-from-server>",
    ui: {
      title: "Biometric login",
      subTitle: "Use biometrics to confirm this action",
      negativeButtonText: "Cancel"
    }
  });
} catch (error) {
  // Device does not support biometric auth, has no biometric lock, or API failed.
}
```

Security notes:

- Biometrics confirm local user presence; they are not backend identity proof by themselves. Pair `secretData` with backend verification/webhook flow where required.
- Pair biometric success with server-side session/auth checks for sensitive actions.
- Provide fallback PIN/password/OTP if product requires access recovery.

Official docs: https://miniapp.zaloplatforms.com/documents/api/biometric-authentication-integration/
