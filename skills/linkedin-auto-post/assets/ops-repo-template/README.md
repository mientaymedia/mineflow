# linkedin-ops — repo vận hành

Repo **private** chứa dữ liệu vận hành: hàng đợi nội dung, bài viết, ảnh, danh sách gia hạn.
Tách khỏi repo `mineflow` (repo skills, chứa mã nguồn) vì đây là dữ liệu, không phải mã.

> **Bắt buộc để private.** Repo này chứa nội dung chưa đăng và thông tin khách hàng.

## Cấu trúc

```text
linkedin-ops/                  (private)
├── .github/workflows/
│   ├── linkedin-post.yml      # đăng bài tới hạn, 12 lần/ngày trong khung giờ đăng
│   └── gws-renewal.yml        # nhắc gia hạn Workspace, 08:00 giờ VN mỗi ngày
├── skills/                    # copy từ mineflow/skills/*/scripts/
│   ├── linkedin_post.py
│   ├── run_queue.py
│   ├── lint_posts.py
│   ├── make_image.py
│   └── renewal_check.py
├── drafts/                    # bài viết .txt
├── img/                       # ảnh 1200x1200
├── content-queue.csv          # hàng đợi đăng bài
└── renewal-tracker.csv        # danh sách gia hạn Workspace
```

## Đăng bài đầu tiên NGAY — một lệnh

```bash
./post-now.sh
```

Tự lấy token nếu chưa có, soát bài bằng lint, **hiện toàn bộ nội dung ra màn hình**,
hỏi xác nhận, rồi mới đăng. Không chờ lịch, không cần cron.
Đăng xong tự ghi `posted` và URN vào hàng đợi.

```bash
./post-now.sh w1-t5     # chỉ định bài cụ thể
```

Bài còn placeholder bị chặn, không đăng được.

---

## Cài lịch tự động — một lệnh

```bash
./setup.sh
```

Script kiểm tra môi trường, lấy token (mở trình duyệt để bấm Allow), soát bài,
cài cron, rồi chạy thử. **Không cần GitHub, không cần repo, không cần secret.**
Chạy lại nhiều lần được — nó phát hiện token còn hiệu lực thì bỏ qua bước lấy lại.

Sau đó chỉ còn đọc bài và mở khoá:

```bash
cat drafts/w1-t3-ba-ho-so-mot-khach.txt
./approve.sh --week 1
```

Muốn chạy trên GitHub Actions thay vì máy cá nhân thì theo phần dưới.

---

## Cài đặt trên GitHub Actions — năm bước

### 1. Tạo repo private

Trên GitHub: **New repository** → tên `linkedin-ops` → chọn **Private** → Create.

### 2. Copy file vào repo

```bash
git clone https://github.com/<tài-khoản>/linkedin-ops.git
cd linkedin-ops

# Template workflow và .gitignore
cp -r <đường-dẫn>/mineflow/skills/linkedin-auto-post/assets/ops-repo-template/. .

# Scripts
mkdir -p skills
cp <đường-dẫn>/mineflow/skills/linkedin-auto-post/scripts/*.py skills/
cp <đường-dẫn>/mineflow/skills/gws-renewal/scripts/*.py       skills/

# Nội dung tuần 1-4 đã viết sẵn
cp -r <đường-dẫn>/mineflow/skills/linkedin-auto-post/assets/drafts .
cp -r <đường-dẫn>/mineflow/skills/linkedin-auto-post/assets/img .
cp <đường-dẫn>/mineflow/skills/linkedin-auto-post/assets/content-queue.example.csv content-queue.csv
cp <đường-dẫn>/mineflow/skills/gws-renewal/assets/renewal-tracker.example.csv renewal-tracker.csv
```

Sau đó **sửa `renewal-tracker.csv`** thành danh sách khách Workspace thật.

### 3. Lấy token và nạp vào GitHub Secrets

```bash
python3 skills/get_token.py --client-id XXX --env-file .env
cat .env      # xem hai giá trị cần copy
```

Trên GitHub: **Settings → Secrets and variables → Actions → New repository secret**

| Tên secret | Giá trị |
|---|---|
| `LINKEDIN_ACCESS_TOKEN` | dòng `LINKEDIN_ACCESS_TOKEN=` trong `.env` |
| `LINKEDIN_AUTHOR_URN` | dòng `LINKEDIN_AUTHOR_URN=` trong `.env` |

`.env` đã nằm trong `.gitignore` — không bao giờ commit nó.

### 4. Duyệt bài rồi mở khoá

Bài do AI viết nằm ở `status = draft`. **Không bài nào lên feed cho tới khi bạn đổi sang `ready`.**

```bash
# Soát bằng lint trước
python3 skills/lint_posts.py --queue content-queue.csv

# Đọc từng bài
cat drafts/w1-t3-ba-ho-so-mot-khach.txt
```

Duyệt xong, mở khoá bằng `approve.sh`:

```bash
./approve.sh --list          # xem trạng thái toàn bộ hàng đợi
./approve.sh --week 1        # mở khoá cả tuần 1
./approve.sh w2-t3 w2-t7     # hoặc từng bài
```

`approve.sh` chạy lint trước và **từ chối mở khoá bài còn lỗi** — ba bài khung
chờ nguyên liệu sẽ không mở được cho tới khi viết xong.

Kiểm tra lại trước khi push:

```bash
python3 skills/run_queue.py --queue content-queue.csv --dry-run --limit 9
```

### 5. Bật lịch

```bash
git add -A && git commit -m "Khởi tạo repo vận hành" && git push
```

Vào tab **Actions** → bật workflows nếu GitHub hỏi.
Chạy thử ngay bằng **Run workflow** trên `LinkedIn auto-post` (nút chạy tay).

## Lịch chạy

| Workflow | Cron (UTC) | Giờ VN | Ghi chú |
|---|---|---|---|
| `linkedin-post` | `0,30 0-2,12-14 * * *` | 07:00–09:30 và 19:00–21:30 | 12 lần/ngày, mỗi lần tối đa **1 bài** |
| `gws-renewal` | `0 1 * * *` | 08:00 | Mở issue khi có khách tới hạn |

Script tự lọc bài tới hạn theo `publish_at` (giờ VN, `--tz-offset 7`), nên chạy thừa cũng vô hại.

Chi phí Actions: khoảng **180 phút/tháng**. Free tier private repo là 2.000 phút/tháng.

> Cron của GitHub Actions **có thể trễ vài phút** vào giờ cao điểm. Đó là lý do khung giờ
> rộng hơn giờ đăng thực tế. Đừng phụ thuộc vào độ chính xác đến từng phút.

## Bảo trì

| Việc | Tần suất | Cách làm |
|---|---|---|
| Refresh access token | 45 ngày/lần | Chạy lại `get_token.py`, cập nhật secret |
| Nạp bài mới | Hằng tuần | Thêm dòng vào `content-queue.csv`, đẩy file `.txt` và ảnh |
| Cập nhật danh sách gia hạn | Khi có khách mới | Sửa `renewal-tracker.csv` |

## Khi có sự cố

Tab **Actions** → chọn lần chạy → xem **Summary**. Output của script nằm ở đó.

Bảng lỗi thường gặp: `mineflow/skills/linkedin-auto-post/references/automation-runbook.md` mục 8.
