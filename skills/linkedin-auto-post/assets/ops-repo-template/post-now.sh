#!/usr/bin/env bash
# Đăng NGAY một bài lên LinkedIn. Không chờ lịch, không cần cron.
#
#   ./post-now.sh            # chọn bài đầu tiên chưa đăng
#   ./post-now.sh w1-t5      # hoặc chỉ định bài
#
# Tự lấy token nếu chưa có. Hiện bài ra màn hình và hỏi xác nhận trước khi gửi.

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
QUEUE="${QUEUE:-content-queue.csv}"
PY="$(command -v python3 || true)"
[[ -n "$PY" ]] || { echo "LỖI: chưa có python3." >&2; exit 1; }
[[ -f "$QUEUE" ]] || { echo "LỖI: không tìm thấy $QUEUE" >&2; exit 1; }

bold() { printf '\033[1m%s\033[0m\n' "$1"; }

# --- 1. Token ---
if [[ ! -f .env ]] || ! grep -q '^LINKEDIN_ACCESS_TOKEN=.\+' .env; then
  bold "Chưa có token — lấy bây giờ"
  echo "  Cần Client ID từ https://www.linkedin.com/developers/apps"
  read -r -p "  Client ID: " CID
  [[ -n "$CID" ]] || { echo "LỖI: thiếu Client ID." >&2; exit 1; }
  echo "  Trình duyệt sẽ mở. Đăng nhập LinkedIn và bấm Allow."
  LINKEDIN_CLIENT_ID="$CID" "$PY" skills/get_token.py --env-file .env
fi
set -a; . ./.env; set +a

# --- 2. Chọn bài ---
ID="${1:-}"
if [[ -z "$ID" ]]; then
  ID="$("$PY" - "$QUEUE" <<'PYEOF'
import csv, sys
for r in csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")):
    if (r.get("status") or "").strip().lower() not in ("posted", "skipped"):
        print(r["id"]); break
PYEOF
)"
  [[ -n "$ID" ]] || { echo "Không còn bài nào chưa đăng." >&2; exit 1; }
fi

read -r TEXT_FILE IMAGE ALT < <("$PY" - "$QUEUE" "$ID" <<'PYEOF'
import csv, sys
rows = {r["id"]: r for r in csv.DictReader(open(sys.argv[1], encoding="utf-8-sig"))}
r = rows.get(sys.argv[2])
if not r:
    sys.exit("LỖI: không có bài id {!r} trong hàng đợi".format(sys.argv[2]))
if (r.get("status") or "").strip().lower() == "posted":
    sys.exit("LỖI: bài {} đã đăng rồi ({})".format(sys.argv[2], r.get("post_urn") or "?"))
print(r["text_file"], r.get("image") or "-", "|" + (r.get("alt_text") or ""))
PYEOF
) || exit 1
ALT="${ALT#|}"

# --- 3. Soát bằng lint, chặn bài chưa viết xong ---
bold "Soát bài $ID"
"$PY" skills/lint_posts.py "$TEXT_FILE" || {
  echo "Bài còn lỗi — không đăng. Sửa xong chạy lại." >&2; exit 1; }

# --- 4. Cho xem rồi mới gửi ---
echo; bold "NỘI DUNG SẼ ĐĂNG LÊN LINKEDIN"
echo "────────────────────────────────────────────────────────"
cat "$TEXT_FILE"
echo "────────────────────────────────────────────────────────"
[[ "$IMAGE" != "-" ]] && echo "Ảnh    : $IMAGE" && echo "Alt    : $ALT"
echo "Đăng lên: profile cá nhân, chế độ PUBLIC"
echo
read -r -p "Đăng bài này ngay? [y/N] " OK
[[ "$OK" == "y" || "$OK" == "Y" ]] || { echo "Đã huỷ, chưa đăng gì."; exit 0; }

# --- 5. Đăng ---
ARGS=(--text-file "$TEXT_FILE")
[[ "$IMAGE" != "-" ]] && ARGS+=(--image "$IMAGE" --alt-text "$ALT")
URN="$("$PY" skills/linkedin_post.py "${ARGS[@]}")" || { echo "Đăng thất bại." >&2; exit 1; }

# --- 6. Ghi ngược vào hàng đợi ---
"$PY" - "$QUEUE" "$ID" "$URN" <<'PYEOF'
import csv, os, sys, tempfile, datetime as dt
path, pid, urn = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path, encoding="utf-8-sig", newline="") as fh:
    rd = csv.DictReader(fh); rows = list(rd); fields = rd.fieldnames
for r in rows:
    if r["id"] == pid:
        r["status"] = "posted"; r["post_urn"] = urn
        r["posted_at"] = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
d = os.path.dirname(os.path.abspath(path)) or "."
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
os.replace(tmp, path)
PYEOF

echo
bold "ĐÃ ĐĂNG"
echo "  $URN"
echo "  Xem tại: https://www.linkedin.com/feed/"
echo
echo "  Việc tiếp theo — quan trọng hơn cả bài viết:"
echo "  Trả lời mọi bình luận trong 2 giờ đầu. Đó là nơi hội thoại thành deal."
[[ "$ID" == "w4-t7" ]] && echo "  Bài này: dán link https://mineflow.vn/ vào BÌNH LUẬN ĐẦU TIÊN."
