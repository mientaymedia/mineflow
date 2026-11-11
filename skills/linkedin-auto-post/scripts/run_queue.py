#!/usr/bin/env python3
"""Chạy hàng đợi nội dung LinkedIn: đăng những bài đã tới hạn và ghi kết quả ngược vào CSV.

Chỉ dùng thư viện chuẩn Python 3.8+.

Cột CSV (xem assets/content-queue.example.csv):
    id           mã bài, duy nhất
    publish_at   thời điểm đăng, dạng 'YYYY-MM-DD HH:MM' theo giờ địa phương (mặc định UTC+7)
    status       draft | ready | posted | error | skipped   (chỉ 'ready' mới được đăng)
    text_file    đường dẫn file .txt chứa nội dung
    image        đường dẫn ảnh; nhiều ảnh ngăn bằng dấu ';'
    alt_text     alt text theo thứ tự ảnh; ngăn bằng dấu ';'
    visibility   PUBLIC | CONNECTIONS | LOGGED_IN  (rỗng = PUBLIC)
    post_urn     script ghi vào sau khi đăng thành công
    posted_at    script ghi vào (UTC ISO 8601)
    note         script ghi thông báo lỗi vào đây

Ví dụ:
    python3 run_queue.py --queue content-queue.csv --dry-run
    python3 run_queue.py --queue content-queue.csv --limit 1
"""

import argparse
import csv
import datetime as dt
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from linkedin_post import DEFAULT_VERSION, LinkedInError, publish  # noqa: E402
from lint_posts import check as lint_check  # noqa: E402

FIELDS = ["id", "publish_at", "status", "text_file", "image", "alt_text",
          "visibility", "post_urn", "posted_at", "note"]

TIME_FORMATS = ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")


def parse_publish_at(value, tz_offset_hours):
    """Đổi 'YYYY-MM-DD HH:MM' theo giờ địa phương thành datetime UTC (naive)."""
    value = (value or "").strip()
    if not value:
        raise ValueError("publish_at rỗng")
    for fmt in TIME_FORMATS:
        try:
            local = dt.datetime.strptime(value, fmt)
            return local - dt.timedelta(hours=tz_offset_hours)
        except ValueError:
            continue
    raise ValueError("publish_at không đọc được: {!r} (cần 'YYYY-MM-DD HH:MM')".format(value))


def split_list(value):
    return [item.strip() for item in (value or "").split(";") if item.strip()]


def read_queue(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        for field in FIELDS:
            row.setdefault(field, "")
    return rows


def write_queue(path, rows):
    """Ghi đè CSV một cách an toàn: ghi file tạm cùng thư mục rồi thay thế."""
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


def resolve(path, base_dir):
    """Đường dẫn trong CSV được hiểu là tương đối so với thư mục chứa CSV."""
    if not path:
        return path
    return path if os.path.isabs(path) else os.path.join(base_dir, path)


def due_rows(rows, now_utc, tz_offset):
    """Trả về (index, row, lỗi) cho các dòng status=ready đã tới hạn.

    Bài tới hạn sớm nhất đứng trước; các dòng có publish_at hỏng xếp cuối
    (chúng chỉ được báo lỗi, không chiếm suất --limit).
    """
    ready = []
    broken = []
    for idx, row in enumerate(rows):
        if (row.get("status") or "").strip().lower() != "ready":
            continue
        try:
            when = parse_publish_at(row.get("publish_at"), tz_offset)
        except ValueError as exc:
            broken.append((idx, row, str(exc)))
            continue
        if when <= now_utc:
            ready.append((when, idx, row))
    ready.sort(key=lambda item: (item[0], item[1]))
    return [(idx, row, None) for _, idx, row in ready] + broken


def run(args):
    queue_path = os.path.abspath(args.queue)
    base_dir = os.path.dirname(queue_path)
    if not os.path.isfile(queue_path):
        print("LỖI: không tìm thấy file hàng đợi: " + queue_path, file=sys.stderr)
        return 1
    rows = read_queue(queue_path)
    now_utc = dt.datetime.utcnow()

    pending = due_rows(rows, now_utc, args.tz_offset)
    if not pending:
        print("Không có bài nào tới hạn.")
        return 0

    token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    if not token and not args.dry_run:
        print("LỖI: thiếu biến môi trường LINKEDIN_ACCESS_TOKEN", file=sys.stderr)
        return 1

    author_urn = args.author_urn or os.environ.get("LINKEDIN_AUTHOR_URN") or ""
    changed = False
    published = 0
    failed = 0

    for idx, row, parse_error in pending:
        if published >= args.limit:
            break
        post_id = row.get("id") or "dòng {}".format(idx + 2)

        if parse_error:
            if not args.dry_run:
                row["status"] = "error"
                row["note"] = parse_error
                changed = True
            failed += 1
            print("[{}] LỖI: {}".format(post_id, parse_error), file=sys.stderr)
            continue

        try:
            text_path = resolve(row.get("text_file"), base_dir)
            if not text_path:
                raise ValueError("thiếu text_file")
            with open(text_path, "r", encoding="utf-8") as fh:
                text = fh.read().strip()

            # Chốt an toàn cuối: bài còn lỗi lint thì không lên feed, kể cả khi
            # status đã là 'ready'. Bắt được cả trường hợp đổi status nhầm cho
            # một bài mới chỉ là khung chờ nguyên liệu.
            if not args.skip_lint:
                lint_errors, _, _ = lint_check(text_path)
                if lint_errors:
                    raise ValueError("lint chặn: " + "; ".join(lint_errors))

            images = [resolve(p, base_dir) for p in split_list(row.get("image"))]
            alts = split_list(row.get("alt_text"))
            if images and len(alts) != len(images):
                raise ValueError("số alt_text ({}) không khớp số ảnh ({})".format(
                    len(alts), len(images)))

            visibility = (row.get("visibility") or "PUBLIC").strip().upper() or "PUBLIC"

            urn = publish(token, text, images, alts, author_urn, visibility,
                          args.api_version, args.dry_run)
        except (LinkedInError, ValueError, OSError) as exc:
            if not args.dry_run:
                row["status"] = "error"
                row["note"] = str(exc)[:500]
                changed = True
            failed += 1
            print("[{}] LỖI: {}".format(post_id, exc), file=sys.stderr)
            continue

        published += 1
        if args.dry_run:
            print("[{}] dry-run OK — chưa đăng, không đổi status.".format(post_id))
            continue

        row["status"] = "posted"
        row["post_urn"] = urn
        row["posted_at"] = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        row["note"] = ""
        changed = True
        print("[{}] đã đăng: {}".format(post_id, urn or "(không có URN trả về)"))

    if changed and not args.dry_run:
        write_queue(queue_path, rows)

    print("Xong: {} bài đăng, {} lỗi.".format(published, failed))
    return 1 if failed else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Đăng các bài LinkedIn đã tới hạn trong hàng đợi CSV.")
    parser.add_argument("--queue", required=True, help="Đường dẫn file CSV hàng đợi")
    parser.add_argument("--limit", type=int, default=1,
                        help="Số bài tối đa mỗi lần chạy (mặc định 1)")
    parser.add_argument("--tz-offset", type=float, default=7.0,
                        help="Chênh lệch giờ của publish_at so với UTC (mặc định 7 = giờ VN)")
    parser.add_argument("--author-urn", help="Ghi đè LINKEDIN_AUTHOR_URN")
    parser.add_argument("--api-version",
                        default=os.environ.get("LINKEDIN_API_VERSION", DEFAULT_VERSION))
    parser.add_argument("--skip-lint", action="store_true",
                        help="Bỏ qua kiểm tra lint trước khi đăng (không khuyến khích)")
    parser.add_argument("--dry-run", action="store_true",
                        help="In payload, không gọi API, không sửa CSV")
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
