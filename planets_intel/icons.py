"""Turn icon URLs into data URIs for the HTML file."""

import base64
import json
import urllib.error
import urllib.request


def embed_icons(report: dict) -> dict:
    """Return a copy whose icon fields are data URIs, or null when a fetch fails."""
    copied = json.loads(json.dumps(report))
    cache: dict[str, str | None] = {}
    for player in copied["players"]:
        for kind in ("hulls", "advantages"):
            for item in player[kind]:
                url = item.get("icon")
                if not isinstance(url, str) or not url:
                    item["icon"] = None
                    continue
                if url not in cache:
                    cache[url] = _data_uri(url)
                item["icon"] = cache[url]
    return copied


def _data_uri(url: str) -> str | None:
    request = urllib.request.Request(url, headers={"User-Agent": "planets-intel"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
            content_type = response.headers.get("Content-Type", "")
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
    if not payload or not content_type.startswith("image/"):
        return None
    mime = content_type.split(";", 1)[0].strip()
    encoded = base64.standard_b64encode(payload).decode("ascii")
    return f"data:{mime};base64,{encoded}"
