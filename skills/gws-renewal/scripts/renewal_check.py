#!/usr/bin/env python3
"""Theo dõi gia hạn Google Workspace: ai tới hạn cần chạm hôm nay.

Chỉ dùng thư viện chuẩn Python 3.8+.

Cột CSV (xem assets/renewal-tracker.example.csv):
    id, khach_hang, nguoi_lien_he, zalo_or_phone, so_seat, gia_moi_seat_nam,
    expiry_date (YYYY-MM-DD), stage, last_touch_at, last_stage_done, note

stage: active | at_risk | renewed | churned | paused

Ví dụ:
    python3 renewal_check.py --list renewal-tracker.csv
    python3 renewal_check.py --list renewal-tracker.csv --done c001 c002
    python3 renewal_check.py --list renewal-tracker.csv --renewed c001
    python3 renewal_check.py --list renewal-tracker.csv --report
"""

import argparse
import csv
import datetime as dt
import os
import sys
import tempfile

FIELDS = ["id", "khach_hang", "nguoi_lien_he", "zalo_or_phone", "so_seat",
          "gia_moi_seat_nam", "expiry_date", "stage", "last_touch_at",
          "last_stage_done", "note"]

# (số ngày trước hạn, mã mốc, việc cần làm, kênh)
CADENCE = [
    (90, "T-90", "Kiểm tra số user thực tế so với số seat đang trả", "Nội bộ"),
    (60, "T-60", "Nhắn thăm hỏi, báo trước ngày hết hạn", "Zalo"),
    (30, "T-30", "Gửi báo giá gia hạn kèm hoá đơn mẫu", "Email"),
    (14, "T-14", "Gọi xác nhận", "Điện thoại"),
    (7,  "T-7",  "Nhắc cuối, nêu rõ rủi ro gián đoạn dịch vụ", "Zalo"),
    (-1, "T+1",  "Xác nhận đã gia hạn, hỏi có cần thêm seat không", "Zalo"),
]
STAGE_ORDER = [code for _, code, _, _ in CADENCE]

ACTIVE_STAGES = {"active", "at_risk"}
RENEWAL_RATE_ALERT = 0.85


def today():
    return dt.date.today()


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def to_number(value):
    try:
        return float(str(value or "").replace(",", "").strip() or 0)
    except ValueError:
        return 0.0


def read_list(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        for field in FIELDS:
            row.setdefault(field, "")
        if not (row.get("stage") or "").strip():
            row["stage"] = "active"
    return rows


def write_list(path, rows):
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({f: row.get(f, "") for f in FIELDS})
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def due_stage(row):
    """Mốc cần làm hôm nay.

    Khi nhiều mốc cùng đã tới ngưỡng (ví dụ còn 28 ngày thì T-90, T-60 và T-30
    đều qua), phải lấy mốc **sát hạn nhất**, không phải mốc đầu tiên — nếu không
    sẽ đi kiểm tra seat trong khi lẽ ra phải gửi báo giá gấp.

    Trả về (code, việc, kênh, số ngày còn lại, số mốc đã lỡ).
    """
    expiry = parse_date(row.get("expiry_date"))
    if expiry is None:
        return None
    days_left = (expiry - today()).days
    done = (row.get("last_stage_done") or "").strip()
    done_idx = STAGE_ORDER.index(done) if done in STAGE_ORDER else -1

    reached = []
    for idx, (threshold, code, task, channel) in enumerate(CADENCE):
        if idx <= done_idx:
            continue
        # T+1 chỉ kích hoạt sau ngày hết hạn; các mốc còn lại khi đã tới ngưỡng
        hit = days_left < 0 if threshold < 0 else days_left <= threshold
        if hit:
            reached.append((code, task, channel))
    if not reached:
        return None
    code, task, channel = reached[-1]
    return code, task, channel, days_left, len(reached) - 1


def show_worklist(rows):
    due, overdue, broken = [], [], []
    for row in rows:
        stage = (row.get("stage") or "active").strip()
        if stage not in ACTIVE_STAGES:
            continue
        if parse_date(row.get("expiry_date")) is None:
            broken.append((row, "expiry_date sai hoặc trống: {!r}".format(row.get("expiry_date"))))
            continue
        item = due_stage(row)
        if item:
            (overdue if item[3] < 0 else due).append((row, item))

    due.sort(key=lambda x: x[1][3])

    print("=" * 72)
    print("GIA HẠN GOOGLE WORKSPACE — VIỆC HÔM NAY {}".format(today()))
    print("=" * 72)

    if overdue:
        print("\n### ĐÃ QUÁ HẠN — xử lý trước ({})\n".format(len(overdue)))
        for row, (code, task, channel, days, missed) in overdue:
            print("  [{}] {} — hết hạn {} ngày trước".format(code, row.get("khach_hang"), -days))
            print("      {} | {} | {}".format(task, channel, row.get("zalo_or_phone") or "-"))

    print("\n### CẦN CHẠM HÔM NAY ({})\n".format(len(due)))
    if not due:
        print("  (không có ai tới hạn)")
    for row, (code, task, channel, days, missed) in due:
        seats = to_number(row.get("so_seat"))
        value = seats * to_number(row.get("gia_moi_seat_nam"))
        print("  " + "-" * 68)
        print("  [{}] {}  ({:.0f} ngày nữa hết hạn)".format(code, row.get("khach_hang"), days))
        print("      việc  : {}".format(task))
        if missed:
            print("      ⚠ đã lỡ {} mốc trước đó — chạm bù ngay".format(missed))
        print("      kênh  : {} -> {}".format(channel, row.get("zalo_or_phone") or "chưa có"))
        print("      người : {}".format(row.get("nguoi_lien_he") or "-"))
        print("      giá trị: {:.0f} seat, ~{:,.0f}đ/năm".format(seats, value))
        if (row.get("note") or "").strip():
            print("      ghi chú: {}".format(row["note"].strip()))

    if broken:
        print("\n### DỮ LIỆU HỎNG ({})\n".format(len(broken)))
        for row, reason in broken:
            print("  {} | {} | {}".format(row.get("id"), row.get("khach_hang"), reason))

    ids = [row.get("id") for row, _ in due + overdue]
    if ids:
        print("\n" + "-" * 72)
        print("Chạm xong thì ghi nhận:  --done " + " ".join(i for i in ids if i))
        print("Khách đã gia hạn:        --renewed <id>")
    return 0


def mark_done(rows, ids):
    index = {(r.get("id") or "").strip(): r for r in rows}
    changed = False
    for cid in ids:
        row = index.get(cid)
        if row is None:
            print("  {}: không tìm thấy".format(cid), file=sys.stderr)
            continue
        item = due_stage(row)
        if not item:
            print("  {}: không có mốc nào đang tới hạn".format(cid), file=sys.stderr)
            continue
        row["last_stage_done"] = item[0]
        row["last_touch_at"] = today().isoformat()
        changed = True
        print("  {}: đã chạm mốc {}".format(cid, item[0]))
    return changed


def mark_renewed(rows, ids, months):
    index = {(r.get("id") or "").strip(): r for r in rows}
    changed = False
    for cid in ids:
        row = index.get(cid)
        if row is None:
            print("  {}: không tìm thấy".format(cid), file=sys.stderr)
            continue
        expiry = parse_date(row.get("expiry_date"))
        if expiry is None:
            print("  {}: expiry_date không đọc được".format(cid), file=sys.stderr)
            continue
        # Dời hạn thêm N tháng, giữ nguyên ngày trong tháng khi có thể
        year = expiry.year + (expiry.month - 1 + months) // 12
        month = (expiry.month - 1 + months) % 12 + 1
        day = min(expiry.day, [31, 29 if year % 4 == 0 and (year % 100 or not year % 400) else 28,
                               31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        row["expiry_date"] = dt.date(year, month, day).isoformat()
        row["stage"] = "active"
        row["last_stage_done"] = ""
        row["last_touch_at"] = today().isoformat()
        changed = True
        print("  {}: đã gia hạn, hạn mới {}".format(cid, row["expiry_date"]))
    return changed


def report(rows):
    active = [r for r in rows if (r.get("stage") or "").strip() in ACTIVE_STAGES]
    renewed = [r for r in rows if (r.get("stage") or "").strip() == "renewed"]
    churned = [r for r in rows if (r.get("stage") or "").strip() == "churned"]

    seats = sum(to_number(r.get("so_seat")) for r in active)
    arr = sum(to_number(r.get("so_seat")) * to_number(r.get("gia_moi_seat_nam")) for r in active)

    print("\n" + "=" * 72)
    print("TOÀN CẢNH MẢNG GOOGLE WORKSPACE")
    print("=" * 72)
    print("  Khách đang hoạt động : {}".format(len(active)))
    print("  Tổng seat            : {:.0f}".format(seats))
    print("  Doanh thu năm (ARR)  : {:,.0f}đ".format(arr))

    decided = len(renewed) + len(churned)
    if decided:
        rate = len(renewed) / decided
        print("  Tỉ lệ gia hạn        : {:.0%}  ({}/{})".format(rate, len(renewed), decided))
        if rate < RENEWAL_RATE_ALERT:
            print("  ⚠ Dưới {:.0%} — đang mất khách âm thầm. Sửa nhịp chạm trước khi tìm khách mới."
                  .format(RENEWAL_RATE_ALERT))
    else:
        print("  Tỉ lệ gia hạn        : chưa đủ dữ liệu")

    upcoming = []
    for row in active:
        expiry = parse_date(row.get("expiry_date"))
        if expiry and 0 <= (expiry - today()).days <= 90:
            upcoming.append((expiry, row))
    upcoming.sort(key=lambda x: x[0])

    print("\n  Hết hạn trong 90 ngày tới: {}".format(len(upcoming)))
    for expiry, row in upcoming:
        value = to_number(row.get("so_seat")) * to_number(row.get("gia_moi_seat_nam"))
        print("    {}  {:<26} {:>3} ngày  {:>12,.0f}đ".format(
            expiry, (row.get("khach_hang") or "")[:26], (expiry - today()).days, value))

    at_risk = sum(to_number(r.get("so_seat")) * to_number(r.get("gia_moi_seat_nam"))
                  for _, r in upcoming)
    if at_risk:
        print("\n  Doanh thu cần bảo vệ trong 90 ngày: {:,.0f}đ".format(at_risk))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Theo dõi gia hạn Google Workspace theo nhịp T-90 đến T+1.")
    parser.add_argument("--list", required=True, help="Đường dẫn renewal-tracker.csv")
    parser.add_argument("--done", nargs="+", metavar="ID", help="Đã chạm xong các khách này")
    parser.add_argument("--renewed", nargs="+", metavar="ID", help="Các khách đã gia hạn")
    parser.add_argument("--months", type=int, default=12, help="Số tháng gia hạn (mặc định 12)")
    parser.add_argument("--report", action="store_true", help="In toàn cảnh mảng")
    parser.add_argument("--dry-run", action="store_true", help="Xem trước, không ghi CSV")
    args = parser.parse_args(argv)

    path = os.path.abspath(args.list)
    if not os.path.isfile(path):
        print("LỖI: không tìm thấy " + path, file=sys.stderr)
        return 1
    rows = read_list(path)

    if args.done or args.renewed:
        changed = False
        if args.done:
            changed |= mark_done(rows, args.done)
        if args.renewed:
            changed |= mark_renewed(rows, args.renewed, args.months)
        if changed and not args.dry_run:
            write_list(path, rows)
            print("\nĐã cập nhật " + os.path.basename(path))
        elif args.dry_run:
            print("\n[dry-run] Không ghi vào CSV.")
        report(rows)
        return 0

    if args.report:
        report(rows)
        return 0

    rc = show_worklist(rows)
    report(rows)
    return rc


if __name__ == "__main__":
    sys.exit(main())
