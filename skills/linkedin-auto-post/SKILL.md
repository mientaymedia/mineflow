---
name: linkedin-auto-post
description: Build and auto-publish LinkedIn content (text + images) to promote a B2B SaaS product. Use for LinkedIn content strategy, ICP-driven post templates, hook writing, image/carousel specs, LinkedIn Posts API and Images API integration, OAuth token setup, a CSV publishing queue, cron/GitHub Actions scheduling, and pipeline KPIs. Default product context: MineFlow CDP + Loyalty on Zalo for Vietnamese retail and e-commerce SMBs.
---

# LinkedIn Content & Auto-Posting

Hệ thống hai lớp:

1. **Content layer** — biến sản phẩm thành nội dung LinkedIn tạo pipeline, không phải vanity metrics.
2. **Automation layer** — hàng đợi CSV + script Python (stdlib, không dependency) đẩy bài kèm ảnh lên LinkedIn theo lịch.

Baseline API: LinkedIn Versioned API, `LinkedIn-Version: 202604`, kiểm tra ngày 2026-09-03.

## Nguyên tắc bắt buộc

- Mỗi bài phải phục vụ **một ICP**, **một vấn đề**, **một hành động tiếp theo**. Không đăng cho vui.
- KPI chính là **profile view → connection request có phản hồi → discovery call**, không phải like/impression.
- Không tự động hoá khi chưa có 10 bài viết tay đã kiểm chứng. Automation nhân bản kết quả, không tạo ra kết quả.
- Không bao giờ commit access token. Token đọc từ biến môi trường `LINKEDIN_ACCESS_TOKEN`.

## Quy trình chuẩn

```
Chọn ICP + offer  →  references/content-strategy.md
      ↓
Viết bài theo template  →  references/post-templates.md
      ↓
Làm ảnh  →  references/image-playbook.md
      ↓
Nạp vào hàng đợi  →  assets/content-queue.example.csv
      ↓
Chạy tự động  →  scripts/run_queue.py  (cron / GitHub Actions)
      ↓
Đo KPI hằng tuần  →  references/automation-runbook.md
```

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
```

## References

### Nội dung
- [content-strategy.md](./references/content-strategy.md) — ICP, positioning, 5 content pillar, hook bank, lịch 30 ngày, KPI
- [post-templates.md](./references/post-templates.md) — 12 template bài viết tiếng Việt kèm ví dụ đã điền cho MineFlow
- [image-playbook.md](./references/image-playbook.md) — kích thước ảnh, 6 mẫu visual, quy tắc chữ trên ảnh, carousel PDF

### Kỹ thuật
- [linkedin-api.md](./references/linkedin-api.md) — OAuth scope, lấy author URN, Images API, Posts API, escaping, lỗi thường gặp
- [automation-runbook.md](./references/automation-runbook.md) — schema hàng đợi CSV, cron, GitHub Actions, rate limit, guardrail, dashboard KPI

### Scripts
- [linkedin_post.py](./scripts/linkedin_post.py) — đăng 1 bài: text, 1 ảnh, hoặc nhiều ảnh
- [run_queue.py](./scripts/run_queue.py) — đọc CSV, đăng bài tới hạn, ghi ngược kết quả

## Giới hạn cần biết trước khi bắt đầu

| Việc | Điều kiện |
|---|---|
| Đăng lên **profile cá nhân** | Scope `w_member_social` — LinkedIn Developer app tự duyệt được |
| Đăng lên **Company Page** | Scope `w_organization_social` — cần Community Management API, phải nộp đơn duyệt, thường vài tuần |
| Đăng ảnh | Phải qua Images API 2 bước, không có upload 1 lần |
| Carousel (PDF) | Dùng Documents API, LinkedIn đã hạn chế reach — ưu tiên ảnh đơn hoặc multi-image |

Nếu chưa được duyệt Company Page, **bắt đầu bằng profile cá nhân của founder**. Với B2B SaaS giai đoạn đầu, founder profile luôn có reach tốt hơn page mới.
