# Outreach Playbook — Kết nối liên tục với chủ shop bán sàn

Mục tiêu: mỗi tuần biến người lạ đúng tệp thành **cuộc trải nghiệm sản phẩm có lịch hẹn**.
Nội dung (bài đăng) tạo độ tin. Outreach mới tạo pipeline. Hai việc khác nhau, đều cần làm.

---

## 0. CẢNH BÁO BẮT BUỘC ĐỌC — vì sao không tự động hoá phần này

Henry muốn "liên tục kết nối". Đúng hướng. Nhưng **tuyệt đối không dùng công cụ tự động
gửi connection request hoặc tin nhắn hàng loạt** (Dux-Soup, PhantomBuster, LinkedHelper, Sales Navigator scraper...).

| Vấn đề | Hậu quả |
|---|---|
| Vi phạm điều khoản LinkedIn | Khoá tài khoản, thường là **vĩnh viễn**, không kháng cáo được |
| Mất tài khoản = mất cả kênh | Toàn bộ nội dung, kết nối và uy tín cá nhân Henry mất trắng |
| Tin nhắn hàng loạt lộ ngay | Chủ shop nhận ra template trong 3 giây, tỉ lệ trả lời rơi xuống gần 0 |
| Không có đường quay lại | Tài khoản cá nhân của Founder không tạo lại được như một fanpage |

**Kết luận:** tự động hoá phần **soạn thảo, xếp hàng và nhắc việc**. Giữ phần **bấm gửi ở người thật**.
Đó chính là thứ `scripts/outreach_queue.py` làm: mỗi ngày in ra đúng danh sách cần chạm hôm nay,
kèm tin nhắn đã điền sẵn tên và bối cảnh. Henry copy, sửa 1 câu cho cá nhân hoá, bấm gửi.

Chi phí: **20 phút/ngày**. Đổi lại: tài khoản an toàn và tỉ lệ trả lời cao hơn nhiều.

---

## 1. Tệp mục tiêu — chủ shop có bán trên sàn

| Trường | Giá trị |
|---|---|
| Chức danh | Founder / Chủ shop / Giám đốc / Trưởng phòng vận hành / E-commerce Manager |
| Dấu hiệu bán sàn | Hồ sơ hoặc bài viết nhắc Shopee, Lazada, TikTok Shop, Tiki, hoặc "sàn TMĐT" |
| Quy mô | 500–5.000 đơn/tháng, hoặc 20–200 nhân sự, hoặc 3–30 điểm bán |
| Ngành ưu tiên | TPCN, mỹ phẩm, thời trang, F&B, mẹ và bé — ngành có tỉ lệ mua lại cao |
| Loại trừ | Dropshipper cá nhân, shop dưới 100 đơn/tháng, đại lý bán hộ không sở hữu thương hiệu |

**Vì sao loại trừ shop nhỏ:** họ không có ngân sách và không có đủ dữ liệu để CDP tạo giá trị.
Bán cho họ tốn thời gian và tạo khách hàng churn sớm.

### Cách tìm 30 người đầu tiên (miễn phí, không cần Sales Navigator)

1. LinkedIn search → People → từ khoá: `Shopee`, `TikTok Shop`, `thương mại điện tử`, `ecommerce manager`
2. Lọc **Locations: Vietnam**
3. Lọc thêm bằng từ khoá ngành: `mỹ phẩm`, `thực phẩm chức năng`, `thời trang`
4. Xem nhóm LinkedIn về TMĐT Việt Nam → danh sách thành viên
5. Xem danh sách người tương tác dưới bài viết của các KOL ngành TMĐT
6. Người đã like/comment bài của chính Henry — **đây là nhóm chất lượng nhất**, ưu tiên số 1

Chép vào `assets/prospect-list.example.csv`. Mỗi dòng một người.

> **Kiểm chứng bắt buộc:** nếu sau 2 giờ tìm mà không đủ 30 người đúng tệp,
> LinkedIn không phải kênh của tệp này. Dừng, chuyển ngân sách thời gian sang
> Facebook Group TMĐT hoặc outbound qua Zalo. Đây là quyết định 2 giờ tiết kiệm 8 tuần.

---

## 2. Chuỗi 5 chạm

Không bán ở chạm đầu. Mục tiêu mỗi chạm chỉ là **được phép sang chạm tiếp theo**.

| Chạm | Ngày | Hành động | Mục tiêu | Stage trong CSV |
|---|---:|---|---|---|
| 1 | D0 | Gửi connection request kèm ghi chú ≤ 300 ký tự | Được chấp nhận | `connect_sent` |
| 2 | D+1 sau khi đồng ý | Cảm ơn + 1 câu hỏi về bối cảnh của họ | Có phản hồi đầu tiên | `thanks_sent` |
| 3 | D+3 | Gửi **một thứ có giá trị**, không kèm lời chào bán | Được ghi nhận là người hữu ích | `value_sent` |
| 4 | D+7 | **Đề xuất trải nghiệm** — cụ thể, ngắn, có giới hạn | Đặt được lịch | `offer_sent` |
| 5 | D+12 | Chốt hoặc đóng lịch sự | Có câu trả lời rõ ràng | `followed_up` |

Sau chạm 5: `booked` (đã đặt lịch), `no` (từ chối), hoặc `nurture` (quan tâm nhưng chưa phải lúc — chạm lại sau 90 ngày).

**Không có chạm 6.** Theo đuổi quá 5 lần làm hỏng thương hiệu cá nhân và không tăng tỉ lệ chốt.

---

## 3. Nội dung 5 tin nhắn

File thật nằm ở `assets/messages/`. Biến được script điền: `{ten}`, `{shop}`, `{san}`, `{nganh}`.

### Chạm 1 — connection note (≤ 300 ký tự, LinkedIn cắt cứng)

```
Chào {ten}, mình theo dõi mảng bán hàng đa kênh của các thương hiệu Việt.
Thấy {shop} đang bán trên {san} nên muốn kết nối để học hỏi thêm về cách anh/chị
vận hành. Cảm ơn anh/chị.
```

Quy tắc: **không nhắc sản phẩm, không nhắc bán hàng ở chạm 1.** Nhắc là mất 60% tỉ lệ chấp nhận.

### Chạm 2 — cảm ơn + câu hỏi

```
Cảm ơn {ten} đã kết nối.

Mình đang tìm hiểu một chuyện với các thương hiệu bán nhiều kênh: sau khi khách mua
trên {san}, anh/chị có cách nào liên lạc lại với họ không, hay dữ liệu nằm hết ở sàn?

Hỏi thật lòng vì mỗi shop mình gặp làm một kiểu khác nhau.
```

Đây là **câu hỏi discovery**, không phải câu dẫn dắt bán hàng. Câu trả lời cho Henry biết họ có nỗi đau hay không.

### Chạm 3 — cho đi giá trị

```
{ten} ơi, hôm trước anh/chị có nhắc chuyện dữ liệu khách nằm ở sàn.

Mình vừa viết một checklist 7 bước để gộp dữ liệu khách từ sàn + POS + Zalo OA
về một chỗ, làm được trong 30 ngày không cần đội IT. Gửi anh/chị tham khảo, không có gì để bán ở đây cả.

[link bài viết LinkedIn của Henry]
```

**Bắt buộc:** thứ gửi đi phải dùng được **kể cả khi họ không bao giờ mua**. Nếu không, đó là quảng cáo trá hình.

### Chạm 4 — đề xuất trải nghiệm

```
{ten}, mình đang mở vài buổi dựng thử miễn phí cho các thương hiệu bán trên sàn.

Cụ thể: mình lấy dữ liệu mẫu của {shop}, dựng một hồ sơ khách hàng gộp
và một kịch bản nhắn lại khách cũ. 45 phút, online, anh/chị thấy trên màn hình luôn.

Không phải buổi bán hàng — nếu sau đó anh/chị tự làm được thì mình vui.

Tuần này mình còn 2 slot. Anh/chị muốn thứ Tư hay thứ Sáu?
```

Ba thứ khiến lời mời này được nhận:
- **Cụ thể**: nói rõ 45 phút và làm gì
- **Có giới hạn**: 2 slot, không phải "khi nào anh rảnh"
- **Câu hỏi lựa chọn**: "thứ Tư hay thứ Sáu", không phải "anh có quan tâm không"

### Chạm 5 — chốt hoặc đóng lịch sự

```
{ten}, mình gửi lại tin trước phòng anh/chị bận.

Nếu chưa phải lúc thì hoàn toàn ổn — mình sẽ không nhắn thêm nữa.
Khi nào cần bàn chuyện gộp dữ liệu khách, cứ nhắn mình một tiếng.

Chúc {shop} bán tốt mùa này.
```

Câu "mình sẽ không nhắn thêm nữa" làm tăng tỉ lệ trả lời rõ rệt, và giữ cửa cho 6 tháng sau.

---

## 4. Hạn mức an toàn — con số cứng

| Hành động | Hạn mức/ngày | Hạn mức/tuần | Vì sao |
|---|---:|---:|---|
| Connection request | **15** | 75 | LinkedIn giới hạn mềm ~100/tuần; ở 75 là vùng an toàn |
| Tin nhắn follow-up | **20** | 100 | |
| Tổng thời gian | 20 phút | ~2 giờ | Trần cứng, vượt là đang lấy giờ của việc khác |

Ba quy tắc không được phá:

1. **Tỉ lệ chấp nhận dưới 25% → dừng, sửa tin nhắn chạm 1.** Không tăng số lượng để bù.
   Gửi nhiều mà bị từ chối nhiều là tín hiệu LinkedIn dùng để hạn chế tài khoản.
2. **Không gửi hàng loạt trong 5 phút.** Rải đều trong 20 phút.
3. **Mỗi tin nhắn sửa ít nhất một câu cho riêng người đó.** Script điền biến; Henry thêm ngữ cảnh thật.

---

## 5. Vòng lặp hằng ngày — 20 phút

```bash
cd ~/linkedin-ops
python3 ~/mineflow/skills/linkedin-auto-post/scripts/outreach_queue.py --list prospect-list.csv
```

Script in ra ba nhóm:

- **A. Gửi connection request** — tối đa 15 người, kèm ghi chú đã điền sẵn
- **B. Tin nhắn tới hạn hôm nay** — kèm nội dung theo đúng chạm
- **C. Cần Henry quyết** — người đã trả lời, script không xử lý được

Sau khi gửi xong, ghi nhận lại:

```bash
# Chuyển sang chạm tiếp theo và tự hẹn ngày chạm sau
python3 .../outreach_queue.py --list prospect-list.csv --done p001 p002 p003

# Người trả lời quan tâm -> đặt lịch
python3 .../outreach_queue.py --list prospect-list.csv --set p004=booked

# Người từ chối -> đóng
python3 .../outreach_queue.py --list prospect-list.csv --set p005=no
```

`--dry-run` xem trước mọi thay đổi mà không ghi vào CSV.

---

## 6. Xử lý phản đối

| Họ nói | Trả lời |
|---|---|
| "Bên mình đã có CRM rồi" | "CRM lưu người đã mua. Câu hỏi của em là anh/chị có biết ai sắp mua lại không? Đó là việc khác. Em cho anh/chị xem 10 phút thôi." |
| "Dữ liệu sàn không lấy ra được đâu" | "Đúng là sàn không trả hết. Nhưng phần lấy được cộng với dữ liệu đơn hàng và Zalo OA đã đủ dựng hồ sơ khách. Em dựng thử trên dữ liệu của anh/chị cho dễ hình dung." |
| "Đắt quá" | "Anh/chị đang chi bao nhiêu quảng cáo mỗi tháng? Nếu 10% số đó là chi để mua lại khách cũ, con số đó so với phí hằng tháng thế nào?" |
| "Để em bàn lại với team" | "Được ạ. Em gửi anh/chị một trang tóm tắt để đưa team. Thứ Sáu tuần sau em nhắn lại một lần, nếu chưa phải lúc thì em dừng." |
| "Giờ chưa phải lúc" | "Hiểu ạ. Em ghi lại chạm lại sau 3 tháng. Trong lúc đó có gì cần hỏi cứ nhắn em." → `nurture` |

**Không tranh cãi.** Ghi nhận, đưa một bước nhỏ hơn, hoặc đóng lịch sự.

---

## 7. KPI outreach hằng tuần

| KPI | Mục tiêu tháng 1 | Mục tiêu tháng 3 | Tính từ CSV |
|---|---:|---:|---|
| Người mới thêm vào danh sách | 40 | 60 | dòng `new` |
| Connection request gửi | 60 | 75 | `connect_sent` |
| Tỉ lệ chấp nhận | ≥30% | ≥40% | `connected` / `connect_sent` |
| Có hội thoại thật | 8 | 20 | `value_sent` có trả lời |
| **Buổi trải nghiệm đặt được** | **3** | **10** | `booked` |
| Tỉ lệ đặt lịch / kết nối | ≥5% | ≥12% | `booked` / `connected` |

**Chỉ số cảnh báo:** tỉ lệ chấp nhận < 25% hoặc `booked`/`connected` < 3% sau 4 tuần
→ vấn đề ở tệp hoặc ở lời mời, không phải ở số lượng. Dừng gửi thêm, sửa trước.

---

## 8. Điều kiện dừng

Sau **6 tuần** với 400+ connection request và 0 buổi trải nghiệm được đặt:
LinkedIn không phải kênh của tệp chủ shop Việt Nam. Dừng, chuyển 2 giờ/tuần
sang Facebook Group TMĐT hoặc outbound qua Zalo — nơi tệp này thực sự sinh hoạt.

Đây không phải thất bại. Đây là 6 tuần mua được một câu trả lời chắc chắn.
