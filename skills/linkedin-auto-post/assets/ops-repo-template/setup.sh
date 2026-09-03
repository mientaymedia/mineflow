#!/usr/bin/env bash
# Cài đặt toàn bộ hệ thống bằng một lệnh. Chạy trên máy cá nhân.
#
#   ./setup.sh
#
# Không cần GitHub, không cần repo, không cần secret. Chỉ cần máy này.
# Script làm: kiểm tra môi trường -> lấy token -> soát bài -> cài lịch -> chạy thử.

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
ROOT="$(pwd)"

c_ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
c_warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }
c_err()  { printf '  \033[31m✗\033[0m %s\n' "$1" >&2; }
step()   { printf '\n\033[1m%s\033[0m\n' "$1"; }

step "1/5  Kiểm tra môi trường"
PY="$(command -v python3 || true)"
[[ -n "$PY" ]] || { c_err "Chưa có python3. Cài Python 3.8 trở lên rồi chạy lại."; exit 1; }
PYV="$("$PY" -c 'import sys;print("%d.%d"%sys.version_info[:2])')"
"$PY" -c 'import sys;sys.exit(0 if sys.version_info>=(3,8) else 1)' \
  || { c_err "Cần Python 3.8+, đang có $PYV"; exit 1; }
c_ok "python3 $PYV"
for f in skills/run_queue.py skills/get_token.py content-queue.csv; do
  [[ -f "$f" ]] || { c_err "Thiếu $f — giải nén chưa đủ?"; exit 1; }
done
c_ok "đủ file"
command -v crontab >/dev/null 2>&1 && c_ok "có crontab" || c_warn "không có crontab — sẽ bỏ qua bước cài lịch"

step "2/5  Lấy LinkedIn access token"
if [[ -f .env ]] && grep -q '^LINKEDIN_ACCESS_TOKEN=.\+' .env; then
  c_ok ".env đã có token"
  set -a; . ./.env; set +a
  CODE="$(curl -s --max-time 15 -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $LINKEDIN_ACCESS_TOKEN" \
    https://api.linkedin.com/v2/userinfo 2>/dev/null || true)"
  CODE="${CODE:-000}"
  case "$CODE" in
    200) c_ok "token còn hiệu lực" ;;
    401) c_warn "token hết hạn — sẽ lấy lại"; rm -f .env ;;
    *)   c_warn "không kiểm tra được token (HTTP $CODE), vẫn dùng tiếp" ;;
  esac
fi

if [[ ! -f .env ]]; then
  echo "  Cần Client ID và Client Secret từ https://www.linkedin.com/developers/apps"
  read -r -p "  Client ID: " CID
  read -r -s -p "  Client Secret (gõ xong bấm Enter, chữ sẽ không hiện): " CSEC; echo
  [[ -n "$CID" && -n "$CSEC" ]] || { c_err "Thiếu Client ID hoặc Secret."; exit 1; }
  echo "  Trình duyệt sẽ mở ra. Đăng nhập LinkedIn và bấm Allow."
  "$PY" skills/get_token.py --client-id "$CID" --client-secret "$CSEC" --env-file .env \
    || { c_err "Lấy token thất bại. Kiểm tra redirect URL http://localhost:8000/callback trong tab Auth."; exit 1; }
  unset CSEC
  c_ok "đã ghi .env (quyền 600)"
fi

step "3/5  Soát bài viết"
"$PY" skills/lint_posts.py --queue content-queue.csv || true

step "4/5  Trạng thái hàng đợi"
awk -F, 'NR>1 {printf "  %-8s %-18s %s\n", $1, $2, $3}' content-queue.csv
READY="$(awk -F, 'NR>1 && $3=="ready"' content-queue.csv | wc -l | tr -d ' ')"
if [[ "$READY" == "0" ]]; then
  c_warn "chưa bài nào ở trạng thái ready — sẽ không có gì được đăng"
  echo "     Đọc bài:    cat drafts/<tên-file>.txt"
  echo "     Mở khoá:    ./approve.sh --week 1"
else
  c_ok "$READY bài đã mở khoá"
fi

step "5/5  Cài lịch và chạy thử"
if command -v crontab >/dev/null 2>&1; then
  MARKER="# linkedin-auto-post"
  POST="*/15 * * * * cd $ROOT && set -a && . ./.env && set +a && $PY $ROOT/skills/run_queue.py --queue content-queue.csv --limit 1 --tz-offset 7 >> $ROOT/run.log 2>&1 $MARKER"
  RENEW=""
  [[ -f renewal-tracker.csv ]] && \
    RENEW="0 8 * * * cd $ROOT && $PY $ROOT/skills/renewal_check.py --list renewal-tracker.csv >> $ROOT/renewal.log 2>&1 $MARKER"
  CUR="$(crontab -l 2>/dev/null | grep -vF "$MARKER" || true)"
  { [[ -n "$CUR" ]] && printf '%s\n' "$CUR"; printf '%s\n' "$POST"; [[ -n "$RENEW" ]] && printf '%s\n' "$RENEW"; } | crontab -
  c_ok "đăng bài: mỗi 15 phút, tối đa 1 bài"
  [[ -n "$RENEW" ]] && c_ok "gia hạn Workspace: 08:00 hằng ngày"
else
  c_warn "bỏ qua cài lịch (không có crontab)"
fi

echo
"$PY" skills/run_queue.py --queue content-queue.csv --dry-run --limit 9 2>&1 | tail -12

cat <<TXT

$(printf '\033[1mXONG.\033[0m')

  Việc hằng ngày:
    ./approve.sh --list                          xem hàng đợi
    ./approve.sh --week 2                        mở khoá tuần tiếp theo
    python3 skills/renewal_check.py --list renewal-tracker.csv    ai cần chạm hôm nay

  Nhật ký:
    tail -f run.log

  Gỡ lịch:
    crontab -l | grep -vF '# linkedin-auto-post' | crontab -

  Nhớ: refresh token sau 45 ngày -> chạy lại ./setup.sh
TXT
