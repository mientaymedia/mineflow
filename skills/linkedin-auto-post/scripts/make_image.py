#!/usr/bin/env python3
"""Dựng ảnh 1200x1200 cho bài LinkedIn từ 5 mẫu visual trong image-playbook.md.

Render HTML rồi chụp bằng Chromium headless — không cần thư viện Python ngoài.

Mẫu (--template):
    big-number  Một con số lớn + chú thích       (V1, Pillar 1)
    contrast    Trước → Sau, hai cột              (V2, Pillar 2)
    checklist   5-7 dòng đánh số                  (V3, Pillar 3)
    flow        3-5 hộp nối bằng mũi tên          (V4, Pillar 3)
    quote       Một câu ngắn, chữ lớn             (V6, Pillar 4)

Ví dụ:
    python3 make_image.py --template big-number --out img/w1.png \
        --field number=41.000 --field caption="khách trong hệ thống POS" \
        --field highlight="0 người remarketing được"

Đặt CHROMIUM_BIN nếu Chromium nằm ở đường dẫn khác.
"""

import argparse
import html
import os
import shutil
import subprocess
import sys
import tempfile

SIZE = 1200
BRAND = {
    "dark": "#0B1F3B",
    "light": "#F5F7FA",
    "accent": "#2F6FED",
    "warn": "#E5484D",
    "on_dark": "#FFFFFF",
    "on_light": "#0B1F3B",
}
FONT_STACK = '"Be Vietnam Pro", "Inter", "Noto Sans", "DejaVu Sans", sans-serif'

CHROMIUM_CANDIDATES = [
    os.environ.get("CHROMIUM_BIN", ""),
    "/opt/pw-browsers/chromium/chrome",
    "/opt/pw-browsers/chromium",
    "chromium", "chromium-browser", "google-chrome", "chrome",
]

BASE_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:%(size)spx; height:%(size)spx; }
body {
  font-family: %(font)s;
  display:flex; flex-direction:column; justify-content:space-between;
  padding:76px 80px 84px; -webkit-font-smoothing:antialiased;
}
/* line-height rộng ở dòng đầu và cuối: DejaVu Sans có descender sâu,
   dấu tiếng Việt dễ bị cắt khi glyph tràn khỏi line box */
.brand { font-size:26px; letter-spacing:.08em; text-transform:uppercase;
         opacity:.55; font-weight:600; line-height:1.6; }
.foot  { font-size:28px; opacity:.55; line-height:1.6; }
.stack { flex:1; display:flex; flex-direction:column; justify-content:center; gap:28px; }
.eyebrow { font-size:30px; font-weight:600; opacity:.7; }
"""


def esc(text):
    return html.escape(str(text or ""))


def split_items(value):
    return [item.strip() for item in str(value or "").split(";") if item.strip()]


def t_big_number(f):
    return BRAND["dark"], BRAND["on_dark"], """
<div class="brand">{brand}</div>
<div class="stack">
  <div class="eyebrow">{caption}</div>
  <div style="font-size:230px;font-weight:800;line-height:.92;letter-spacing:-.03em">{number}</div>
  <div style="height:8px;width:160px;background:{accent};border-radius:4px;margin:8px 0"></div>
  <div style="font-size:62px;font-weight:700;line-height:1.2;color:{warn}">{highlight}</div>
</div>
<div class="foot">{footer}</div>
""".format(brand=esc(f.get("brand", "MineFlow")), caption=esc(f.get("caption", "")),
           number=esc(f.get("number", "")), highlight=esc(f.get("highlight", "")),
           footer=esc(f.get("footer", "")), accent=BRAND["accent"], warn=BRAND["warn"])


def t_contrast(f):
    """Hai cột Trước → Sau.

    Màu cột phải mặc định là accent (nghĩa là 'tốt hơn'). Khi cột phải mang
    nghĩa xấu — ví dụ teardown 'Chạy được / Hỏng' — truyền after_color=warn
    để màu không nói ngược nội dung.
    """
    palette = {"accent": BRAND["accent"], "warn": BRAND["warn"], "muted": "#6B7A90"}

    def col(title, items, color):
        lis = "".join(
            '<li style="font-size:38px;line-height:1.45;margin-bottom:18px">{}</li>'.format(esc(i))
            for i in items)
        return """
<div style="flex:1">
  <div style="font-size:34px;font-weight:700;color:{c};margin-bottom:28px;
              letter-spacing:.06em;text-transform:uppercase">{t}</div>
  <ul style="list-style:none">{l}</ul>
</div>""".format(c=color, t=esc(title), l=lis)

    after_color = palette.get(f.get("after_color", "accent"), BRAND["accent"])
    before_color = palette.get(f.get("before_color", "muted"), "#6B7A90")

    return BRAND["light"], BRAND["on_light"], """
<div class="brand">{brand}</div>
<div class="stack">
  <div style="font-size:52px;font-weight:800;line-height:1.2;margin-bottom:16px">{title}</div>
  <div style="display:flex;gap:44px;align-items:flex-start">
    {before}
    <div style="font-size:64px;color:{accent};font-weight:800;align-self:center">&rarr;</div>
    {after}
  </div>
</div>
<div class="foot">{footer}</div>
""".format(brand=esc(f.get("brand", "MineFlow")), title=esc(f.get("title", "")),
           before=col(f.get("before_title", "Trước"), split_items(f.get("before_items")), before_color),
           after=col(f.get("after_title", "Sau"), split_items(f.get("after_items")), after_color),
           footer=esc(f.get("footer", "")), accent=BRAND["accent"])


def t_checklist(f):
    items = split_items(f.get("items"))
    lis = "".join("""
<li style="display:flex;gap:26px;align-items:flex-start;margin-bottom:26px">
  <span style="flex:0 0 46px;height:46px;border:4px solid {a};border-radius:10px;
               display:flex;align-items:center;justify-content:center;
               color:{a};font-size:28px;font-weight:800;margin-top:4px">{n}</span>
  <span style="font-size:42px;line-height:1.35">{t}</span>
</li>""".format(a=BRAND["accent"], n=idx, t=esc(item)) for idx, item in enumerate(items, 1))

    return BRAND["light"], BRAND["on_light"], """
<div class="brand">{brand}</div>
<div class="stack">
  <div style="font-size:56px;font-weight:800;line-height:1.2;margin-bottom:20px">{title}</div>
  <ul style="list-style:none">{lis}</ul>
</div>
<div class="foot">{footer}</div>
""".format(brand=esc(f.get("brand", "MineFlow")), title=esc(f.get("title", "")),
           lis=lis, footer=esc(f.get("footer", "")))


def t_flow(f):
    nodes = split_items(f.get("nodes"))
    boxes = []
    for i, node in enumerate(nodes):
        if i:
            boxes.append('<div style="font-size:44px;color:{};font-weight:800">&rarr;</div>'.format(
                BRAND["accent"]))
        boxes.append("""
<div style="background:rgba(255,255,255,.08);border:3px solid rgba(255,255,255,.22);
            border-radius:18px;padding:26px 20px;flex:1;text-align:center;
            font-size:34px;font-weight:600;line-height:1.3">{}</div>""".format(esc(node)))

    target = f.get("target", "")
    target_html = """
<div style="margin-top:52px;background:{a};border-radius:22px;padding:38px;text-align:center;
            font-size:46px;font-weight:800;line-height:1.25">{t}</div>""".format(
        a=BRAND["accent"], t=esc(target)) if target else ""

    return BRAND["dark"], BRAND["on_dark"], """
<div class="brand">{brand}</div>
<div class="stack">
  <div style="font-size:54px;font-weight:800;line-height:1.2;margin-bottom:24px">{title}</div>
  <div style="display:flex;gap:20px;align-items:stretch">{boxes}</div>
  {target}
</div>
<div class="foot">{footer}</div>
""".format(brand=esc(f.get("brand", "MineFlow")), title=esc(f.get("title", "")),
           boxes="".join(boxes), target=target_html, footer=esc(f.get("footer", "")))


def t_quote(f):
    return BRAND["dark"], BRAND["on_dark"], """
<div class="brand">{brand}</div>
<div class="stack">
  <div style="font-size:120px;line-height:.6;color:{a};font-weight:800">&ldquo;</div>
  <div style="font-size:76px;font-weight:800;line-height:1.25;letter-spacing:-.02em">{q}</div>
  <div style="height:8px;width:140px;background:{a};border-radius:4px;margin-top:16px"></div>
</div>
<div class="foot" style="font-size:30px;opacity:.65">{author}</div>
""".format(brand=esc(f.get("brand", "MineFlow")), q=esc(f.get("quote", "")),
           author=esc(f.get("author", "")), a=BRAND["accent"])


TEMPLATES = {
    "big-number": t_big_number,
    "contrast": t_contrast,
    "checklist": t_checklist,
    "flow": t_flow,
    "quote": t_quote,
}


def build_html(template, fields):
    bg, fg, body = TEMPLATES[template](fields)
    css = BASE_CSS % {"size": SIZE, "font": FONT_STACK}
    return ('<!doctype html><html lang="vi"><head><meta charset="utf-8">'
            "<style>{css}\nbody{{background:{bg};color:{fg}}}</style></head>"
            "<body>{body}</body></html>").format(css=css, bg=bg, fg=fg, body=body)


def find_chromium():
    for candidate in CHROMIUM_CANDIDATES:
        if not candidate:
            continue
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    return None


def render(html_text, out_path):
    binary = find_chromium()
    if not binary:
        raise RuntimeError("Không tìm thấy Chromium. Đặt CHROMIUM_BIN trỏ tới binary.")
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, "page.html")
        with open(page, "w", encoding="utf-8") as fh:
            fh.write(html_text)
        cmd = [binary, "--headless", "--disable-gpu", "--no-sandbox",
               "--hide-scrollbars", "--force-device-scale-factor=1",
               "--window-size={0},{0}".format(SIZE),
               "--screenshot=" + out_path,
               "--user-data-dir=" + os.path.join(tmp, "profile"),
               "file://" + page]
        proc = subprocess.run(cmd, capture_output=True, timeout=120)
        if not os.path.isfile(out_path):
            raise RuntimeError("Chromium không tạo được ảnh:\n" +
                               proc.stderr.decode("utf-8", "replace")[-1500:])
    return out_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Dựng ảnh 1200x1200 cho bài LinkedIn.")
    parser.add_argument("--template", required=True, choices=sorted(TEMPLATES))
    parser.add_argument("--out", required=True, help="Đường dẫn file PNG")
    parser.add_argument("--field", action="append", default=[], metavar="KEY=VALUE",
                        help="Nội dung cho mẫu; danh sách ngăn bằng dấu ';'")
    parser.add_argument("--print-html", action="store_true", help="In HTML, không render")
    args = parser.parse_args(argv)

    fields = {}
    for item in args.field:
        if "=" not in item:
            parser.error("--field cần dạng KEY=VALUE, nhận được {!r}".format(item))
        key, value = item.split("=", 1)
        fields[key.strip()] = value

    page = build_html(args.template, fields)
    if args.print_html:
        print(page)
        return 0
    try:
        path = render(page, args.out)
    except RuntimeError as exc:
        print("LỖI: {}".format(exc), file=sys.stderr)
        return 1
    print("{}  ({:.0f} KB)".format(path, os.path.getsize(path) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
