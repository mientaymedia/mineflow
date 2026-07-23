# Advertising & Widget APIs

Current API docs include ads and UI widgets. Use only when Mini App has approval and UX reason.

## Advertising

APIs in docs:

- `setupAd`
- `loadAd`
- `displayAd`
- `refreshAd`

Typical flow:

```ts
import { setupAd, loadAd, displayAd } from "zmp-sdk/apis";

await setupAd({});
await loadAd({});
await displayAd({});
```

Implementation guidance:

- Do not block core task with ads.
- Handle unsupported/no-fill states.
- Respect Zalo policy and review requirements.
- Keep ad calls behind feature flags if rollout risk exists.

Official docs: https://miniapp.zaloplatforms.com/documents/api/setupAd/

## Function Button Widget

```ts
import { showFunctionButtonWidget } from "zmp-sdk/apis";

await showFunctionButtonWidget({});
```

Use for platform-supported function buttons where docs/policy permit.

## OA Widget

```ts
import { showOAWidget } from "zmp-sdk/apis";

await showOAWidget({});
```

Use to encourage OA follow/contact without disrupting main flow.
