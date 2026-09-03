# MineFlow Skills

Claude Code skills used to build and grow MineFlow.

| Skill | Dùng khi |
|---|---|
| [`zalo-mini-app`](skills/zalo-mini-app/) | Xây Zalo Mini App: ZaUI, zmp-sdk, payment, Open API, eKYC, publish |
| [`linkedin-auto-post`](skills/linkedin-auto-post/) | Xây nội dung LinkedIn quảng bá sản phẩm và đăng tự động bài viết kèm ảnh |

---

## zalo-mini-app

Build Zalo Mini Apps - lightweight web apps running inside the Zalo super-app platform.

### What's Updated

- **SDK contract fixes** - `getPhoneNumber` and `getLocation` document token-based backend exchange flows instead of direct sensitive data returns.
- **Media API fixes** - `openMediaPicker` now uses current parameter names like `maxSelectItem`, current media types, and `{ data }` response shape.
- **Local File Storage** - Uses current `LFSStorage` namespace with `isSupportLFS`, `saveFile`, `getFileInfo`, `getSavedFileList`, `removeSavedFile`.
- **Payment** - Added Checkout / Payment integration guide: create order, callbacks, status checks, refund, payment methods.
- **Open APIs** - Added partner/open API coverage: webhook, signature verification, partner deployment/publish APIs, KYB references.
- **eKYC** - Added high-level eKYC API map and secure integration notes.
- **ZaUI refresh** - Notes current docs track ZaUI 1.11.x, with container/layout utilities like `Box`, `Center`, `Stack`, `Grid`, `Cluster`, `ZBox`.
- **DevTools refresh** - Notes both CLI and Zalo Mini App Extension flows.
- **API taxonomy refresh** - Adds newer API groups: permission, biometric auth, advertising, widgets, local file storage, documents.
- **Zalo/OA and biometric fixes** - Updates `followOA`, `viewOAQr`, `openProfilePicker`, camera permission, network type, and biometric auth examples to current docs.

### Installation

#### Using add-skill CLI

```bash
# Install to current project
npx add-skill neddtu/zalo-mini-app-skills

# Install globally
npx add-skill neddtu/zalo-mini-app-skills -g

# Install for specific agent
npx add-skill neddtu/zalo-mini-app-skills -a claude-code
```

#### Manual Installation

```bash
git clone https://github.com/neddtu/zalo-mini-app-skills.git
cp -r zalo-mini-app-skills/skills/zalo-mini-app ~/.claude/skills/
```

For Codex/ClaudeKit-style local skills:

```bash
cp -r zalo-mini-app-skills/skills/zalo-mini-app ~/.agents/skills/
```

### Usage

The skill activates when you ask about:

- Building Zalo Mini Apps
- ZaUI components
- Zalo Mini App SDK APIs
- Permission/user profile/phone number/location flows
- Storage, local files, camera/media, document preview
- Payment and Checkout integration
- Open APIs, partner APIs, KYB/eKYC
- Mini App publication, review, testing, CLI/Extension workflow

Example prompts:

- "Create a Zalo Mini App with bottom navigation"
- "Use the latest getPhoneNumber flow safely"
- "Integrate Zalo Mini App payment callback"
- "Add Local File Storage support"
- "Review this Mini App against Zalo design guidelines"

### Skill Structure

```text
skills/zalo-mini-app/
├── SKILL.md
└── references/
    ├── getting-started.md
    ├── api-overview.md
    ├── api-user.md
    ├── api-storage.md
    ├── api-ui.md
    ├── api-device.md
    ├── api-local-file-storage.md
    ├── api-permission-biometric.md
    ├── api-advertising-widgets.md
    ├── api-zalo.md
    ├── payment-checkout.md
    ├── open-apis.md
    ├── ekyc-apis.md
    ├── zaui-overview.md
    ├── zaui-layout.md
    ├── zaui-display.md
    ├── zaui-form.md
    ├── zaui-overlay.md
    ├── design-guidelines.md
    ├── web-design-guidelines.md
    └── react-best-practices.md
```

### Official Resources

- [Zalo Mini App Documentation](https://miniapp.zaloplatforms.com/documents/)
- [API Documentation](https://miniapp.zaloplatforms.com/documents/api/)
- [ZaUI Documentation](https://miniapp.zaloplatforms.com/documents/zaui/)
- [Payment Documentation](https://miniapp.zaloplatforms.com/documents/payment/)
- [Open APIs](https://miniapp.zaloplatforms.com/documents/open-apis/)
- [eKYC APIs](https://miniapp.zaloplatforms.com/documents/ekyc/)
- [Mini App Center](https://miniapp.zaloplatforms.com/)
- [Agent Skills Specification](https://agentskills.io/specification)

## License

MIT

---

## linkedin-auto-post

Xây nội dung LinkedIn quảng bá sản phẩm B2B SaaS và đăng tự động bài viết kèm ảnh.

Hai lớp:

- **Content** — ICP, 5 content pillar, 20 hook, 12 template bài tiếng Việt, playbook làm ảnh, lịch 30 ngày, KPI dẫn tới pipeline.
- **Automation** — hàng đợi CSV + script Python (chỉ thư viện chuẩn) đẩy bài kèm ảnh qua LinkedIn Posts API và Images API, chạy bằng cron hoặc GitHub Actions.

```bash
export LINKEDIN_ACCESS_TOKEN="..."

# Xem trước payload, không gọi API
python3 skills/linkedin-auto-post/scripts/linkedin_post.py \
  --text-file bai-001.txt --image anh.png \
  --alt-text "Biểu đồ tỉ lệ khách quay lại" --dry-run

# Đăng các bài đã tới hạn trong hàng đợi
python3 skills/linkedin-auto-post/scripts/run_queue.py --queue content-queue.csv --limit 1
```

### Skill Structure

```text
skills/linkedin-auto-post/
├── SKILL.md
├── references/
│   ├── content-strategy.md      # ICP, pillar, hook bank, lịch 30 ngày, KPI, rủi ro
│   ├── post-templates.md        # 12 template bài viết tiếng Việt
│   ├── image-playbook.md        # kích thước, 6 mẫu visual, bộ màu, alt text
│   ├── linkedin-api.md          # OAuth, author URN, Images API, Posts API, lỗi thường gặp
│   └── automation-runbook.md    # schema CSV, cron, GitHub Actions, token, guardrail
├── scripts/
│   ├── linkedin_post.py         # đăng 1 bài: text / 1 ảnh / nhiều ảnh
│   └── run_queue.py             # đọc CSV, đăng bài tới hạn, ghi ngược kết quả
└── assets/
    ├── content-queue.example.csv
    ├── drafts/
    └── img/
```

### Official Resources

- [LinkedIn Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)
- [LinkedIn Images API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api)
- [LinkedIn Developer Portal](https://developer.linkedin.com/)
