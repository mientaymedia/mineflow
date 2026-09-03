---
name: linkedin-auto-post
description: Build and auto-publish LinkedIn content (text + images) and run a safe, human-in-the-loop outreach cadence to promote a B2B product. Use for LinkedIn content strategy, ICP-driven post templates, hook writing, image specs, LinkedIn Posts API and Images API integration, OAuth token setup, a CSV publishing queue, cron/GitHub Actions scheduling, connection-request and DM sequences to prospects, prospect pipeline tracking, and pipeline KPIs. Product context: MineFlow CDP, Google Workspace and Zalo Business Solutions sold to Vietnamese shop owners selling on marketplaces; posts go to Henry's personal profile.
---

# LinkedIn Content & Auto-Posting

Hệ thống ba lớp:

1. **Content layer** — biến sản phẩm thành nội dung LinkedIn tạo pipeline, không phải vanity metrics.
2. **Publish layer** — hàng đợi CSV + script Python (stdlib, không dependency) đẩy bài kèm ảnh lên LinkedIn theo lịch.
3. **Outreach layer** — kết nối liên tục với chủ shop bán sàn theo chuỗi 5 chạm, có hạn mức an toàn, **người thật bấm gửi**.

Bối cảnh đã chốt với Henry (2026-09-03):
- Kênh đăng: **profile cá nhân Henry** (không dùng Company Page → chỉ cần scope `w_member_social`).
- Ba dòng sản phẩm: **MineFlow CDP**, **Google Workspace**, **Zalo Business Solutions** — bán theo bậc thang cho cùng một ICP.
- Khách hàng thật đang dùng: **Hậu Tâm Official** (một khách).

Baseline API: LinkedIn Versioned API, `LinkedIn-Version: 202604`, kiểm tra ngày 2026-09-03.

## Nguyên tắc bắt buộc

- Mỗi bài phải phục vụ **một ICP**, **một vấn đề**, **một hành động tiếp theo**. Không đăng cho vui.
- KPI chính là **profile view → connection request có phản hồi → discovery call**, không phải like/impression.
- Không tự động hoá khi chưa có 10 bài viết tay đã kiểm chứng. Automation nhân bản kết quả, không tạo ra kết quả.
- Không bao giờ commit access token. Token đọc từ biến môi trường `LINKEDIN_ACCESS_TOKEN`.
- **Chỉ tự động hoá việc đăng bài.** Connection request và tin nhắn do người thật bấm gửi — công cụ tự động gửi hàng loạt vi phạm điều khoản LinkedIn và thường bị khoá tài khoản vĩnh viễn.

## Quy trình chuẩn

```
Chọn ICP + bậc thang offer  →  references/content-strategy.md
      ↓
        ┌──────────────────────────┬──────────────────────────────┐
        │  LUỒNG NỘI DUNG          │  LUỒNG OUTREACH              │
        │  (tạo độ tin)            │  (tạo pipeline)              │
        ├──────────────────────────┼──────────────────────────────┤
        │ post-templates.md        │ outreach-playbook.md         │
        │ image-playbook.md        │ assets/prospect-list.csv     │
        │ content-queue.csv        │ assets/messages/*.txt        │
        │ scripts/run_queue.py     │ scripts/outreach_queue.py    │
        │ → cron tự đăng           │ → in việc, Henry bấm gửi     │
        └──────────────────────────┴──────────────────────────────┘
      ↓
Đo KPI hằng tuần  →  automation-runbook.md + outreach-playbook.md mục 7
```

Hai luồng nuôi nhau: bài viết là thứ gửi ở chạm 3 của outreach; người tương tác với bài
là nguồn prospect chất lượng nhất cho danh sách outreach.

## Quick Start

```bash
export LINKEDIN_ACCESS_TOKEN="..."          # xem references/linkedin-api.md để lấy token
export LINKEDIN_AUTHOR_URN="urn:li:person:xxxx"   # bỏ trống -> script tự lấy từ /v2/userinfo

# Đăng thử 1 bài kèm ảnh
python3 scripts/linkedin_post.py \
  --text-file drafts/post-001.txt \
  --image assets/img/post-001.png \
  --alt-text "Dashboard MineFlow hiển thị tỉ lệ khách quay lại" \
  --dry-run

# Bỏ --dry-run để đăng thật

# Chạy hàng đợi (chỉ đăng bài đã tới hạn, status=ready)
python3 scripts/run_queue.py --queue content-queue.csv

# Việc outreach hôm nay: ai cần gửi kết nối, tin nào tới hạn (script KHÔNG tự gửi)
python3 scripts/outreach_queue.py --list prospect-list.csv

# Gửi xong thì ghi nhận
python3 scripts/outreach_queue.py --list prospect-list.csv --done p001 p002
```

## References

### Nội dung
- [content-strategy.md](./references/content-strategy.md) — ICP, positioning, 5 content pillar, hook bank, lịch 30 ngày, KPI
- [post-templates.md](./references/post-templates.md) — 12 template bài viết tiếng Việt kèm ví dụ đã điền cho MineFlow
- [image-playbook.md](./references/image-playbook.md) — kích thước ảnh, 6 mẫu visual, quy tắc chữ trên ảnh, carousel PDF

### Outreach
- [outreach-playbook.md](./references/outreach-playbook.md) — tệp chủ shop bán sàn, cách tìm 30 người đầu, chuỗi 5 chạm, hạn mức an toàn, xử lý phản đối, KPI

### Kỹ thuật
- [linkedin-api.md](./references/linkedin-api.md) — OAuth scope, lấy author URN, Images API, Posts API, escaping, lỗi thường gặp
- [automation-runbook.md](./references/automation-runbook.md) — schema hàng đợi CSV, cron, GitHub Actions, rate limit, guardrail, dashboard KPI

### Scripts
- [linkedin_post.py](./scripts/linkedin_post.py) — đăng 1 bài: text, 1 ảnh, hoặc nhiều ảnh
- [run_queue.py](./scripts/run_queue.py) — đọc CSV, đăng bài tới hạn, ghi ngược kết quả
- [outreach_queue.py](./scripts/outreach_queue.py) — in việc outreach hôm nay kèm tin nhắn đã điền, theo dõi pipeline. **Không gửi gì lên LinkedIn**

## Giới hạn cần biết trước khi bắt đầu

| Việc | Điều kiện |
|---|---|
| Đăng lên **profile cá nhân** | Scope `w_member_social` — LinkedIn Developer app tự duyệt được |
| Đăng lên **Company Page** | Scope `w_organization_social` — cần Community Management API, phải nộp đơn duyệt, thường vài tuần |
| Đăng ảnh | Phải qua Images API 2 bước, không có upload 1 lần |
| Carousel (PDF) | Dùng Documents API, LinkedIn đã hạn chế reach — ưu tiên ảnh đơn hoặc multi-image |
| **Gửi connection request / tin nhắn** | **Không có API.** LinkedIn không mở API cho việc này với lý do chính đáng — mọi công cụ tự động đều vi phạm điều khoản |

Henry đã chốt dùng **profile cá nhân**, nên chỉ cần scope `w_member_social` — LinkedIn tự duyệt,
không phải chờ Community Management API. Đây cũng là lựa chọn đúng: với B2B giai đoạn đầu,
profile founder luôn có reach tốt hơn page mới.
