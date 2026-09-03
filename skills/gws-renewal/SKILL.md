---
name: gws-renewal
description: Run the Google Workspace reseller line as a standalone product line - protect recurring revenue with a renewal cadence, track seats and renewal rate, and keep the boundary with other product lines. Use for Google Workspace renewals, expiry reminders at T-90/60/30/14/7, migration deals, seat and gross-profit tracking, renewal-rate KPIs, and deciding whether the line is still worth running.
---

# Google Workspace — mảng sản phẩm độc lập

> **Quy tắc gốc:** đây là **một mảng sản phẩm riêng**, không phải phễu của MineFlow,
> không phải bậc thang dẫn vào MineFlow. Doanh thu, chi phí, giờ Henry và KPI ghi nhận **riêng**.

Vai trò trong OCP: **Cash Engine** — tạo tiền ngắn hạn, chu kỳ bán ngắn, ít tốn giờ Founder.
Không cố biến nó thành mảng "chiến lược". Giá trị của nó là **tiền đều và ít tốn thời gian**.

## Vì sao việc gia hạn quan trọng hơn việc tìm khách mới

Doanh thu gia hạn là **doanh thu chắc chắn nhất trong toàn bộ danh mục**:
khách đã dùng, đã tin, đã có ngân sách. Chi phí giữ gần bằng 0.

Nhưng nó cũng là doanh thu **dễ mất nhất một cách âm thầm**: khách không báo là sẽ rời,
họ chỉ đơn giản không gia hạn — và thường vì không ai nhắc đúng lúc.

Vì vậy việc đáng tự động hoá đầu tiên trong toàn bộ danh mục không phải marketing.
Là **lịch nhắc gia hạn**.

## Quick Start

```bash
# Ai tới hạn cần chạm hôm nay?
python3 scripts/renewal_check.py --list renewal-tracker.csv

# Ghi nhận đã chạm xong
python3 scripts/renewal_check.py --list renewal-tracker.csv --done c001 c002

# Khách đã gia hạn -> dời hạn sang năm sau
python3 scripts/renewal_check.py --list renewal-tracker.csv --renewed c001

# Toàn cảnh: doanh thu năm, số seat, tỉ lệ gia hạn, khách sắp mất
python3 scripts/renewal_check.py --list renewal-tracker.csv --report
```

Copy `assets/renewal-tracker.example.csv` làm điểm bắt đầu. Mở bằng Excel hay Google Sheets đều được.

## Nhịp chạm — sáu mốc

| Mốc | Việc | Kênh |
|---|---|---|
| **T-90** | Kiểm tra số user thực tế so với số seat đang trả | Nội bộ |
| **T-60** | Nhắn thăm hỏi, báo trước ngày hết hạn | Zalo |
| **T-30** | Gửi báo giá gia hạn kèm hoá đơn mẫu | Email |
| **T-14** | Gọi xác nhận | Điện thoại |
| **T-7** | Nhắc cuối, nêu rõ rủi ro gián đoạn dịch vụ | Zalo |
| **T+1** | Xác nhận đã gia hạn, hỏi có cần thêm seat không | Zalo |

Script tự tính mốc từ `expiry_date` và chỉ in ra người tới hạn hôm nay.

## References

- [product-line.md](./references/product-line.md) — bản chất mảng, hai motion renewal/migration,
  ICP riêng, offer, bảng kênh, KPI, **ranh giới với MineFlow**, rủi ro, điều kiện giữ hay bỏ

## Nguyên tắc bắt buộc

- **Không gộp mảng.** Doanh thu, chi phí, giờ và KPI ghi riêng. Không lấy số khách Workspace
  làm KPI tăng trưởng của mảng khác.
- **Không chào bán sản phẩm khác trong cuộc gọi gia hạn**, trừ khi khách tự nêu vấn đề.
  Biến cuộc chăm sóc thành cuộc bán hàng làm hỏng tỉ lệ gia hạn — thứ duy nhất mảng này sống bằng.
- **Cạnh tranh bằng quy trình, không bằng giá.** Ai cũng bán được cùng một gói Google.
  Khác biệt là hoá đơn đúng, hỗ trợ tiếng Việt, và không để khách quên ngày hết hạn.
- **Tỉ lệ gia hạn dưới 85% là báo động.** Sửa nhịp chạm trước khi đi tìm khách mới.
- `renewal-tracker.csv` chứa thông tin khách hàng — **không commit**, đã nằm trong `.gitignore`.
