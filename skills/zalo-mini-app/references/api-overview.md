# Zalo Mini App API Overview

## Installation

```bash
npm install zmp-sdk
```

## Import Pattern

```ts
import { apiName } from "zmp-sdk/apis";
```

Most APIs support Promise style. Some docs/examples may also include callback-style `success`/`fail`. Prefer Promise/`async` unless project convention differs.

## API Categories

### User & Authorization

See [api-user.md](./api-user.md)

- `authorize`
- `getUserID`
- `getUserInfo`
- `getPhoneNumber` - token-based phone flow
- `getAccessToken`
- `getSetting`
- `getAppInfo`
- `getSystemInfo`
- `getDeviceIdAsync`
- `getContextAsync`

### Storage

See [api-storage.md](./api-storage.md)

- `setItem`, `getItem`, `removeItem`, `clear`
- `getStorageInfo`
- legacy/native aliases: `setStorage`, `getStorage`, `removeStorage`, `clearStorage`, `getNativeStorageInfo`

### UI & Navigation

See [api-ui.md](./api-ui.md)

- `showToast`, `closeLoading`
- `configAppView`
- `setNavigationBarColor`, `setNavigationBarTitle`, `setNavigationBarLeftButton`
- `hideKeyboard`
- `closeApp`, `openMiniApp`, `openWebview`, `sendDataToPreviousMiniApp`, `getRouteParams`

### Device, Media & Documents

See [api-device.md](./api-device.md)

- `getLocation`
- `createCameraContext`, camera context methods/events
- `requestCameraPermission`, `checkZaloCameraPermission`
- `chooseImage`, `openMediaPicker`
- `saveImageToGallery`, `saveVideoToGallery`
- `downloadFile`, `openDocument`
- `scanQRCode`, `checkNFC`, `scanNFC`
- `getNetworkType`, `onNetworkStatusChange`
- `vibrate`, `keepScreen`

### Local File Storage

See [api-local-file-storage.md](./api-local-file-storage.md)

- `isSupportLFS`
- `saveFile`
- `getFileInfo`
- `getSavedFileList`
- `removeSavedFile`

### Permissions & Biometric Auth

See [api-permission-biometric.md](./api-permission-biometric.md)

- `openPermissionSetting`
- `requestSendNotification`
- `requestUpdateZalo`
- `checkStateBioAuthentication`
- `openBioAuthentication`

### Advertising & Widgets

See [api-advertising-widgets.md](./api-advertising-widgets.md)

- `setupAd`, `loadAd`, `displayAd`, `refreshAd`
- `showFunctionButtonWidget`
- `showOAWidget`

### Zalo Features

See [api-zalo.md](./api-zalo.md)

- `followOA`, `unfollowOA`, `interactOA`, `viewOAQr`
- `openChat`, `openPhone`, `openSMS`
- `openProfile`, `openProfilePicker`
- `openShareSheet`, `openPostFeed`
- `createShortcut`, `addRating`, `minimizeApp`, `favoriteApp`

### Payment / Open APIs / eKYC

Backend-facing docs:

- [payment-checkout.md](./payment-checkout.md)
- [open-apis.md](./open-apis.md)
- [ekyc-apis.md](./ekyc-apis.md)

## Events

```ts
import { events, EventName } from "zmp-sdk/apis";

events.on(EventName.NetworkChanged, (data) => {});
events.on(EventName.AppPaused, () => {});
events.on(EventName.AppResumed, () => {});
events.on(EventName.OpenApp, () => {});
events.on(EventName.OnDataCallback, (data) => {});
```

Event names vary by SDK version. Verify against installed `zmp-sdk` types.

## Error Handling

```ts
import { AppError } from "zmp-sdk";

try {
  const result = await someApi({});
} catch (error) {
  if (error instanceof AppError) {
    console.error(error.code, error.message);
  }
}
```

Common handling:

- Permission denied: show fallback / explain permission.
- Unsupported API/version: degrade gracefully or prompt update.
- Network/payment/file failures: keep idempotent retry path.

Official error docs: https://miniapp.zaloplatforms.com/documents/api/errorCode/

## Permission Notes

- Some APIs require Zalo approval before production use.
- Do not request all permissions on first load.
- Ask in-context with clear user benefit.
- Provide fallback where possible.
