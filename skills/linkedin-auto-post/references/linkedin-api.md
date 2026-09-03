# LinkedIn API — Đăng bài kèm ảnh

Baseline: LinkedIn Versioned API, header `LinkedIn-Version: 202604`, kiểm tra 2026-09-03.
LinkedIn phát hành version mới hằng tháng (YYYYMM) và giữ mỗi version khoảng 1 năm.
Nếu gặp lỗi `426 Upgrade Required`, đổi sang version mới hơn.

## 1. Tạo app và xin quyền

1. Vào <https://developer.linkedin.com/> → **Create app**. Bắt buộc gắn với một LinkedIn Page bạn là admin.
2. Tab **Products**, request:

| Product | Cho phép | Duyệt |
|---|---|---|
| **Sign In with LinkedIn using OpenID Connect** | scope `openid`, `profile`, `email` — dùng để lấy person URN | Tự động |
| **Share on LinkedIn** | scope `w_member_social` — **đăng lên profile cá nhân** | Tự động |
| **Community Management API** | scope `w_organization_social`, `r_organization_social` — **đăng lên Company Page** | Phải nộp đơn, thường vài tuần |

> **Quyết định thực tế:** bắt đầu với profile cá nhân (`w_member_social`). Nộp đơn Community Management API
> song song, nhưng đừng chờ nó mới bắt đầu đăng.

3. Tab **Auth** → thêm **Authorized redirect URL**: `http://localhost:8000/callback`.

## 2. Lấy access token (3-legged OAuth)

### Cách nhanh — dùng `scripts/get_token.py`

Chạy **trên máy cá nhân** (script cần mở được trình duyệt để đăng nhập LinkedIn):

```bash
python3 scripts/get_token.py \
  --client-id XXX --client-secret YYY --env-file .env
```

Script tự làm hết: mở trình duyệt, dựng server hứng callback, kiểm tra `state` chống CSRF,
đổi code lấy token, gọi `/v2/userinfo` lấy luôn author URN, ghi `.env` với quyền `600`,
và cảnh báo nếu thiếu scope `w_member_social`. Henry chỉ bấm **Allow** một lần.

Token **không in ra màn hình** để tránh lọt vào lịch sử terminal.

> **Không chạy script này trên máy chủ dùng chung hoặc trong session Claude Code.**
> Nó tạo ra thông tin đăng nhập cho phép đăng bài dưới danh nghĩa của bạn.

### Cách thủ công — khi muốn hiểu từng bước

**Bước 1 — mở URL này trên trình duyệt, đăng nhập, đồng ý:**

```
https://www.linkedin.com/oauth/v2/authorization
  ?response_type=code
  &client_id={CLIENT_ID}
  &redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fcallback
  &state=random123
  &scope=openid%20profile%20email%20w_member_social
```

Trình duyệt bị redirect về `http://localhost:8000/callback?code=AQT...&state=random123`.
Copy giá trị `code` (hết hạn sau 30 giây — làm bước 2 ngay).

**Bước 2 — đổi code lấy token:**

```bash
curl -X POST 'https://www.linkedin.com/oauth/v2/accessToken' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=authorization_code' \
  -d 'code=AQT...' \
  -d 'client_id={CLIENT_ID}' \
  -d 'client_secret={CLIENT_SECRET}' \
  -d 'redirect_uri=http://localhost:8000/callback'
```

Trả về:
```json
{
  "access_token": "AQV...",
  "expires_in": 5184000,
  "refresh_token": "AQW...",
  "refresh_token_expires_in": 31536000,
  "scope": "openid,profile,email,w_member_social"
}
```

- Access token sống **60 ngày**. Refresh token sống **365 ngày** (chỉ cấp cho app đã được duyệt refresh).
- Lưu token vào biến môi trường hoặc secret manager. **Không commit vào git.**

**Refresh token:**
```bash
curl -X POST 'https://www.linkedin.com/oauth/v2/accessToken' \
  -d 'grant_type=refresh_token' \
  -d 'refresh_token=AQW...' \
  -d 'client_id={CLIENT_ID}' \
  -d 'client_secret={CLIENT_SECRET}'
```

Nếu app chưa được cấp refresh token, phải làm lại bước 1–2 mỗi 60 ngày. Đặt lịch nhắc.

## 3. Lấy author URN

**Profile cá nhân** — dùng OpenID userinfo:

```bash
curl 'https://api.linkedin.com/v2/userinfo' \
  -H 'Authorization: Bearer {TOKEN}'
```

```json
{ "sub": "abc123XYZ", "name": "Henry", "email": "..." }
```

→ Author URN là `urn:li:person:abc123XYZ`

**Company Page** (cần `r_organization_social`):

```bash
curl 'https://api.linkedin.com/rest/organizationAcls?q=roleAssignee&role=ADMINISTRATOR&state=APPROVED' \
  -H 'Authorization: Bearer {TOKEN}' \
  -H 'LinkedIn-Version: 202604' \
  -H 'X-Restli-Protocol-Version: 2.0.0'
```

→ Author URN là `urn:li:organization:{id}`

## 4. Headers dùng cho MỌI request `/rest/*`

```
Authorization: Bearer {ACCESS_TOKEN}
LinkedIn-Version: 202604
X-Restli-Protocol-Version: 2.0.0
Content-Type: application/json
```

Thiếu `LinkedIn-Version` → **426 Upgrade Required**. Đây là lỗi phổ biến nhất.

## 5. Đăng bài chỉ có text

```bash
curl -X POST 'https://api.linkedin.com/rest/posts' \
  -H 'Authorization: Bearer {TOKEN}' \
  -H 'LinkedIn-Version: 202604' \
  -H 'X-Restli-Protocol-Version: 2.0.0' \
  -H 'Content-Type: application/json' \
  -d '{
    "author": "urn:li:person:abc123XYZ",
    "commentary": "Nội dung bài viết ở đây.",
    "visibility": "PUBLIC",
    "distribution": {
      "feedDistribution": "MAIN_FEED",
      "targetEntities": [],
      "thirdPartyDistributionChannels": []
    },
    "lifecycleState": "PUBLISHED",
    "isReshareDisabledByAuthor": false
  }'
```

Thành công: **HTTP 201**, URN bài viết nằm ở response header `x-restli-id`
(ví dụ `urn:li:share:7123456789`). Body rỗng.

## 6. Đăng bài kèm ảnh — 3 bước bắt buộc

Images API **không có** upload một lần (`SYNCHRONOUS_UPLOAD` không được hỗ trợ).

### Bước 1 — initializeUpload

```bash
curl -X POST 'https://api.linkedin.com/rest/images?action=initializeUpload' \
  -H 'Authorization: Bearer {TOKEN}' \
  -H 'LinkedIn-Version: 202604' \
  -H 'X-Restli-Protocol-Version: 2.0.0' \
  -H 'Content-Type: application/json' \
  -d '{ "initializeUploadRequest": { "owner": "urn:li:person:abc123XYZ" } }'
```

```json
{
  "value": {
    "uploadUrlExpiresAt": 1757000000000,
    "uploadUrl": "https://www.linkedin.com/dms-uploads/...",
    "image": "urn:li:image:C4E10AQ..."
  }
}
```

> `uploadUrlExpiresAt` là thật. Đăng ký rồi để một tiếng sau mới upload sẽ hỏng.
> **Initialize và upload phải nằm trong cùng một lần chạy.**

### Bước 2 — PUT binary lên uploadUrl

```bash
curl -X PUT '{uploadUrl}' \
  -H 'Authorization: Bearer {TOKEN}' \
  --data-binary @anh.png
```

Thành công: **200** hoặc **201**, body rỗng. Không cần đặt `Content-Type` chính xác.

### Bước 3 — tạo post tham chiếu image URN

```json
{
  "author": "urn:li:person:abc123XYZ",
  "commentary": "Nội dung bài viết.",
  "visibility": "PUBLIC",
  "distribution": {
    "feedDistribution": "MAIN_FEED",
    "targetEntities": [],
    "thirdPartyDistributionChannels": []
  },
  "content": {
    "media": {
      "id": "urn:li:image:C4E10AQ...",
      "altText": "Biểu đồ tỉ lệ khách quay lại tăng từ 11% lên 19%"
    }
  },
  "lifecycleState": "PUBLISHED",
  "isReshareDisabledByAuthor": false
}
```

**Nhiều ảnh (2–9):** thay `content.media` bằng:

```json
"content": {
  "multiImage": {
    "images": [
      { "id": "urn:li:image:AAA", "altText": "Ảnh 1" },
      { "id": "urn:li:image:BBB", "altText": "Ảnh 2" }
    ]
  }
}
```

## 7. Escaping trong `commentary` — GOTCHA quan trọng

Trường `commentary` dùng định dạng "little text" của LinkedIn. Các ký tự sau **phải escape bằng `\`**:

```
( ) [ ] { } < > @ | ~ _ * #
```

Ví dụ: `Doanh thu tăng 30% (so với tháng trước)` phải gửi thành
`Doanh thu tăng 30% \\(so với tháng trước\\)`.

Không escape → lỗi `422` hoặc bài hiển thị sai định dạng.
Script `linkedin_post.py` trong skill này đã tự xử lý việc này.

Ngoại lệ: hashtag `#CDP` cần giữ nguyên `#` để LinkedIn nhận là hashtag.
Script giữ nguyên `#` khi ký tự đứng ngay sau là chữ hoặc số.

## 8. Xoá bài

```bash
curl -X DELETE 'https://api.linkedin.com/rest/posts/urn%3Ali%3Ashare%3A7123456789' \
  -H 'Authorization: Bearer {TOKEN}' \
  -H 'LinkedIn-Version: 202604' \
  -H 'X-Restli-Protocol-Version: 2.0.0'
```

URN phải được URL-encode.

## 9. Lỗi thường gặp

| Mã | Nguyên nhân | Xử lý |
|---|---|---|
| **401** | Token hết hạn (60 ngày) hoặc sai | Refresh token, hoặc làm lại OAuth |
| **403** | Thiếu scope, hoặc đăng lên org mà không phải admin | Kiểm tra scope trong response OAuth |
| **422** | `commentary` chưa escape, hoặc thiếu field bắt buộc | Xem mục 7; kiểm tra `distribution` và `lifecycleState` |
| **426** | Thiếu/sai header `LinkedIn-Version` | Thêm header, dùng version YYYYMM còn hiệu lực |
| **429** | Vượt rate limit | Backoff; giới hạn thực tế thoải mái hơn nhiều so với 3 bài/tuần |
| **400** ở bước PUT ảnh | `uploadUrl` đã hết hạn | Gọi lại `initializeUpload` |

## 10. Rate limit

Giới hạn chính thức thay đổi theo tier. Ở mức 3 bài/tuần, không có nguy cơ chạm trần.
Nguyên tắc an toàn:
- Tối đa **1 bài / lần chạy queue**
- Nghỉ **≥ 2 giây** giữa các request
- Không tự động comment, không tự động gửi connection request — đây là hành vi LinkedIn chủ động phát hiện và khoá tài khoản

## Nguồn

- [Images API — Microsoft Learn](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api)
- [Posts API — Microsoft Learn](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)
- [LinkedIn Posting API integration guide — Blotato](https://www.blotato.com/blog/linkedin-posting-api)
- [Automate Company Page posts — Postproxy](https://postproxy.dev/blog/linkedin-api-automate-company-page-publishing/)
