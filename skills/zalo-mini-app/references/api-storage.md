# Storage APIs

Local storage persists on user's device for Mini App data. Use for lightweight non-sensitive app state and cache.

## setItem

```ts
import { setItem } from "zmp-sdk/apis";

await setItem({
  data: {
    key1: "value1",
    key2: { nested: "object" },
    key3: [1, 2, 3]
  }
});
```

## getItem

```ts
import { getItem } from "zmp-sdk/apis";

const { key1, key2 } = await getItem({
  keys: ["key1", "key2"]
});
```

## removeItem

```ts
import { removeItem } from "zmp-sdk/apis";

await removeItem({ keys: ["key1", "key2"] });
```

## clear

```ts
import { clear } from "zmp-sdk/apis";

await clear({});
```

## getStorageInfo

```ts
import { getStorageInfo } from "zmp-sdk/apis";

const { keys, currentSize, limitSize } = await getStorageInfo({});
```

## Legacy / Native Aliases

Current docs also list storage-like aliases:

- `setStorage`
- `getStorage`
- `removeStorage`
- `clearStorage`
- `getNativeStorageInfo`

Prefer the project-standard API. Check installed `zmp-sdk` types before mixing aliases.

## Best Practices

- Store only essential data.
- Use server as source of truth for important records.
- Avoid secrets, access tokens, raw phone numbers, identity documents.
- Add version prefix to cache keys.
- Handle quota exceeded and corrupted data.

## Example: Address Cache

```ts
async function getAddresses() {
  const { addresses } = await getItem({ keys: ["addresses"] });
  return Array.isArray(addresses) ? addresses : [];
}

async function saveAddress(address: unknown) {
  const addresses = await getAddresses();
  addresses.push(address);
  await setItem({ data: { addresses } });
  return addresses;
}
```
