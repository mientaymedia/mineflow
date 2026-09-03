# Image Playbook — Ảnh cho bài LinkedIn

Ảnh không phải để đẹp. Ảnh để **giữ người đọc lại thêm 2 giây** và **giải thích một ý duy nhất**.

## 1. Kích thước và định dạng

| Loại | Kích thước | Tỉ lệ | Ghi chú |
|---|---|---|---|
| Ảnh đơn trong feed | **1200 × 1200 px** | 1:1 | Chiếm nhiều diện tích nhất trên mobile — mặc định dùng cái này |
| Ảnh ngang | 1200 × 627 px | 1.91:1 | Dùng khi cần khoe dashboard rộng |
| Ảnh dọc | 1080 × 1350 px | 4:5 | Dùng cho danh sách dài |
| Multi-image | 1200 × 1200 px | 1:1 | 2–9 ảnh, LinkedIn ghép lưới |
| Carousel PDF | 1080 × 1350 px/trang | 4:5 | Documents API, reach đã bị bóp — cân nhắc |

Ràng buộc kỹ thuật của Images API:
- Định dạng: **JPG, PNG, GIF** (GIF không animate trong feed)
- Dung lượng tối đa: **~10 MB**
- Tối đa **9 ảnh** cho một bài multi-image
- Luôn điền `altText` — vừa cho accessibility, vừa cho SEO nội bộ LinkedIn

## 2. Sáu mẫu visual

Dùng đúng 6 mẫu này. Nhất quán quan trọng hơn đa dạng — sau 20 bài, người đọc nhận ra ảnh của bạn không cần nhìn tên.

| # | Mẫu | Dùng cho pillar | Nội dung |
|---|---|---|---|
| V1 | **Big Number** | P1 Problem | 1 con số khổng lồ + 1 dòng chú thích. Ví dụ: "41.000 khách / 0 người remarketing được" |
| V2 | **Before → After** | P2 Proof | 2 cột, mũi tên ở giữa, 3 chỉ số mỗi cột |
| V3 | **Checklist** | P3 How-to | 5–7 dòng có ô tick. Không quá 7 dòng |
| V4 | **Sơ đồ luồng** | P3 How-to | 3–5 hộp nối bằng mũi tên. Ví dụ: POS + Shopee + Zalo → MineFlow → ZNS |
| V5 | **Screenshot có chú thích** | P3 Demo | Ảnh màn hình thật + 1–2 mũi tên đỏ + chú thích ngắn. **Bắt buộc làm mờ dữ liệu khách** |
| V6 | **Quote card** | P4 POV | 1 câu ≤ 15 từ, chữ lớn, nền đơn sắc |

## 3. Quy tắc chữ trên ảnh

- **Tối đa 15 từ** trên toàn ảnh (trừ V3 checklist và V5 screenshot).
- Cỡ chữ tiêu đề ≥ **60px** ở khung 1200px — phải đọc được trên màn hình điện thoại thu nhỏ.
- Tương phản tối thiểu **4.5:1** giữa chữ và nền.
- Lề an toàn **80px** mỗi cạnh.
- **Một** ý mỗi ảnh. Ảnh cần giải thích thêm là ảnh hỏng.

## 4. Bộ nhận diện (đặt một lần, dùng mãi)

```
Nền chính     #0B1F3B   (xanh navy đậm)
Nền phụ       #F5F7FA   (xám rất nhạt)
Nhấn          #2F6FED   (xanh dương)
Cảnh báo      #E5484D   (đỏ - chỉ dùng cho số liệu xấu)
Chữ trên tối  #FFFFFF
Chữ trên sáng #0B1F3B
Font          Inter hoặc Be Vietnam Pro (có dấu tiếng Việt đầy đủ)
```

**Kiểm tra font tiếng Việt:** gõ thử "Nguyễn Thị Hưởng — 41.000 đơn/tháng". Nếu dấu bị vỡ hoặc lệch, đổi font.
Rất nhiều font display quốc tế không có glyph tiếng Việt.

## 5. Quy trình làm ảnh (30 phút / 3 ảnh)

1. Viết bài trước. Rút ra **một** câu hoặc **một** con số đắt nhất.
2. Chọn mẫu V1–V6 theo pillar.
3. Dựng ảnh — chọn một trong ba cách:
   - **Canva** (nhanh nhất): tạo 6 template một lần, sau đó chỉ thay chữ.
   - **AI tạo ảnh**: chỉ dùng cho ảnh nền/minh hoạ trừu tượng. **Không dùng AI để tạo biểu đồ hay số liệu** — AI viết sai số và sai chính tả tiếng Việt.
   - **Screenshot thật**: cho V5, luôn làm mờ dữ liệu khách hàng.
4. Xuất PNG, đặt tên `YYYY-MM-DD-slug.png`, lưu vào thư mục ảnh của hàng đợi.
5. Viết `alt_text` mô tả **nội dung thật** của ảnh, không nhét từ khoá.

## 6. Alt text — viết thế nào

| Sai | Đúng |
|---|---|
| "MineFlow CDP loyalty Zalo bán lẻ" | "Biểu đồ cột so sánh tỉ lệ khách quay lại trước 11% và sau 19%" |
| "ảnh bài viết" | "Sơ đồ dữ liệu từ POS, Shopee và Zalo OA gộp về một hồ sơ khách hàng" |

Giới hạn thực tế: giữ dưới 200 ký tự.

## 7. Chống nhàm — luân phiên

Trong 4 tuần, đừng dùng cùng một mẫu hai bài liên tiếp. Thứ tự gợi ý:

```
Tuần 1: V1 → V3 → V6
Tuần 2: V1 → V2 → V4
Tuần 3: V1 → V3 → V6
Tuần 4: V2 → V4 → V1
```

## 8. Sai lầm hay gặp

| Sai lầm | Hậu quả |
|---|---|
| Nhồi cả bài viết vào ảnh | Không ai đọc, reach giảm |
| Ảnh stock người cười bắt tay | Mất uy tín tức thì với người mua B2B |
| Logo to hơn nội dung | Trông như quảng cáo, tương tác giảm |
| Screenshot còn nguyên tên/SĐT khách | **Rủi ro pháp lý về dữ liệu cá nhân** |
| Chữ dưới 40px | Không đọc được trên mobile — 80% người xem dùng mobile |
| Số liệu bịa để ảnh "đẹp" | Mất khách khi họ hỏi lại trong discovery call |
