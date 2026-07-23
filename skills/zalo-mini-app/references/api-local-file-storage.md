# Local File Storage APIs

Local File Storage (LFS) stores files locally on the user's device for Mini App reuse.

Official docs: https://miniapp.zaloplatforms.com/documents/api/localFileSystem/

## Support Check

Docs note LFS support begins around `zmp-sdk@2.51.0` and newer Zalo app versions. Check support at runtime.

```ts
import { LFSStorage } from "zmp-sdk/apis";

const { support } = await LFSStorage.isSupportLFS();
if (!support) {
  // fallback: remote URL, normal cache, or ask user to update Zalo
}
```

Current docs expose LFS APIs under `LFSStorage`. Verify installed SDK types when supporting old package versions.

## saveFile

Save a temporary/downloaded file into local file storage.

```ts
import { LFSStorage } from "zmp-sdk/apis";

const { savedPath } = await LFSStorage.saveFile({
  filePath: "local-temp-path-or-downloaded-path"
});
```

## getFileInfo

```ts
import { LFSStorage } from "zmp-sdk/apis";

const info = await LFSStorage.getFileInfo({
  filePath: "saved-file-path"
});
```

## getSavedFileList

```ts
import { LFSStorage } from "zmp-sdk/apis";

const { list } = await LFSStorage.getSavedFileList({});
```

## removeSavedFile

```ts
import { LFSStorage } from "zmp-sdk/apis";

await LFSStorage.removeSavedFile({
  filePath: "saved-file-path"
});
```

## Implementation Guidance

- Treat LFS as cache, not authoritative storage.
- Keep server copy for important documents.
- Add cache invalidation by app version/user id/data version.
- Provide fallback for unsupported devices/Zalo versions.
- Avoid storing sensitive documents unless encrypted/server policy allows.
