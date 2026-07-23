# Zalo Platform APIs

## Official Account (OA)

### followOA / unfollowOA

```ts
import { followOA, unfollowOA } from "zmp-sdk/apis";

await followOA({ id: "your-oa-id" });
await unfollowOA({ id: "your-oa-id" });
```

### interactOA

```ts
import { interactOA } from "zmp-sdk/apis";

await interactOA({ oaId: "your-oa-id" });
```

### viewOAQr

```ts
import { viewOAQr } from "zmp-sdk/apis";

await viewOAQr({
  id: "your-oa-id",
  displayName: "Your OA"
});
```

## Chat & Contact

### openChat

```ts
import { openChat } from "zmp-sdk/apis";

await openChat({
  type: "oa",
  id: "oa-or-user-id",
  message: "Hello!"
});
```

### openPhone / openSMS

```ts
import { openPhone, openSMS } from "zmp-sdk/apis";

await openPhone({ phoneNumber: "0900000000" });
await openSMS({ phoneNumber: "0900000000", content: "Hello" });
```

Verify exact parameter names in installed SDK types, especially when supporting older SDK versions.

## Profile & Social

### openProfile

```ts
import { openProfile } from "zmp-sdk/apis";

await openProfile({
  type: "user",
  id: "user-id"
});
```

### openProfilePicker

```ts
import { openProfilePicker } from "zmp-sdk/apis";

const { users } = await openProfilePicker({ maxProfile: 5 });
```

### openShareSheet

```ts
import { openShareSheet } from "zmp-sdk/apis";

await openShareSheet({
  type: "link",
  data: {
    link: "https://zalo.me/s/app-id",
    title: "Check this out!",
    description: "Amazing mini app",
    thumbnail: "https://example.com/thumb.jpg"
  }
});
```

### openPostFeed

```ts
import { openPostFeed } from "zmp-sdk/apis";

await openPostFeed({
  type: "link",
  data: { link: "https://example.com", title: "My Post" }
});
```

## App Features

```ts
import { createShortcut, addRating, minimizeApp, favoriteApp } from "zmp-sdk/apis";

await createShortcut({});
await addRating({});
await minimizeApp({});
await favoriteApp({});
```

Use these after meaningful user engagement, not immediately on first load.
