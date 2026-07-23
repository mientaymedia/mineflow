# ZaUI Components

Official docs: https://miniapp.zaloplatforms.com/documents/zaui/

Docs currently track ZaUI 1.11.x. `npm view zmp-ui version` observed `1.11.14` on 2026-06-24.

## Installation

```bash
npm install zmp-ui
```

## Usage

```tsx
import { App, Page, Button, Input, Modal } from "zmp-ui";
import "zmp-ui/zaui.css";
```

## Categories

### Foundation

- Colors
- Typography
- Spacing
- Corner radius
- Shadow
- Icons
- Header
- Mini App logo
- Level specification

### Layout / Container

See [zaui-layout.md](./zaui-layout.md)

- `App`
- `Page`
- `Header`
- `BottomNavigation`
- `Tabs`
- `ZMPRouter`
- `AnimationRoutes`
- `Box`
- `Center`
- `Cluster`
- `Grid`
- `Stack`
- `ZBox`

### Display

See [zaui-display.md](./zaui-display.md)

- `Avatar`
- `Calendar`
- `Icon`
- `ImageViewer`
- `List`
- `Progress`
- `Spinner`
- `Swiper`
- `Text`

### Form

See [zaui-form.md](./zaui-form.md)

- `Button`
- `Input`
- `Password`
- `Search`
- `TextArea`
- `OTP`
- `Select`
- `Picker`
- `DatePicker`
- `Switch`
- `Checkbox`
- `Radio`
- `Slider`

### Overlay

See [zaui-overlay.md](./zaui-overlay.md)

- `Modal`
- `Sheet`
- `ActionSheet`
- `SnackbarProvider` / `Snackbar`

## Design Tokens

Primary color: `#006AF5`.

Use official foundation docs for exact current token values:

- https://miniapp.zaloplatforms.com/documents/zaui/foundation/colors/
- https://miniapp.zaloplatforms.com/documents/zaui/foundation/typography/
- https://miniapp.zaloplatforms.com/documents/zaui/foundation/spacing/

## Implementation Guidance

- Prefer ZaUI primitives over custom controls for platform consistency.
- Verify props against installed `zmp-ui` types.
- Respect safe areas and Zalo header/menu placement.
- Use semantic HTML/accessibility wrappers when ZaUI component lacks needed aria behavior.
