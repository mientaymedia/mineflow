# UI & Navigation APIs

## showToast

Display a simple toast message.

```ts
import { showToast } from "zmp-sdk/apis";

await showToast({
  message: "Operation successful"
});
```

Some package versions may support more options, but current public docs emphasize `message`. Verify types before using extra fields like `duration`.

## closeLoading

Hide splash/loading screen.

```ts
import { closeLoading } from "zmp-sdk/apis";

await closeLoading({});
```

## configAppView

Configure Mini App view chrome.

```ts
import { configAppView } from "zmp-sdk/apis";

await configAppView({
  headerColor: "#1843EF",
  headerTextColor: "white",
  statusBarType: "normal",
  actionBarHidden: false,
  hideAndroidBottomNavigationBar: true,
  hideIOSSafeAreaBottom: false
});
```

## Navigation Bar

```ts
import {
  setNavigationBarColor,
  setNavigationBarTitle,
  setNavigationBarLeftButton
} from "zmp-sdk/apis";

await setNavigationBarColor({ color: "#006AF5" });
await setNavigationBarTitle({ title: "New Title" });
await setNavigationBarLeftButton({ type: "back" }); // "back" | "home"
```

## hideKeyboard

```ts
import { hideKeyboard } from "zmp-sdk/apis";

await hideKeyboard({});
```

## Routing APIs

### closeApp

```ts
import { closeApp } from "zmp-sdk/apis";

await closeApp({});
```

### openMiniApp

```ts
import { openMiniApp } from "zmp-sdk/apis";

await openMiniApp({
  appId: "target-mini-app-id",
  path: "/page?param=value"
});
```

### openWebview

```ts
import { openWebview } from "zmp-sdk/apis";

await openWebview({ url: "https://example.com" });
```

### sendDataToPreviousMiniApp

```ts
import { sendDataToPreviousMiniApp } from "zmp-sdk/apis";

await sendDataToPreviousMiniApp({
  data: { result: "success" }
});
```

### getRouteParams

```ts
import { getRouteParams } from "zmp-sdk/apis";

const params = getRouteParams();
```

Use route params only as untrusted input. Validate before backend calls.
