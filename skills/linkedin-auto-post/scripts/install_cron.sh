#!/usr/bin/env bash
# Cài lịch đăng bài bằng cron trên MÁY CỦA HENRY (lựa chọn thay cho GitHub Actions).
#
#   ./install_cron.sh ~/linkedin-ops
#
# Chạy lại nhiều lần được: gỡ mục cũ rồi cài lại, không nhân bản dòng cron.

set -euo pipefail

OPS_DIR="${1:-$HOME/linkedin-ops}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKER="# linkedin-auto-post"
PYTHON="$(command -v python3 || true)"

if [[ -z "$PYTHON" ]]; then
  echo "LỖI: không tìm thấy python3." >&2; exit 1
fi
for f in content-queue.csv .env; do
  if [[ ! -f "$OPS_DIR/$f" ]]; then
    echo "LỖI: thiếu $OPS_DIR/$f — xem assets/ops-repo-template/README.md" >&2; exit 1
  fi
done
if [[ "$(stat -c '%a' "$OPS_DIR/.env" 2>/dev/null || stat -f '%A' "$OPS_DIR/.env")" != "600" ]]; then
  echo "CẢNH BÁO: $OPS_DIR/.env không ở quyền 600. Chạy: chmod 600 $OPS_DIR/.env" >&2
fi

POST_JOB="*/15 * * * * cd $OPS_DIR && set -a && . ./.env && set +a && $PYTHON $SKILL_DIR/run_queue.py --queue content-queue.csv --limit 1 --tz-offset 7 >> $OPS_DIR/run.log 2>&1 $MARKER"

RENEWAL="$(dirname "$SKILL_DIR")/../gws-renewal/scripts/renewal_check.py"
RENEW_JOB=""
if [[ -f "$RENEWAL" && -f "$OPS_DIR/renewal-tracker.csv" ]]; then
  RENEW_JOB="0 8 * * * cd $OPS_DIR && $PYTHON $RENEWAL --list renewal-tracker.csv >> $OPS_DIR/renewal.log 2>&1 $MARKER"
fi

# Giữ nguyên các mục cron khác của Henry, chỉ thay mục của skill này
CURRENT="$(crontab -l 2>/dev/null | grep -vF "$MARKER" || true)"
{
  [[ -n "$CURRENT" ]] && printf '%s\n' "$CURRENT"
  printf '%s\n' "$POST_JOB"
  [[ -n "$RENEW_JOB" ]] && printf '%s\n' "$RENEW_JOB"
} | crontab -

echo "Đã cài lịch:"
echo "  - Đăng bài  : mỗi 15 phút, tối đa 1 bài mỗi lần"
[[ -n "$RENEW_JOB" ]] && echo "  - Gia hạn   : 08:00 hằng ngày"
echo
echo "Xem lại : crontab -l"
echo "Nhật ký : tail -f $OPS_DIR/run.log"
echo "Gỡ bỏ   : crontab -l | grep -vF '$MARKER' | crontab -"
