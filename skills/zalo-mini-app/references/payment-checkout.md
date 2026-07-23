# Payment / Checkout Integration

Official docs: https://miniapp.zaloplatforms.com/documents/payment/

Zalo Mini App payment requires both frontend SDK integration and backend/order management. Never trust frontend-only payment state.

## Main Docs Areas

- Integration settings: merchant registration and payment method setup
- Payment methods: bank, ZaloPay, MoMo, VNPay, PayME, COD, custom methods
- Create order
- Receive callback / notification
- Check transaction / order status
- Update order status
- Refund / refund status

## Recommended Architecture

```text
Mini App frontend
  -> backend: create pending order
  -> Zalo/payment createOrder
  -> user pays in Zalo/payment UI
  -> payment callback/notify to backend
  -> backend verifies signature and updates order
  -> frontend polls or refreshes order status
```

## Create Order

Backend should create an internal order first, then call Zalo/payment API.

```ts
// frontend example
const res = await fetch("/api/orders", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ cartId })
});
const order = await res.json();
```

Backend responsibilities:

- Validate cart/product/pricing on server.
- Generate idempotency key/order code.
- Call payment create order API with signed request.
- Store pending state.
- Return only safe data to frontend.

Docs: https://miniapp.zaloplatforms.com/documents/payment/createOrder/

## Callback / Notify

Payment completion should be confirmed by backend callback/notification, not by client redirect alone.

Backend checklist:

- Verify signature.
- Verify amount/currency/order id.
- Idempotently transition order state.
- Log provider transaction id.
- Return required response format to provider.

Docs:

- https://miniapp.zaloplatforms.com/documents/payment/callback/
- https://miniapp.zaloplatforms.com/documents/payment/notify/

## Check Status

Use status check APIs to reconcile uncertain states.

- `checkTransaction`
- `getOrderStatus`
- `updateOrderStatus`

Docs:

- https://miniapp.zaloplatforms.com/documents/payment/checkTransaction/
- https://miniapp.zaloplatforms.com/documents/payment/getOrderStatus/

## Refund

Refunds should be initiated by backend/admin workflow.

- `createRefund`
- `getRefundStatus`

Docs:

- https://miniapp.zaloplatforms.com/documents/payment/createRefund/
- https://miniapp.zaloplatforms.com/documents/payment/getRefundStatus/

## Security Rules

- Keep secrets server-side only.
- Verify all callbacks/signatures.
- Use idempotent order transitions.
- Do not trust frontend amount/status.
- Store full audit trail for payment state changes.
- Reconcile periodically for `pending`/`unknown` states.
