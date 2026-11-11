#!/usr/bin/env python3
"""Kiểm tra bài viết LinkedIn theo checklist trong post-templates.md.

Chạy trước khi đổi status sang 'ready'. Bắt những lỗi máy kiểm được;
năm lỗi còn lại (số bịa, ví dụ bịa, lộ dữ liệu khách, sai giọng, sai mệnh đề)
vẫn phải người đọc — xem ai-operating-model.md mục 3.

    python3 lint_posts.py drafts/*.txt
    python3 lint_posts.py --queue content-queue.csv
"""

import argparse
import csv
import glob
import os
import re
import sys

MIN_CHARS, MAX_CHARS = 900, 1500
HOOK_LIMIT = 200
MAX_HASHTAGS = 3
MAX_EMOJI = 3

URL_RE = re.compile(r"https?://\S+")
HASHTAG_RE = re.compile(r"(?<!\w)#\w+")
# Đếm emoji trang trí. Các ký hiệu dùng làm bullet có cấu trúc (✔ ✘ ✓ ✗ → ⇒ •)
# phục vụ nội dung chứ không phải trang trí, nên không tính vào hạn mức emoji.
STRUCTURAL = set("\u2714\u2718\u2713\u2717\u2192\u21d2\u2022")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")

PLACEHOLDER_RE = re.compile(r"\[\[.*?\]\]|\{\{.*?\}\}|\[HENRY|TODO|XXX", re.IGNORECASE)


def check(path):
    """Trả về (errors, warnings, stats). errors chặn đăng, warnings chỉ nhắc."""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read().strip()

    errors, warnings = [], []
    chars = len(text)
    lines = text.split("\n")
    hook = lines[0] if lines else ""
    hashtags = HASHTAG_RE.findall(text)

    if not text:
        return ["file rỗng"], [], {"chars": 0}

    if PLACEHOLDER_RE.search(text):
        errors.append("còn placeholder chưa điền — bài chưa viết xong")

    if chars < MIN_CHARS:
        warnings.append("ngắn: {} ký tự (khuyến nghị {}-{})".format(chars, MIN_CHARS, MAX_CHARS))
    elif chars > MAX_CHARS:
        warnings.append("dài: {} ký tự (khuyến nghị {}-{})".format(chars, MIN_CHARS, MAX_CHARS))

    if len(hook) > HOOK_LIMIT:
        errors.append("hook {} ký tự, vượt {} — LinkedIn cắt trên mobile".format(
            len(hook), HOOK_LIMIT))
    if hook.startswith("#"):
        errors.append("hook bắt đầu bằng hashtag — mất tác dụng ba dòng đầu")

    if len(hashtags) > MAX_HASHTAGS:
        errors.append("{} hashtag, tối đa {}".format(len(hashtags), MAX_HASHTAGS))
    elif not hashtags:
        warnings.append("không có hashtag nào")

    # Link ngoài trong body làm giảm reach — phải để ở comment đầu tiên
    for url in URL_RE.findall(text):
        errors.append("có link ngoài trong body ({}) — chuyển xuống comment đầu tiên".format(
            url[:48]))

    emojis = [e for e in EMOJI_RE.findall(text) if e not in STRUCTURAL]
    if len(emojis) > MAX_EMOJI:
        warnings.append("{} emoji, tối đa {} cho nội dung B2B".format(len(emojis), MAX_EMOJI))

    # Đoạn quá dài khó đọc trên mobile
    for i, para in enumerate(text.split("\n\n"), 1):
        if len(para) > 300 and "\n" not in para:
            warnings.append("đoạn {} dài {} ký tự không xuống dòng — khó đọc trên mobile".format(
                i, len(para)))

    return errors, warnings, {"chars": chars, "hook": len(hook), "hashtags": len(hashtags)}


def paths_from_queue(queue_path):
    base = os.path.dirname(os.path.abspath(queue_path))
    out = []
    with open(queue_path, "r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if (row.get("status") or "").strip().lower() in ("posted", "skipped"):
                continue
            rel = (row.get("text_file") or "").strip()
            if rel:
                out.append(rel if os.path.isabs(rel) else os.path.join(base, rel))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="Kiểm tra bài viết LinkedIn trước khi đăng.")
    parser.add_argument("files", nargs="*", help="Các file .txt cần kiểm tra")
    parser.add_argument("--queue", help="Lấy danh sách file từ hàng đợi CSV")
    args = parser.parse_args(argv)

    paths = []
    if args.queue:
        paths += paths_from_queue(args.queue)
    for pattern in args.files:
        paths += sorted(glob.glob(pattern)) or [pattern]
    if not paths:
        parser.error("cần ít nhất một file, hoặc --queue")

    total_err = total_warn = 0
    print("{:<46} {:>6} {:>5} {:>3}  {}".format("file", "ký tự", "hook", "#", "kết quả"))
    print("-" * 84)

    for path in paths:
        name = os.path.basename(path)
        if not os.path.isfile(path):
            print("{:<46} {:>6} {:>5} {:>3}  KHÔNG TÌM THẤY".format(name, "-", "-", "-"))
            total_err += 1
            continue
        errors, warnings, st = check(path)
        total_err += len(errors)
        total_warn += len(warnings)
        verdict = "LỖI" if errors else ("nhắc" if warnings else "OK")
        print("{:<46} {:>6} {:>5} {:>3}  {}".format(
            name[:46], st.get("chars", 0), st.get("hook", 0), st.get("hashtags", 0), verdict))
        for msg in errors:
            print("      LỖI  {}".format(msg))
        for msg in warnings:
            print("      nhắc {}".format(msg))

    print("-" * 84)
    print("{} lỗi, {} nhắc trên {} file.".format(total_err, total_warn, len(paths)))
    if total_err:
        print("Sửa hết LỖI trước khi đổi status sang ready.")
    print("\nNăm điều máy không kiểm được — Henry vẫn phải đọc:")
    print("  1. Số liệu có nguồn thật?   2. Ví dụ là chuyện thật?   3. Không lộ dữ liệu khách?")
    print("  4. Đúng giọng Henry?        5. Phục vụ mệnh đề nào?")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
