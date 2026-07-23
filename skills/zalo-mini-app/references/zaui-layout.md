# ZaUI Layout & Container Components

## App

Root component wrapping the Mini App.

```tsx
import { App } from "zmp-ui";

<App>{children}</App>
```

## Page

```tsx
import { Page, Header } from "zmp-ui";

<Page>
  <Header title="Page Title" />
  <main className="page-content">Content</main>
</Page>
```

Common props include scroll restoration / scrollbar behavior. Verify exact names in installed types.

## Header

```tsx
import { Header } from "zmp-ui";

<Header title="My Page" showBackIcon onBackClick={() => navigate(-1)} />
```

## BottomNavigation

```tsx
import { BottomNavigation, Icon } from "zmp-ui";

<BottomNavigation fixed>
  <BottomNavigation.Item key="home" label="Home" icon={<Icon icon="zi-home" />} />
  <BottomNavigation.Item key="profile" label="Profile" icon={<Icon icon="zi-user" />} />
</BottomNavigation>
```

Keep primary tabs concise. Zalo design recommends limited main destinations.

## Tabs

```tsx
import { Tabs } from "zmp-ui";

<Tabs defaultActiveKey="tab1">
  <Tabs.Tab key="tab1" label="Tab 1">Content 1</Tabs.Tab>
  <Tabs.Tab key="tab2" label="Tab 2">Content 2</Tabs.Tab>
</Tabs>
```

## Router

```tsx
import { ZMPRouter, AnimationRoutes, Route } from "zmp-ui";

<ZMPRouter>
  <AnimationRoutes>
    <Route path="/" element={<HomePage />} />
    <Route path="/profile" element={<ProfilePage />} />
  </AnimationRoutes>
</ZMPRouter>
```

## Box / Center / Cluster / Grid / Stack / ZBox

Current ZaUI docs include container/layout utilities.

```tsx
import { Box, Stack, Grid, Center, Cluster } from "zmp-ui";

<Stack space="m">
  <Box p={4}>Card content</Box>
  <Grid columns={2} gap={4}>...</Grid>
  <Center>Centered</Center>
  <Cluster>Inline cluster</Cluster>
</Stack>
```

Exact props differ by version; check `zmp-ui` docs/types.

Official examples:

- https://miniapp.zaloplatforms.com/documents/zaui/container/box/
- https://miniapp.zaloplatforms.com/documents/zaui/container/stack/
- https://miniapp.zaloplatforms.com/documents/zaui/container/grid/
