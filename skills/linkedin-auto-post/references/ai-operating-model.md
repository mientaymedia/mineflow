# AI Operating Model — AI làm gì, Henry làm gì

> Bối cảnh Henry chốt 2026-09-03: AI viết nội dung và script đăng bài, Henry chỉ duyệt.
> Đúng — nhưng ràng buộc thời gian **chuyển chỗ**, không biến mất. Tài liệu này chỉ ra chỗ mới.

## 1. Phân vai — ai làm được việc gì

| Việc | AI | Script | Henry | Ghi chú |
|---|:--:|:--:|:--:|---|
| Viết nháp bài theo template | ✅ 100% | | | Cần nguyên liệu ở mục 2 |
| Sinh hook, biến thể tiêu đề | ✅ 100% | | | |
| Soạn tin nhắn outreach điền biến | | ✅ 100% | | `outreach_queue.py` |
| Dựng ảnh từ template Canva | ✅ 80% | | 20% | AI hay sai số liệu và dấu tiếng Việt — phải soát |
| Nạp hàng đợi, đăng bài đúng giờ | | ✅ 100% | | `run_queue.py` + cron |
| **Cung cấp nguyên liệu thật** | ❌ | ❌ | ✅ **100%** | **Ràng buộc mới số 1** |
| **Duyệt trước khi đăng** | ❌ | ❌ | ✅ 100% | Mục 3 |
| **Bấm gửi connection request** | ❌ | ❌ | ✅ 100% | LinkedIn không có API. Tự động = khoá tài khoản |
| **Trả lời comment và inbox** | ❌ | ❌ | ✅ 100% | **Ràng buộc mới số 2** — đây là nơi deal xảy ra |
| Discovery call, buổi dựng thử 45 phút | ❌ | ❌ | ✅ 100% | |
| Chốt deal, báo giá, hợp đồng | ❌ | ❌ | ✅ 100% | |

**Kết luận đọc từ bảng:** AI xoá gần hết cột "sản xuất". Nó không chạm được vào cột "nguyên liệu"
và cột "quan hệ" — mà đó mới là chỗ tạo ra tiền.

## 2. Ràng buộc số 1 — nguyên liệu thật

AI không biết tuần vừa rồi Henry gặp ai, khách nói gì, con số nào thay đổi.
Không có nguyên liệu, AI viết được bài **đúng ngữ pháp nhưng chung chung** — loại bài không ai phản hồi.

Đây là thứ quyết định LinkedIn thành hay bại, và **không thể giao cho AI**.

### Weekly Input Brief — 15 phút, chủ nhật

Henry trả lời 8 câu này bằng gạch đầu dòng, không cần viết hay. AI biến nó thành 3 bài.

```
1. Tuần này nói chuyện với những ai? Họ than phiền điều gì? (chép nguyên văn nếu nhớ)
2. Câu hỏi nào khách hỏi mà mình phải suy nghĩ mới trả lời được?
3. Con số nào thay đổi tuần này? (doanh thu, số khách, số seat, tỉ lệ nào đó)
4. Mình làm sai chuyện gì? Học được gì?
5. Thấy gì trên thị trường mà thấy sai/kỳ lạ?
6. Có ai từ chối mình không? Lý do họ nêu là gì?
7. Có kết quả nào của khách hàng đáng kể không? (kèm: đã xin phép chia sẻ chưa)
8. Tuần tới muốn ai đọc được bài của mình nhất?
```

**Quy tắc cứng:** không có brief → **không đăng bài tuần đó**. Đăng bài chung chung tệ hơn không đăng:
nó đốt reach và dạy thuật toán rằng nội dung của Henry không đáng phân phối.

## 3. Ràng buộc số 2 — chất lượng duyệt

"Chỉ duyệt" nghe nhẹ, nhưng duyệt hời hợt trong 4 tuần sẽ biến thành đóng dấu tự động.
Khi đó Henry đang tự động hoá việc đăng nội dung mà chính mình không đứng sau.

### Checklist duyệt 60 giây/bài — 5 thứ AI hay sai

| # | Kiểm tra | Vì sao |
|---|---|---|
| 1 | **Mọi con số có nguồn thật không?** | AI bịa số rất trôi chảy. Số sai → mất khách ở buổi discovery |
| 2 | **Ví dụ có phải chuyện thật của Henry không?** | Ví dụ bịa nghe hay nhưng rỗng, và không chịu nổi một câu hỏi ngược |
| 3 | **Có lộ tên/SĐT/dữ liệu khách hàng không?** | Rủi ro pháp lý về dữ liệu cá nhân, và mất niềm tin của khách hiện tại |
| 4 | **Đọc lên có giống giọng Henry không?** | Người mua B2B nhận ra giọng AI. Reach có thể tốt, niềm tin thì không |
| 5 | **Bài này phục vụ mệnh đề nào?** | Không thuộc mệnh đề nào ở content-strategy mục 2 → bỏ, không sửa |

Trượt bất kỳ mục nào → trả lại AI viết lại, **không sửa vá rồi đăng**.

Trong hàng đợi CSV, đây chính là ý nghĩa của cột `status`: bài AI viết ra để `draft`.
Chỉ Henry đổi sang `ready`. Không có đường nào khác để bài lên feed.

## 4. Thời gian thật của Henry sau khi AI làm hết phần sản xuất

| Việc | Ai làm | Henry (phút/tuần) |
|---|---|---:|
| Weekly Input Brief | Henry | 15 |
| Duyệt 3 bài × 60 giây + 1 lần sửa | Henry | 15 |
| Soát ảnh (số liệu, dấu tiếng Việt) | Henry | 10 |
| Viết bài, làm ảnh, nạp queue, đăng | **AI + script** | **0** |
| Soạn tin nhắn outreach | **Script** | **0** |
| **Bấm gửi outreach 15 request/ngày × 5** | Henry | **100** |
| **Trả lời comment 2h đầu + inbox** | Henry | **60** |
| Chốt số KPI | Henry | 10 |
| | | **≈ 3,5 giờ/tuần** |

So với ước tính 6 giờ khi làm tay: **AI tiết kiệm ~2,5 giờ/tuần**. Đáng kể, nhưng không về 0.

**160 trong 210 phút còn lại nằm ở hai việc AI không chạm được:** bấm gửi outreach và trả lời người thật.

### Và con số này tăng khi kênh chạy tốt

| Mức độ thành công | Buổi dựng thử/tháng | Giờ Henry/tháng thêm |
|---|---:|---:|
| Chưa có lead | 0 | 0 |
| Đạt mục tiêu tháng 1 | 3 | ~5 |
| Đạt mục tiêu tháng 3 | 10 | ~17 |

Mỗi buổi dựng thử = 45 phút gọi + ~30 phút chuẩn bị dữ liệu mẫu + ~25 phút follow-up.

**Thành công của kênh này tạo thêm việc cho Henry, không giảm.** Đó là loại "vấn đề" nên có —
nhưng phải biết trước để không nhận nhiều buổi hơn khả năng làm tốt.

## 5. Vì thời gian sản xuất rẻ đi — nên tiêu vào đâu?

Sai lầm dễ mắc: sản xuất rẻ nên **tăng tần suất bài**.

**Không tăng.** Ba lý do:

1. Chưa có dữ liệu bài nào tạo phản hồi. Tăng tần suất lúc này chỉ nhân bản sai lầm nhanh hơn.
2. Nút thắt nằm ở nguyên liệu (mục 2), không ở khả năng viết. 5 bài/tuần từ một brief 15 phút
   sẽ loãng hơn 3 bài/tuần từ cùng brief đó.
3. Đăng nhiều mà tương tác thấp làm giảm reach của mọi bài sau.

Thời gian tiết kiệm được nên dồn theo thứ tự:

| Ưu tiên | Dồn vào | Vì sao |
|---:|---|---|
| 1 | **Trả lời comment và inbox trong 2 giờ đầu** | Đây là nơi hội thoại thành deal. Trả lời chậm = mất |
| 2 | **Outreach** — giữ đủ 15 request/ngày, không bỏ ngày nào | Kênh tạo pipeline trực tiếp |
| 3 | **Chất lượng nguyên liệu** — brief dài hơn, cụ thể hơn | Nâng trần chất lượng của mọi bài |
| 4 | Tăng tần suất bài | **Chỉ sau 4 tuần có dữ liệu** hook nào chạy |

## 6. Điều kiện xem lại

Sau 4 tuần, xem hai chỉ số:

| Nếu | Nghĩa là | Làm gì |
|---|---|---|
| Bài đăng đủ nhưng ~0 comment thật | Nội dung chung chung — thiếu nguyên liệu | Brief sâu hơn. **Không** tăng tần suất |
| Có comment nhưng ~0 hội thoại inbox | CTA sai hoặc trả lời chậm | Sửa CTA, ưu tiên trả lời trong 2h |
| Có hội thoại nhưng ~0 buổi dựng thử | Lời mời chưa đủ cụ thể | Sửa chạm 4 ở outreach-playbook mục 3 |
| Có buổi dựng thử nhưng ~0 chốt | Vấn đề ở offer hoặc giá | Không phải vấn đề của LinkedIn. Xem lại offer |

Mỗi dòng chỉ về một chỗ khác nhau. Đừng sửa cả bốn cùng lúc.
