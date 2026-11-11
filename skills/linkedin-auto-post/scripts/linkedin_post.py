#!/usr/bin/env python3
"""Đăng bài lên LinkedIn (text / 1 ảnh / nhiều ảnh) qua Versioned API.

Chỉ dùng thư viện chuẩn của Python 3.8+, không cần cài gì thêm.

Biến môi trường:
    LINKEDIN_ACCESS_TOKEN   (bắt buộc) access token 3-legged OAuth
    LINKEDIN_AUTHOR_URN     (tuỳ chọn) vd urn:li:person:xxx hoặc urn:li:organization:123
                            bỏ trống -> tự lấy person URN từ /v2/userinfo
    LINKEDIN_API_VERSION    (tuỳ chọn) mặc định 202604

Ví dụ:
    python3 linkedin_post.py --text-file bai-001.txt --image anh.png \
        --alt-text "Biểu đồ tỉ lệ khách quay lại" --dry-run
"""

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.linkedin.com"
DEFAULT_VERSION = "202604"

# Ký tự phải escape trong trường "commentary" (định dạng little text của LinkedIn).
# '#' xử lý riêng để giữ được hashtag.
RESERVED = set("|{}@[]()<>*_~\\")

MAX_IMAGES = 9
MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}


class LinkedInError(RuntimeError):
    """Lỗi trả về từ LinkedIn API, kèm status và body để chẩn đoán."""

    def __init__(self, status, body, url):
        self.status = status
        self.body = body
        super().__init__("LinkedIn API {} tại {}: {}".format(status, url, body))


def escape_commentary(text):
    """Escape ký tự đặc biệt cho trường commentary, giữ nguyên hashtag.

    '#' chỉ được giữ nguyên khi ngay sau nó là chữ/số (tức là một hashtag);
    mọi trường hợp khác đều escape để tránh lỗi 422.
    """
    out = []
    for i, ch in enumerate(text):
        if ch in RESERVED:
            out.append("\\" + ch)
        elif ch == "#":
            nxt = text[i + 1] if i + 1 < len(text) else ""
            out.append("#" if nxt.isalnum() else "\\#")
        else:
            out.append(ch)
    return "".join(out)


def _request(method, url, token, version, body=None, content_type="application/json",
             raw=False, timeout=60):
    """Gửi một request tới LinkedIn và trả về (status, headers, parsed_body)."""
    headers = {
        "Authorization": "Bearer " + token,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    if version:
        headers["LinkedIn-Version"] = version

    data = None
    if body is not None:
        if raw:
            data = body
        else:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = content_type

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read()
            parsed = None
            if payload:
                try:
                    parsed = json.loads(payload.decode("utf-8"))
                except (ValueError, UnicodeDecodeError):
                    parsed = payload
            return resp.status, dict(resp.headers), parsed
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise LinkedInError(exc.code, detail, url) from None


def get_person_urn(token):
    """Lấy author URN của chính chủ token qua OpenID userinfo."""
    # /v2/userinfo là endpoint cũ, không nhận header LinkedIn-Version.
    _, _, data = _request("GET", API_BASE + "/v2/userinfo", token, version=None)
    sub = (data or {}).get("sub")
    if not sub:
        raise LinkedInError(200, "userinfo không trả về 'sub': {}".format(data),
                            API_BASE + "/v2/userinfo")
    return "urn:li:person:" + sub


def _check_image(path):
    if not os.path.isfile(path):
        raise FileNotFoundError("Không tìm thấy ảnh: " + path)
    size = os.path.getsize(path)
    if size == 0:
        raise ValueError("Ảnh rỗng: " + path)
    if size > MAX_IMAGE_BYTES:
        raise ValueError("Ảnh {} nặng {:.1f} MB, vượt giới hạn 10 MB".format(
            path, size / 1024 / 1024))
    guessed, _ = mimetypes.guess_type(path)
    if guessed and guessed not in ALLOWED_IMAGE_TYPES:
        raise ValueError("Định dạng {} không được LinkedIn chấp nhận ({})".format(
            guessed, ", ".join(sorted(ALLOWED_IMAGE_TYPES))))


def upload_image(token, author_urn, path, version=DEFAULT_VERSION):
    """Upload một ảnh, trả về image URN.

    initializeUpload và PUT phải chạy liền nhau: uploadUrl có hạn dùng ngắn.
    """
    _check_image(path)

    url = API_BASE + "/rest/images?action=initializeUpload"
    _, _, data = _request("POST", url, token, version,
                          body={"initializeUploadRequest": {"owner": author_urn}})
    value = (data or {}).get("value") or {}
    upload_url = value.get("uploadUrl")
    image_urn = value.get("image")
    if not upload_url or not image_urn:
        raise LinkedInError(200, "initializeUpload thiếu uploadUrl/image: {}".format(data), url)

    with open(path, "rb") as fh:
        blob = fh.read()
    _request("PUT", upload_url, token, version=None, body=blob,
             content_type="application/octet-stream", raw=True, timeout=180)
    return image_urn


def build_post_body(author_urn, text, media=None, visibility="PUBLIC"):
    """Dựng JSON body cho POST /rest/posts.

    media: None | {"id": urn, "altText": str} | list các dict như trên.
    """
    body = {
        "author": author_urn,
        "commentary": escape_commentary(text),
        "visibility": visibility,
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    if isinstance(media, list) and len(media) > 1:
        body["content"] = {"multiImage": {"images": media}}
    elif isinstance(media, list) and media:
        body["content"] = {"media": media[0]}
    elif isinstance(media, dict):
        body["content"] = {"media": media}
    return body


def create_post(token, body, version=DEFAULT_VERSION):
    """Tạo bài viết, trả về URN của bài (header x-restli-id)."""
    url = API_BASE + "/rest/posts"
    _, headers, _ = _request("POST", url, token, version, body=body)
    lowered = {k.lower(): v for k, v in headers.items()}
    return lowered.get("x-restli-id") or lowered.get("x-linkedin-id") or ""


def publish(token, text, images=None, alt_texts=None, author_urn=None,
            visibility="PUBLIC", version=DEFAULT_VERSION, dry_run=False):
    """Đăng một bài hoàn chỉnh. Trả về URN bài viết ('' nếu dry-run)."""
    images = list(images or [])
    alt_texts = list(alt_texts or [])
    if len(images) > MAX_IMAGES:
        raise ValueError("Tối đa {} ảnh mỗi bài, đang có {}".format(MAX_IMAGES, len(images)))
    if not text.strip():
        raise ValueError("Nội dung bài viết rỗng")

    for path in images:
        _check_image(path)

    if not author_urn:
        author_urn = os.environ.get("LINKEDIN_AUTHOR_URN") or ""
    if not author_urn:
        if dry_run:
            author_urn = "urn:li:person:DRY_RUN"
        else:
            author_urn = get_person_urn(token)

    media = []
    for idx, path in enumerate(images):
        alt = alt_texts[idx] if idx < len(alt_texts) else os.path.basename(path)
        if dry_run:
            media.append({"id": "urn:li:image:DRY_RUN_{}".format(idx), "altText": alt})
        else:
            media.append({"id": upload_image(token, author_urn, path, version),
                          "altText": alt})
            time.sleep(2)  # nhịp an toàn giữa các request

    body = build_post_body(author_urn, text, media or None, visibility)

    if dry_run:
        print(json.dumps(body, ensure_ascii=False, indent=2))
        print("\n[dry-run] Không gửi request nào tới LinkedIn.", file=sys.stderr)
        return ""

    return create_post(token, body, version)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Đăng bài lên LinkedIn (text + ảnh).")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Nội dung bài viết")
    src.add_argument("--text-file", help="File .txt chứa nội dung bài viết (UTF-8)")
    parser.add_argument("--image", action="append", default=[],
                        help="Đường dẫn ảnh, lặp lại tối đa 9 lần")
    parser.add_argument("--alt-text", action="append", default=[],
                        help="Alt text tương ứng theo thứ tự --image")
    parser.add_argument("--author-urn", help="Ghi đè LINKEDIN_AUTHOR_URN")
    parser.add_argument("--visibility", default="PUBLIC",
                        choices=["PUBLIC", "CONNECTIONS", "LOGGED_IN"])
    parser.add_argument("--api-version",
                        default=os.environ.get("LINKEDIN_API_VERSION", DEFAULT_VERSION))
    parser.add_argument("--dry-run", action="store_true",
                        help="In payload ra màn hình, không gọi API")
    args = parser.parse_args(argv)

    token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    if not token and not args.dry_run:
        parser.error("Thiếu biến môi trường LINKEDIN_ACCESS_TOKEN")

    if args.text_file:
        with open(args.text_file, "r", encoding="utf-8") as fh:
            text = fh.read().strip()
    else:
        text = args.text

    try:
        urn = publish(token, text, args.image, args.alt_text, args.author_urn,
                      args.visibility, args.api_version, args.dry_run)
    except (LinkedInError, ValueError, FileNotFoundError) as exc:
        print("LỖI: {}".format(exc), file=sys.stderr)
        return 1

    if urn:
        print(urn)
    return 0


if __name__ == "__main__":
    sys.exit(main())
