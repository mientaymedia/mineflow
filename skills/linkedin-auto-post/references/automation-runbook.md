# Automation Runbook — Vận hành đăng tự động

## 0. Nguyên tắc trước khi bật automation

**Không tự động hoá một quy trình chưa ổn định.** Thứ tự bắt buộc:

1. Đăng tay 10 bài. Đo bài nào có phản hồi thật (comment có nội dung, tin nhắn inbox).
2. Chốt được 5 template hoạt động.
3. Lúc đó mới bật hàng đợi tự động.

Automation nhân bản kết quả có sẵn. Nếu nội dung chưa tạo được phản hồi, tự động hoá chỉ nhân bản sự im lặng nhanh hơn.

## 1. Cấu trúc thư mục làm việc

Đặt ngoài repo skill (đây là dữ liệu vận hành, không phải mã nguồn):

```
~/linkedin-ops/
├── content-queue.csv          # hàng đợi, mở bằng Excel/Google Sheets
├── drafts/                    # nội dung bài, mỗi bài 1 file .txt UTF-8
│   ├── w1-t3-chi-phi-khach-cu.txt
│   └── ...
├── img/                       # ảnh 1200x1200 PNG/JPG
│   └── w1-t3-big-number.png
└── .env                       # token — KHÔNG commit
```

Copy `assets/content-queue.example.csv` làm điểm bắt đầu.

## 2. Schema hàng đợi CSV

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| `id` | ✔ | Mã bài duy nhất, vd `w1-t3` |
| `publish_at` | ✔ | `YYYY-MM-DD HH:MM`, **giờ Việt Nam** (script quy đổi bằng `--tz-offset 7`) |
| `status` | ✔ | `draft` \| `ready` \| `posted` \| `error` \| `skipped` — **chỉ `ready` mới được đăng** |
| `text_file` | ✔ | Đường dẫn file `.txt`, tương đối so với thư mục chứa CSV |
| `image` | | Đường dẫn ảnh; nhiều ảnh ngăn bằng `;` (tối đa 9) |
| `alt_text` | | Alt text theo đúng thứ tự ảnh, ngăn bằng `;`. **Số lượng phải khớp số ảnh** |
| `visibility` | | `PUBLIC` (mặc định) \| `CONNECTIONS` \| `LOGGED_IN` |
| `post_urn` | auto | Script ghi vào sau khi đăng |
| `posted_at` | auto | Script ghi vào, UTC ISO 8601 |
| `note` | auto | Script ghi lỗi vào đây |

**Hai chốt an toàn, không phải một:**

1. **Cột `status`** — chỉ dòng `ready` mới được đăng.
2. **Lint tự động** — trước mỗi lần đăng, `run_queue.py` chạy `lint_posts.py` trên bài đó.
   Bài còn placeholder chưa điền, hook quá 200 ký tự, quá 3 hashtag, hoặc có link ngoài
   trong body sẽ **bị từ chối kể cả khi `status` đã là `ready`**. Đây là lưới an toàn cho
   trường hợp đổi `status` nhầm cho một bài mới chỉ là khung chờ nguyên liệu.
   Bỏ qua bằng `--skip-lint` — không khuyến khích.

**Cột `status` chính là chốt kiểm duyệt.** Viết bài xong để `draft`. Chỉ đổi sang `ready`
sau khi đã đọc lại và chạy `--dry-run`. Không có bài nào tự lên feed mà bạn chưa duyệt.

## 3. Quy trình chạy hằng tuần

```bash
cd ~/linkedin-ops
set -a && source .env && set +a          # nạp LINKEDIN_ACCESS_TOKEN, LINKEDIN_AUTHOR_URN

# B0: soát bài bằng lint trước khi duyệt
python3 ~/mineflow/skills/linkedin-auto-post/scripts/lint_posts.py \
  --queue content-queue.csv

# B1: kiểm tra payload trước, không gọi API
python3 ~/mineflow/skills/linkedin-auto-post/scripts/run_queue.py \
  --queue content-queue.csv --dry-run --limit 9

# B2: nếu payload đúng, đổi status các bài sang 'ready' trong CSV

# B3: cron tự chạy phần còn lại
```

`--dry-run` **không sửa CSV** và không gọi API — chạy bao nhiêu lần cũng an toàn.

## 3b. Bộ triển khai sẵn — dùng cái này thay vì tự dựng

`assets/ops-repo-template/` chứa đủ file cho một repo vận hành private:

```text
ops-repo-template/
├── .github/workflows/linkedin-post.yml   # đăng bài, 12 lần/ngày trong khung giờ đăng
├── .github/workflows/gws-renewal.yml     # nhắc gia hạn, mở issue khi có việc
├── .gitignore
└── README.md                             # hướng dẫn cài đặt 5 bước
```

Hoặc chạy trên máy cá nhân: `scripts/install_cron.sh ~/linkedin-ops` — cài cron,
chạy lại nhiều lần được, không nhân bản dòng cron, và kiểm tra `.env` có đúng quyền 600 không.

**Repo vận hành phải để private** — nó chứa nội dung chưa đăng và thông tin khách hàng.

## 4. Lên lịch bằng cron

Chạy mỗi 15 phút; script tự bỏ qua bài chưa tới hạn.

```cron
# LinkedIn auto-post — mỗi 15 phút, tối đa 1 bài mỗi lần
*/15 * * * * cd $HOME/linkedin-ops && set -a && . ./.env && set +a && \
  /usr/bin/python3 $HOME/mineflow/skills/linkedin-auto-post/scripts/run_queue.py \
  --queue content-queue.csv --limit 1 >> $HOME/linkedin-ops/run.log 2>&1
```

Vì sao `--limit 1`: nếu queue có 3 bài quá hạn, bạn không muốn cả 3 lên feed trong cùng một phút.
Giới hạn 1 bài/lần chạy khiến chúng cách nhau ít nhất 15 phút.

`run_queue.py` trả về **exit code 1 khi có lỗi** — dùng để bắn cảnh báo trong cron hoặc CI.

## 5. Lên lịch bằng GitHub Actions

Dùng khi không có máy chạy 24/7. Ảnh và bài viết nằm trong một private repo riêng.

```yaml
name: linkedin-auto-post
on:
  schedule:
    - cron: "0,30 * * * *"    # UTC — 08:00 giờ VN = 01:00 UTC
  workflow_dispatch:

jobs:
  post:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Publish due posts
        env:
          LINKEDIN_ACCESS_TOKEN: ${{ secrets.LINKEDIN_ACCESS_TOKEN }}
          LINKEDIN_AUTHOR_URN: ${{ secrets.LINKEDIN_AUTHOR_URN }}
        run: python3 scripts/run_queue.py --queue content-queue.csv --limit 1
      - name: Commit queue state
        run: |
          git config user.name  "linkedin-bot"
          git config user.email "bot@users.noreply.github.com"
          git add content-queue.csv
          git diff --staged --quiet || git commit -m "chore: cập nhật trạng thái hàng đợi"
          git push
```

Lưu ý: cron của GitHub Actions tính theo **UTC** và có thể trễ vài phút vào giờ cao điểm.
Đừng phụ thuộc vào độ chính xác đến từng phút.

## 6. Quản lý token — việc bảo trì duy nhất

Access token LinkedIn sống **60 ngày**.

| Việc | Tần suất | Cách làm |
|---|---|---|
| Refresh token | 45 ngày/lần (đặt lịch nhắc) | Xem mục 2 trong `linkedin-api.md` |
| Kiểm tra token còn sống | Hằng tuần | `curl -s -o /dev/null -w "%{http_code}" https://api.linkedin.com/v2/userinfo -H "Authorization: Bearer $LINKEDIN_ACCESS_TOKEN"` → mong đợi `200` |
| Xoay token khi nghi lộ | Ngay lập tức | Revoke trong LinkedIn Developer app, tạo lại |
| **Xoay client secret khi lộ** | Ngay lập tức | Tab **Auth** của app → tạo secret mới. Secret cũ mất hiệu lực. Sau đó chạy lại `get_token.py` và cập nhật secret trên GitHub |

**Client secret cũng là bí mật, ngang với token.** Ai có `client_id` + `client_secret`
có thể dựng luồng OAuth mạo danh app của bạn. Đừng dán vào chat, tin nhắn, hay issue.

**Không bao giờ commit token.** Kiểm tra trước mỗi lần push:
```bash
git diff --staged | grep -iE 'AQ[A-Za-z0-9_-]{20,}|access_token' && echo "DỪNG LẠI"
```

## 7. Guardrail — tránh bị LinkedIn hạn chế tài khoản

| Quy tắc | Lý do |
|---|---|
| Tối đa **3 bài/tuần** | Vượt quá là dấu hiệu hành vi bot với tài khoản mới |
| Tối đa **1 bài/lần chạy** | Tránh dồn bài lên feed cùng lúc |
| Nghỉ **≥ 2 giây** giữa các request (script đã làm) | Nhịp giống người dùng thật |
| **Không** tự động comment | LinkedIn phát hiện rất tốt và khoá tài khoản |
| **Không** tự động gửi connection request | Như trên — việc này Henry làm tay, 20 phút/tuần |
| **Không** tự động trả lời tin nhắn | Inbox là nơi chốt deal, không giao cho bot |

Chỉ tự động hoá phần **đăng bài**. Toàn bộ phần tương tác giữ ở người thật.

## 8. Xử lý sự cố

| Triệu chứng | Nguyên nhân | Xử lý |
|---|---|---|
| `LỖI: LinkedIn API 401` | Token hết hạn | Refresh token, đổi `status` từ `error` về `ready`, chạy lại |
| `LỖI: LinkedIn API 426` | Version API quá cũ | Đặt `LINKEDIN_API_VERSION` sang tháng mới hơn |
| `LỖI: LinkedIn API 422` | Nội dung có ký tự lạ | Script đã tự escape; nếu vẫn lỗi, kiểm tra bài có emoji hiếm hoặc ký tự vô hình |
| `số alt_text (0) không khớp số ảnh (1)` | Quên điền alt text | Điền `alt_text`, đổi `status` về `ready` |
| `Không có bài nào tới hạn` | Không có dòng `ready` quá hạn | Kiểm tra cột `status` và `publish_at` |
| Bài đăng đúng nhưng `post_urn` rỗng | LinkedIn không trả header `x-restli-id` | Bài vẫn lên; kiểm tra trên profile rồi điền tay |
| Bài lên feed sai giờ | Sai `--tz-offset` | Giờ VN dùng `--tz-offset 7` |

**Sau mọi lỗi:** sửa nguyên nhân → đổi `status` từ `error` về `ready` → chạy lại.
Bài đã `posted` sẽ không bị đăng lại.

## 9. Dashboard KPI hằng tuần

`run_queue.py` chỉ lo phần đăng. Số liệu hiệu quả phải lấy tay từ LinkedIn analytics
(API analytics chỉ mở cho Company Page đã được duyệt Community Management).

Bảng theo dõi tối thiểu — mỗi tuần một dòng:

| Tuần | Bài đăng | Impression | Profile view | CR gửi | CR nhận | Hội thoại inbox | **Discovery call** | Proposal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| W1 | 3 | | | | | | | |

Chỉ **hai cột cuối** quyết định kênh này có đáng duy trì hay không.
Impression tăng mà discovery call bằng 0 sau 8 tuần nghĩa là sai ICP hoặc sai offer, không phải sai nội dung.

## 10. Chi phí và điều kiện dừng

| Hạng mục | Chi phí |
|---|---|
| LinkedIn API | 0đ |
| Hạ tầng chạy cron | 0đ (máy có sẵn) hoặc ~0đ (GitHub Actions free tier) |
| Thời gian Henry | ~4 giờ/tuần |
| **Chi phí thật** | **4 giờ/tuần của Founder** — đây là con số cần theo dõi |

**Điều kiện dừng:** 8 tuần, 24 bài, đúng lịch, mà không có discovery call nào →
dừng kênh LinkedIn, chuyển 4 giờ đó sang outbound trực tiếp tới danh sách 50 khách mục tiêu.

## 11. Tuỳ chọn: chuyển sang workflow Mineflow

Nếu MineFlow đã có module workflow (trigger theo lịch + HTTP step), có thể thay cron/GitHub Actions
bằng chính workflow của MineFlow. Lợi ích: một khách hàng tham chiếu là chính mình, và có case study thật để viết bài Pillar 2.

Bước chuyển: giữ nguyên logic 3 bước trong `linkedin-api.md`
(initializeUpload → PUT binary → POST /rest/posts) dưới dạng 3 HTTP step.
Chỉ làm việc này **sau khi** quy trình đã chạy ổn định 4 tuần bằng script.
