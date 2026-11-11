# messages/

Nội dung 5 chạm outreach. Mỗi file ứng với một stage trong `prospect-list.csv`.

| File | Stage sinh ra | Chạm |
|---|---|---|
| `connect.txt` | `connect_sent` | 1 — connection note, **≤ 300 ký tự** (LinkedIn cắt cứng) |
| `thanks.txt` | `thanks_sent` | 2 — cảm ơn + câu hỏi discovery |
| `value.txt` | `value_sent` | 3 — cho đi giá trị, không bán |
| `offer.txt` | `offer_sent` | 4 — đề xuất buổi trải nghiệm |
| `followup.txt` | `followed_up` | 5 — chốt hoặc đóng lịch sự |

Biến được script điền tự động: `{ten}`, `{shop}`, `{san}`, `{nganh}`.
Biến thiếu dữ liệu hiện thành `[ten?]` để Henry thấy ngay mà điền tay.

Sửa nội dung ở đây, không sửa trong script.
**Luôn thêm ít nhất một câu riêng cho từng người trước khi gửi.**
