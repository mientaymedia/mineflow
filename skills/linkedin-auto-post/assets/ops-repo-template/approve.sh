#!/usr/bin/env bash
# Mở khoá bài đã duyệt: đổi status từ draft sang ready.
#
#   ./approve.sh w1-t3 w1-t5 w1-t7     # mở khoá từng bài
#   ./approve.sh --week 1              # mở khoá cả tuần 1
#   ./approve.sh --list                # xem trạng thái hiện tại
#
# Chạy lint trước, từ chối mở khoá bài còn lỗi.

set -euo pipefail
QUEUE="${QUEUE:-content-queue.csv}"
[[ -f "$QUEUE" ]] || { echo "LỖI: không tìm thấy $QUEUE" >&2; exit 1; }

if [[ "${1:-}" == "--list" ]]; then
  printf '%-8s %-18s %-8s %s\n' ID PUBLISH_AT STATUS FILE
  awk -F, 'NR>1 {printf "%-8s %-18s %-8s %s\n", $1, $2, $3, $4}' "$QUEUE"
  exit 0
fi

IDS=()
if [[ "${1:-}" == "--week" ]]; then
  [[ -n "${2:-}" ]] || { echo "LỖI: --week cần số tuần" >&2; exit 1; }
  while IFS=, read -r id _; do [[ "$id" == w$2-* ]] && IDS+=("$id"); done < <(tail -n +2 "$QUEUE")
else
  IDS=("$@")
fi
[[ ${#IDS[@]} -gt 0 ]] || { echo "Dùng: ./approve.sh <id>... | --week N | --list" >&2; exit 1; }

for id in "${IDS[@]}"; do
  line="$(awk -F, -v id="$id" '$1==id' "$QUEUE")"
  if [[ -z "$line" ]]; then echo "  $id: không có trong hàng đợi" >&2; continue; fi
  file="$(printf '%s' "$line" | cut -d, -f4)"
  if ! python3 skills/lint_posts.py "$file" >/dev/null 2>&1; then
    echo "  $id: BỊ CHẶN — bài còn lỗi lint. Chạy: python3 skills/lint_posts.py $file" >&2
    continue
  fi
  # Chỉ đổi cột status (cột 3) của đúng dòng có id này
  python3 - "$QUEUE" "$id" <<'PY'
import csv, os, sys, tempfile
path, target = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8-sig", newline="") as fh:
    reader = csv.DictReader(fh); rows = list(reader); fields = reader.fieldnames
for row in rows:
    if row["id"] == target and row["status"] == "draft":
        row["status"] = "ready"
d = os.path.dirname(os.path.abspath(path)) or "."
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
os.replace(tmp, path)
PY
  echo "  $id: draft -> ready"
done
echo
echo "Kiểm tra lại trước khi push:"
echo "  python3 skills/run_queue.py --queue $QUEUE --dry-run --limit 9"
