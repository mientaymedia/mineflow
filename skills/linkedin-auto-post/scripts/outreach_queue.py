#!/usr/bin/env python3
"""Hàng đợi outreach LinkedIn: in ra việc cần chạm hôm nay, kèm tin nhắn đã điền sẵn.

Script này KHÔNG gửi gì lên LinkedIn. Cố ý như vậy: tự động gửi connection request
hoặc tin nhắn hàng loạt vi phạm điều khoản LinkedIn và thường bị khoá tài khoản
vĩnh viễn. Script lo phần soạn thảo, xếp hàng và nhắc việc; Henry bấm gửi.

Chỉ dùng thư viện chuẩn Python 3.8+.

Cột CSV (xem assets/prospect-list.example.csv):
    id, ten, chuc_danh, shop, san, nganh, linkedin_url,
    stage, next_action_at, last_action_at, note

Ví dụ:
    python3 outreach_queue.py --list prospect-list.csv
    python3 outreach_queue.py --list prospect-list.csv --done p001 p002
    python3 outreach_queue.py --list prospect-list.csv --set p004=booked
    python3 outreach_queue.py --list prospect-list.csv --done p001 --dry-run
"""

import argparse
import csv
import datetime as dt
import os
import sys
import tempfile

FIELDS = ["id", "ten", "chuc_danh", "shop", "san", "nganh", "linkedin_url",
          "stage", "next_action_at", "last_action_at", "note"]

# stage hiện tại -> (stage kế tiếp, số ngày chờ trước chạm kế, file tin nhắn cho chạm HIỆN TẠI)
# 'file tin nhắn' là thứ cần gửi khi prospect đang ở stage đó và đã tới hạn.
FLOW = {
    "new":          ("connect_sent",  3, "connect.txt"),
    "connected":    ("thanks_sent",   3, "thanks.txt"),
    "thanks_sent":  ("value_sent",    4, "value.txt"),
    "value_sent":   ("offer_sent",    5, "offer.txt"),
    "offer_sent":   ("followed_up",   0, "followup.txt"),
}

# Stage chờ hành động của người khác hoặc đã đóng — script không tự đẩy tiếp.
WAITING = {"connect_sent": "chờ họ chấp nhận kết nối"}
CLOSED = {"booked": "đã đặt lịch trải nghiệm",
          "no": "đã từ chối",
          "nurture": "chạm lại sau 90 ngày",
          "followed_up": "đã chạm đủ 5 lần"}

VALID_STAGES = set(FLOW) | set(WAITING) | set(CLOSED)

DEFAULT_DAILY_CONNECTS = 15
DEFAULT_DAILY_MESSAGES = 20
CONNECT_NOTE_LIMIT = 300
NURTURE_DAYS = 90


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


def read_list(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        for field in FIELDS:
            row.setdefault(field, "")
        if not (row.get("stage") or "").strip():
            row["stage"] = "new"
    return rows


def write_list(path, rows):
    """Ghi đè an toàn: file tạm cùng thư mục rồi os.replace."""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in FIELDS})
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def load_message(messages_dir, filename):
    path = os.path.join(messages_dir, filename)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().strip()


def fill(template, row):
    """Điền biến. Biến thiếu dữ liệu hiện thành [ten?] để người gửi thấy mà sửa tay."""
    out = template
    for key in ("ten", "shop", "san", "nganh"):
        value = (row.get(key) or "").strip()
        out = out.replace("{" + key + "}", value if value else "[{}?]".format(key))
    return out


def is_due(row):
    """Tới hạn khi chưa có next_action_at (người mới) hoặc ngày hẹn đã đến."""
    when = parse_date(row.get("next_action_at"))
    return when is None or when <= today()


def block(row, text, kind):
    lines = []
    label = row.get("ten") or row.get("id")
    shop = row.get("shop") or ""
    lines.append("─" * 68)
    lines.append("{}  |  {}  |  {}".format(row.get("id"), label, shop))
    if row.get("linkedin_url"):
        lines.append(row["linkedin_url"])
    if (row.get("note") or "").strip():
        lines.append("ghi chú: " + row["note"].strip())
    lines.append("")
    lines.append(text)
    if kind == "connect":
        length = len(text)
        flag = "OK" if length <= CONNECT_NOTE_LIMIT else "QUÁ DÀI, LinkedIn sẽ cắt"
        lines.append("")
        lines.append("[{} ký tự / {} — {}]".format(length, CONNECT_NOTE_LIMIT, flag))
    return "\n".join(lines)


def show_worklist(rows, messages_dir, max_connects, max_messages):
    connects, messages, attention = [], [], []

    for row in rows:
        stage = (row.get("stage") or "new").strip()
        if stage in CLOSED:
            continue
        if stage in WAITING:
            when = parse_date(row.get("next_action_at"))
            if when is not None and when <= today():
                attention.append((row, "{} — quá hạn từ {}".format(WAITING[stage], when)))
            continue
        if stage not in FLOW:
            attention.append((row, "stage không hợp lệ: {!r}".format(stage)))
            continue
        if not is_due(row):
            continue
        text = fill(load_message(messages_dir, FLOW[stage][2]), row)
        (connects if stage == "new" else messages).append((row, text))

    over_connects = max(0, len(connects) - max_connects)
    over_messages = max(0, len(messages) - max_messages)
    connects = connects[:max_connects]
    messages = messages[:max_messages]

    print("=" * 68)
    print("VIỆC OUTREACH HÔM NAY — {}".format(today()))
    print("=" * 68)

    print("\n### A. GỬI CONNECTION REQUEST ({} người)\n".format(len(connects)))
    if not connects:
        print("(không có ai — thêm người mới vào CSV với stage = new)")
    for row, text in connects:
        print(block(row, text, "connect"))
        print()
    if over_connects:
        print("[Giữ lại {} người cho ngày mai — hạn mức an toàn {}/ngày]".format(
            over_connects, max_connects))

    print("\n### B. TIN NHẮN TỚI HẠN ({} người)\n".format(len(messages)))
    if not messages:
        print("(không có tin nào tới hạn hôm nay)")
    for row, text in messages:
        print(block(row, text, "message"))
        print()
    if over_messages:
        print("[Giữ lại {} tin cho ngày mai — hạn mức an toàn {}/ngày]".format(
            over_messages, max_messages))

    print("\n### C. CẦN HENRY QUYẾT ({} người)\n".format(len(attention)))
    if not attention:
        print("(không có)")
    for row, reason in attention:
        print("  {} | {} | {}".format(row.get("id"), row.get("ten") or "-", reason))

    ids = [row.get("id") for row, _ in connects + messages]
    if ids:
        print("\n" + "─" * 68)
        print("Gửi xong thì ghi nhận lại:")
        print("  --done " + " ".join(i for i in ids if i))
    return 0


def advance(rows, ids, dry_run):
    """Đẩy prospect sang stage kế tiếp và tự hẹn ngày chạm sau."""
    index = {(row.get("id") or "").strip(): row for row in rows}
    changed = False
    for pid in ids:
        row = index.get(pid)
        if row is None:
            print("  {}: không tìm thấy trong danh sách".format(pid), file=sys.stderr)
            continue
        stage = (row.get("stage") or "new").strip()
        if stage not in FLOW:
            print("  {}: stage {!r} không tự đẩy tiếp được (dùng --set)".format(pid, stage),
                  file=sys.stderr)
            continue
        nxt, wait_days, _ = FLOW[stage]
        row["stage"] = nxt
        row["last_action_at"] = today().isoformat()
        row["next_action_at"] = (today() + dt.timedelta(days=wait_days)).isoformat()
        changed = True
        print("  {}: {} → {} (chạm kế {})".format(pid, stage, nxt, row["next_action_at"]))
    return changed


def set_stage(rows, pairs, dry_run):
    """Đặt stage thủ công, dạng id=stage."""
    index = {(row.get("id") or "").strip(): row for row in rows}
    changed = False
    for pair in pairs:
        if "=" not in pair:
            print("  {!r}: sai định dạng, cần id=stage".format(pair), file=sys.stderr)
            continue
        pid, stage = pair.split("=", 1)
        pid, stage = pid.strip(), stage.strip()
        row = index.get(pid)
        if row is None:
            print("  {}: không tìm thấy trong danh sách".format(pid), file=sys.stderr)
            continue
        if stage not in VALID_STAGES:
            print("  {}: stage {!r} không hợp lệ. Hợp lệ: {}".format(
                pid, stage, ", ".join(sorted(VALID_STAGES))), file=sys.stderr)
            continue
        row["stage"] = stage
        row["last_action_at"] = today().isoformat()
        if stage == "nurture":
            row["next_action_at"] = (today() + dt.timedelta(days=NURTURE_DAYS)).isoformat()
        elif stage in CLOSED:
            row["next_action_at"] = ""
        elif stage in FLOW:
            row["next_action_at"] = today().isoformat()
        changed = True
        print("  {}: → {}".format(pid, stage))
    return changed


def stats(rows):
    counts = {}
    for row in rows:
        stage = (row.get("stage") or "new").strip()
        counts[stage] = counts.get(stage, 0) + 1

    sent = counts.get("connect_sent", 0)
    accepted = sum(counts.get(s, 0) for s in
                   ("connected", "thanks_sent", "value_sent", "offer_sent",
                    "followed_up", "booked", "nurture"))
    booked = counts.get("booked", 0)

    print("\n" + "=" * 68)
    print("PIPELINE")
    print("=" * 68)
    for stage in ["new", "connect_sent", "connected", "thanks_sent", "value_sent",
                  "offer_sent", "followed_up", "booked", "nurture", "no"]:
        if counts.get(stage):
            print("  {:<14} {}".format(stage, counts[stage]))

    total_requests = sent + accepted
    if total_requests:
        print("\n  Tỉ lệ chấp nhận : {:.0f}%  ({}/{})".format(
            100 * accepted / total_requests, accepted, total_requests))
        if 100 * accepted / total_requests < 25:
            print("  ⚠ Dưới 25% — sửa tin nhắn chạm 1 trước khi gửi thêm.")
    if accepted:
        print("  Đặt lịch/kết nối : {:.0f}%  ({}/{})".format(
            100 * booked / accepted, booked, accepted))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Hàng đợi outreach LinkedIn — in việc cần làm hôm nay. Không tự gửi gì.")
    parser.add_argument("--list", required=True, help="Đường dẫn prospect-list.csv")
    parser.add_argument("--messages-dir",
                        help="Thư mục chứa mẫu tin nhắn (mặc định: assets/messages của skill)")
    parser.add_argument("--done", nargs="+", metavar="ID",
                        help="Đã gửi xong: đẩy các id này sang chạm kế tiếp")
    parser.add_argument("--set", nargs="+", metavar="ID=STAGE",
                        help="Đặt stage thủ công, vd p004=booked p005=no")
    parser.add_argument("--daily-connects", type=int, default=DEFAULT_DAILY_CONNECTS,
                        help="Hạn mức connection request/ngày (mặc định 15)")
    parser.add_argument("--daily-messages", type=int, default=DEFAULT_DAILY_MESSAGES,
                        help="Hạn mức tin nhắn/ngày (mặc định 20)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Xem trước thay đổi, không ghi vào CSV")
    args = parser.parse_args(argv)

    list_path = os.path.abspath(args.list)
    if not os.path.isfile(list_path):
        print("LỖI: không tìm thấy danh sách: " + list_path, file=sys.stderr)
        return 1

    messages_dir = args.messages_dir or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "messages")
    if not os.path.isdir(messages_dir):
        print("LỖI: không tìm thấy thư mục mẫu tin nhắn: " + messages_dir, file=sys.stderr)
        return 1

    rows = read_list(list_path)

    if args.done or args.set:
        changed = False
        if args.done:
            changed |= advance(rows, args.done, args.dry_run)
        if args.set:
            changed |= set_stage(rows, args.set, args.dry_run)
        if changed and not args.dry_run:
            write_list(list_path, rows)
            print("\nĐã cập nhật " + os.path.basename(list_path))
        elif args.dry_run:
            print("\n[dry-run] Không ghi vào CSV.")
        stats(rows)
        return 0

    try:
        rc = show_worklist(rows, messages_dir, args.daily_connects, args.daily_messages)
    except OSError as exc:
        print("LỖI đọc mẫu tin nhắn: {}".format(exc), file=sys.stderr)
        return 1
    stats(rows)
    return rc


if __name__ == "__main__":
    sys.exit(main())
