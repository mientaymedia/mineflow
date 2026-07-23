# Getting Started with Zalo Mini App

Official docs: https://miniapp.zaloplatforms.com/documents/intro/getting-started/

## Prerequisites

- Node.js installed.
- Zalo developer account.
- Zalo App created and activated.
- Mini App created in Mini App Center.
- Required permissions reviewed/approved for production APIs.

## High-Level Flow

1. Create Zalo App.
2. Create Mini App under that Zalo App.
3. Verify/authenticate Mini App as required by current docs.
4. Configure permissions, app info, category, OA/payment if needed.
5. Develop with CLI or Zalo Mini App Extension.
6. Test on real Zalo app/device.
7. Deploy test version.
8. Submit for review.
9. Publish approved version.
10. Monitor, notify users, and reconcile backend events.

## Install CLI

```bash
npm install -g zmp-cli
zmp login
```

## Create Project

```bash
zmp create my-app
cd my-app
zmp start
```

Alternative: use the Zalo Mini App Extension/IDE flow from official DevTools docs.

## Project Structure

Typical projects include:

```text
my-app/
├── src/
│   ├── pages/
│   ├── components/
│   └── app.tsx | app.jsx | app.js
├── app-config.json
├── package.json
└── vite.config.* / build config
```

## app-config.json

Example shape:

```json
{
  "app": {
    "title": "My App",
    "headerColor": "#006AF5",
    "headerTitle": "App Title",
    "textColor": "white",
    "leftButton": "back",
    "statusBar": "normal",
    "actionBarHidden": false
  },
  "listCSS": [],
  "listSyncJS": [],
  "listAsyncJS": []
}
```

Check current official app-config docs for exact fields:
https://miniapp.zaloplatforms.com/documents/devtools/app-config/

## Run & Test

```bash
zmp start
```

Test on device:

1. Open Zalo app.
2. Use QR/test link from Mini App Center or devtools.
3. Test permissions, phone token flow, location, media, payment callbacks on real devices.

## Deploy

```bash
zmp deploy
```

CLI docs:

- https://miniapp.zaloplatforms.com/documents/devtools/cli/commands/login/
- https://miniapp.zaloplatforms.com/documents/devtools/cli/commands/start/
- https://miniapp.zaloplatforms.com/documents/devtools/cli/commands/deploy/

## Convert Existing Web App

```bash
cd your-web-app
zmp init
```

Common adjustments:

- Root element should match Mini App template (often `#app`).
- For Vite, use relative base such as `base: "./"` when needed.
- Avoid browser APIs unavailable in Zalo webview.
- Replace web-only auth/payment with Zalo Mini App flows.

## Publishing Checklist

- App name, icon, description, category are accurate.
- Required permissions approved.
- User data purpose clear.
- Phone number flow uses backend token exchange.
- Payment callbacks verified server-side.
- UI follows Zalo design and safe areas.
- No crashes on Android/iOS Zalo current versions.
- Bundle/performance acceptable.
- No secrets in frontend bundle.
