import json
import os
import time
from datetime import datetime, timezone
from urllib.parse import urlencode

import requests

OUT = "data/heritage-images.json"
API = "https://commons.wikimedia.org/w/api.php"
SEARCHES = [
    "Aden Yemen old historical",
    "Aden old port Yemen",
    "Lahij Yemen historical",
    "Hadramaut historical Yemen",
    "Shabwa Yemen archaeological",
    "Socotra historical Yemen",
    "Al Mahrah Yemen historical",
    "Qaiti Sultanate",
    "Kathiri Sultanate",
    "Lahej Sultanate"
]
ALLOWED_LICENSE = ("Public Domain", "CC0", "CC BY", "CC BY-SA")


def clean(v):
    return " ".join(str(v or "").split())


def request(params):
    params.update({"format": "json", "formatversion": 2})
    r = requests.get(API, params=params, timeout=30, headers={"User-Agent": "NashhalArchiveBot/1.0"})
    r.raise_for_status()
    return r.json()


def license_text(meta):
    for key in ("LicenseShortName", "UsageTerms", "License"):
        value = meta.get(key, {})
        if isinstance(value, dict):
            value = value.get("value", "")
        if value:
            return clean(value)
    return ""


def collect():
    existing = []
    if os.path.exists(OUT):
        try:
            with open(OUT, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []
    seen = {x.get("pageid") for x in existing}
    found = []

    for query in SEARCHES:
        try:
            data = request({
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": 6,
                "gsrlimit": 8,
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "iiurlwidth": 1000,
            })
            for page in data.get("query", {}).get("pages", []):
                if page.get("pageid") in seen:
                    continue
                info = (page.get("imageinfo") or [{}])[0]
                meta = info.get("extmetadata") or {}
                lic = license_text(meta)
                if not any(x.lower() in lic.lower() for x in ALLOWED_LICENSE):
                    continue
                thumb = info.get("thumburl") or info.get("url")
                if not thumb:
                    continue
                item = {
                    "pageid": page.get("pageid"),
                    "title": page.get("title", "").replace("File:", ""),
                    "image_url": thumb,
                    "original_url": info.get("url", thumb),
                    "source_url": "https://commons.wikimedia.org/wiki/" + (page.get("title", "").replace(" ", "_")),
                    "source": "Wikimedia Commons",
                    "license": lic,
                    "artist": clean((meta.get("Artist") or {}).get("value", "")),
                    "description": clean((meta.get("ImageDescription") or {}).get("value", "")),
                    "query": query,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                }
                found.append(item)
                seen.add(page.get("pageid"))
            time.sleep(0.4)
        except Exception as exc:
            print(f"Archive search failed for {query}: {exc}")

    combined = (found + existing)[:120]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"Archive images added: {len(found)}; total: {len(combined)}")


if __name__ == "__main__":
    collect()
