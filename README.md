# Zalo Mini App Skills

Build Zalo Mini Apps - lightweight web apps running inside the Zalo super-app platform.

## What's Updated

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

## Installation

### Using add-skill CLI

```bash
# Install to current project
npx add-skill neddtu/zalo-mini-app-skills

# Install globally
npx add-skill neddtu/zalo-mini-app-skills -g

# Install for specific agent
npx add-skill neddtu/zalo-mini-app-skills -a claude-code
```

### Manual Installation

```bash
git clone https://github.com/neddtu/zalo-mini-app-skills.git
cp -r zalo-mini-app-skills/skills/zalo-mini-app ~/.claude/skills/
```

For Codex/ClaudeKit-style local skills:

```bash
cp -r zalo-mini-app-skills/skills/zalo-mini-app ~/.agents/skills/
```

## Usage

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

## Skill Structure

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

## Official Resources

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
