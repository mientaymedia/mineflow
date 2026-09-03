#!/usr/bin/env python3
"""Lấy LinkedIn access token bằng OAuth 3-legged — chạy trên MÁY CỦA HENRY.

Script tự làm hết phần lằng nhằng: mở trình duyệt, hứng callback, đổi code lấy
token, lấy luôn author URN, ghi ra file .env với quyền 600.
Henry chỉ bấm "Allow" một lần trên trình duyệt.

Chuẩn bị (một lần, tại developer.linkedin.com):
  1. Create app, gắn với một LinkedIn Page mình là admin
  2. Tab Products -> request "Sign In with LinkedIn using OpenID Connect"
     và "Share on LinkedIn". Cả hai tự duyệt, không phải chờ.
  3. Tab Auth -> Authorized redirect URLs -> thêm: http://localhost:8000/callback

Chạy:
  python3 get_token.py --client-id XXX --client-secret YYY --env-file .env

  hoặc đặt sẵn biến môi trường LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET
  rồi chỉ cần: python3 get_token.py --env-file .env

CẢNH BÁO: file .env chứa token đăng bài dưới danh nghĩa của bạn.
Không commit, không dán vào chat, không gửi qua tin nhắn.
"""

import argparse
import http.server
import json
import os
import secrets
import stat
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
SCOPES = "openid profile email w_member_social"

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000
CALLBACK_PATH = "/callback"

PAGE = """<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>{title}</title><style>
body{{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:#0B1F3B;color:#fff;
display:flex;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center}}
.box{{max-width:520px;padding:40px}}h1{{font-size:28px;margin:0 0 12px}}
p{{font-size:17px;line-height:1.6;opacity:.8;margin:0}}
.ok{{color:#4ADE80}}.err{{color:#E5484D}}</style></head>
<body><div class="box"><h1 class="{cls}">{title}</h1><p>{body}</p></div></body></html>"""


class Result:
    """Kết quả callback, chia sẻ giữa thread server và thread chính."""

    def __init__(self):
        self.code = None
        self.error = None
        self.done = threading.Event()


def make_handler(expected_state, result):
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # không in log HTTP ra màn hình

        def _respond(self, status, cls, title, body):
            page = PAGE.format(cls=cls, title=title, body=body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != CALLBACK_PATH:
                self._respond(404, "err", "Không đúng đường dẫn",
                              "Chờ LinkedIn chuyển hướng về /callback.")
                return

            params = urllib.parse.parse_qs(parsed.query)
            state = (params.get("state") or [""])[0]
            code = (params.get("code") or [""])[0]
            err = (params.get("error_description") or params.get("error") or [""])[0]

            if err:
                result.error = "LinkedIn từ chối: " + err
            elif not secrets.compare_digest(state, expected_state):
                # state sai => request không phải do script này khởi tạo
                result.error = "State không khớp — huỷ để phòng CSRF."
            elif not code:
                result.error = "Callback không có 'code'."

            if result.error:
                self._respond(400, "err", "Chưa lấy được token", result.error)
            else:
                result.code = code
                self._respond(200, "ok", "Xong rồi",
                              "Đã lấy được mã uỷ quyền. Đóng tab này và quay lại cửa sổ terminal.")
            result.done.set()

    return Handler


def post_form(url, fields):
    data = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError("LinkedIn trả về {}: {}".format(exc.code, detail)) from None


def get_person_urn(token):
    req = urllib.request.Request(USERINFO_URL, headers={"Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Không gọi được /v2/userinfo: {}".format(exc.code)) from None
    sub = data.get("sub")
    if not sub:
        raise RuntimeError("userinfo không trả về 'sub'")
    return "urn:li:person:" + sub, data.get("name", "")


def write_env(path, token, urn, refresh_token):
    """Ghi .env với quyền 600 (chỉ chủ sở hữu đọc được)."""
    path = os.path.abspath(path)
    lines = [
        "# LinkedIn — sinh bởi get_token.py. KHÔNG commit file này.",
        "LINKEDIN_ACCESS_TOKEN={}".format(token),
        "LINKEDIN_AUTHOR_URN={}".format(urn),
    ]
    if refresh_token:
        lines.append("LINKEDIN_REFRESH_TOKEN={}".format(refresh_token))
    lines.append("")

    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    return path


def run(args):
    client_id = args.client_id or os.environ.get("LINKEDIN_CLIENT_ID", "")
    client_secret = args.client_secret or os.environ.get("LINKEDIN_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        print("LỖI: thiếu client id hoặc client secret.\n"
              "Dùng --client-id/--client-secret, hoặc đặt LINKEDIN_CLIENT_ID "
              "và LINKEDIN_CLIENT_SECRET.", file=sys.stderr)
        return 1

    redirect_uri = "http://{}:{}{}".format(args.host, args.port, CALLBACK_PATH)
    state = secrets.token_urlsafe(24)
    result = Result()

    try:
        server = http.server.HTTPServer((args.host, args.port), make_handler(state, result))
    except OSError as exc:
        print("LỖI: không mở được {}:{} — {}\n"
              "Cổng đang bận? Dùng --port khác, nhớ thêm URL mới vào tab Auth của app."
              .format(args.host, args.port, exc), file=sys.stderr)
        return 1

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    auth_url = AUTH_URL + "?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": SCOPES,
    })

    print("Mở trình duyệt để đăng nhập LinkedIn và bấm Allow.")
    print("Nếu trình duyệt không tự mở, dán link này:\n\n{}\n".format(auth_url))
    if not args.no_browser:
        try:
            webbrowser.open(auth_url)
        except Exception:
            pass

    print("Đang chờ callback tại {} ... (Ctrl+C để huỷ)".format(redirect_uri))
    try:
        if not result.done.wait(timeout=args.timeout):
            print("\nLỖI: hết {} giây mà chưa nhận được callback.".format(args.timeout),
                  file=sys.stderr)
            return 1
    except KeyboardInterrupt:
        print("\nĐã huỷ.", file=sys.stderr)
        return 1
    finally:
        server.shutdown()
        server.server_close()

    if result.error:
        print("LỖI: " + result.error, file=sys.stderr)
        return 1

    print("Đang đổi mã lấy token...")
    try:
        payload = post_form(TOKEN_URL, {
            "grant_type": "authorization_code",
            "code": result.code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        })
    except RuntimeError as exc:
        print("LỖI: {}".format(exc), file=sys.stderr)
        return 1

    token = payload.get("access_token")
    if not token:
        print("LỖI: phản hồi không có access_token: {}".format(payload), file=sys.stderr)
        return 1
    refresh_token = payload.get("refresh_token", "")
    expires_days = int(payload.get("expires_in", 0)) // 86400
    granted = payload.get("scope", "")

    try:
        urn, name = get_person_urn(token)
    except RuntimeError as exc:
        print("CẢNH BÁO: lấy được token nhưng không lấy được author URN — {}".format(exc),
              file=sys.stderr)
        urn, name = "", ""

    print("\n" + "=" * 60)
    print("LẤY TOKEN THÀNH CÔNG")
    print("=" * 60)
    if name:
        print("  Tài khoản   : {}".format(name))
    if urn:
        print("  Author URN  : {}".format(urn))
    print("  Token sống  : {} ngày".format(expires_days or "?"))
    print("  Refresh     : {}".format("có" if refresh_token else "KHÔNG — phải làm lại sau 60 ngày"))
    print("  Scope       : {}".format(granted))

    if "w_member_social" not in granted:
        print("\n  ⚠ Thiếu scope w_member_social — sẽ KHÔNG đăng bài được.")
        print("    Vào tab Products của app, request 'Share on LinkedIn', rồi chạy lại.")

    if args.env_file:
        path = write_env(args.env_file, token, urn, refresh_token)
        print("\n  Đã ghi: {} (quyền 600)".format(path))
        print("  KHÔNG commit file này. Kiểm tra nó nằm trong .gitignore.")
    else:
        print("\n  Không ghi file (thiếu --env-file). Đặt thủ công:")
        print("    export LINKEDIN_ACCESS_TOKEN='<token>'")
        print("    export LINKEDIN_AUTHOR_URN='{}'".format(urn))
        print("  Token không in ra màn hình để tránh lọt vào lịch sử terminal.")

    print("\nBước tiếp theo:")
    print("  set -a && source .env && set +a")
    print("  python3 run_queue.py --queue content-queue.csv --dry-run")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Lấy LinkedIn access token bằng OAuth 3-legged (chạy trên máy cá nhân).")
    parser.add_argument("--client-id", help="Client ID của app (hoặc LINKEDIN_CLIENT_ID)")
    parser.add_argument("--client-secret", help="Client Secret (hoặc LINKEDIN_CLIENT_SECRET)")
    parser.add_argument("--env-file", help="Ghi token ra file này với quyền 600, vd .env")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--timeout", type=int, default=300, help="Giây chờ callback (mặc định 300)")
    parser.add_argument("--no-browser", action="store_true", help="Không tự mở trình duyệt")
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
