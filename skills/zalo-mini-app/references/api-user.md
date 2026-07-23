# User & Authorization APIs

Use these APIs from `zmp-sdk/apis`.

```ts
import { authorize, getUserInfo, getPhoneNumber } from "zmp-sdk/apis";
```

## authorize

Request permission for sensitive data.

```ts
await authorize({
  scopes: ["scope.userInfo", "scope.userPhonenumber"]
});
```

Common scopes:

- `scope.userInfo` - user display name and avatar
- `scope.userPhonenumber` - phone number token flow
- `scope.userLocation` - GPS location

Notes:

- Some scopes require Mini App approval before production use.
- Admin/tester accounts can often test before review.
- Ask only when needed; explain value to user.

## getUserID

Get a stable user identifier in Mini App context.

```ts
import { getUserID } from "zmp-sdk/apis";

const userID = await getUserID({});
```

## getUserInfo

Get user profile data.

```ts
import { getUserInfo } from "zmp-sdk/apis";

const { userInfo } = await getUserInfo({
  autoRequestPermission: true,
  avatarType: "normal" // "small" | "normal" | "large"
});
```

Typical fields:

```ts
type UserInfo = {
  id: string;
  name?: string;
  avatar?: string;
  followedOA?: boolean;
  idByOA?: string;
  isSensitive?: boolean;
};
```

Handle denial:

```ts
try {
  const { userInfo } = await getUserInfo({ autoRequestPermission: true });
} catch (error: any) {
  if (error?.code === -1401) {
    // user denied permission
  }
}
```

## getPhoneNumber: Current Token-Based Flow

Current docs describe `getPhoneNumber` returning a **token**, not the actual phone number.

```ts
import { getPhoneNumber } from "zmp-sdk/apis";

const { token } = await getPhoneNumber({});
await fetch("/api/zalo/phone-number", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ token })
});
```

Backend responsibilities:

1. Receive `token` from Mini App.
2. Call Zalo Open API endpoint for phone number exchange with proper app credentials/access token.
3. Return normalized phone number to app only if product really needs it.
4. Do not log raw token or phone number unless required and protected.

Security notes:

- Token is short-lived and single-use.
- Exchange token immediately.
- Do not expose app secret/client secret in frontend.
- Store phone only with clear user purpose and data retention rules.

Outdated pattern to avoid:

```ts
// Avoid. Current docs do not return { number } directly.
const { number } = await getPhoneNumber({});
```

Official docs: https://miniapp.zaloplatforms.com/documents/api/getPhoneNumber/

## getAccessToken

Get an access token for backend verification / Open API calls.

```ts
import { getAccessToken } from "zmp-sdk/apis";

const { accessToken } = await getAccessToken({});
```

Send token to backend over HTTPS. Validate with Zalo Open APIs server-side.

## getSetting

Check permission status.

```ts
import { getSetting } from "zmp-sdk/apis";

const settings = await getSetting({});
// e.g. { "scope.userInfo": true, "scope.userPhonenumber": false }
```

If permission is disabled, consider `openPermissionSetting` from permission APIs.

## getAppInfo

```ts
import { getAppInfo } from "zmp-sdk/apis";

const appInfo = await getAppInfo({});
```

## getSystemInfo

```ts
import { getSystemInfo } from "zmp-sdk/apis";

const system = await getSystemInfo({});
// platform, zaloVersion, language, screen size, status bar, safe areas, etc.
```

## getDeviceIdAsync

```ts
import { getDeviceIdAsync } from "zmp-sdk/apis";

const deviceId = await getDeviceIdAsync({});
```

Use only when device-level behavior is justified. Avoid fingerprinting-like use.

## getContextAsync

Get context when the Mini App opened.

```ts
import { getContextAsync } from "zmp-sdk/apis";

const context = await getContextAsync({});
```

Use for entry point/referrer-aware routing, not for security decisions by itself.
