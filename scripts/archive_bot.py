import json
import os
import time
from datetime import datetime, timezone

import requests

OUT = "data/heritage-images.json"
API = "https://commons.wikimedia.org/w/api.php"
SEARCHES = [
    "Yafa Yemen historical",
    "Yafai Yemen historical",
    "Upper Yafa Yemen",
    "Lower Yafa Yemen",
    "Yafa Sultanate",
    "Yafa Upper Sultanate",
    "Yafa Lower Sultanate",
    "Yafai tribesmen Yemen",
    "Yafa Yemen villages",
    "Yafa Yemen architecture",
    "Yafa Yemen map",
    "Yafa al Mahjaba Yemen",
    "Yafa Ja'ar Yemen",
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
    r = requests.get(API, params=params, timeout=30, headers={"User-Agent": "NashhalArchiveBot/1.1"})
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
                "gsrlimit": 12,
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "iiurlwidth": 1200,
            })

            for page in data.get("query", {}).get("pages", []):
                pageid = page.get("pageid")
                if not pageid or pageid in seen:
                    continue

                info = (page.get("imageinfo") or [{}])[0]
                meta = info.get("extmetadata") or {}
                lic = license_text(meta)
                if not any(x.lower() in lic.lower() for x in ALLOWED_LICENSE):
                    continue

                image_url = info.get("thumburl") or info.get("url")
                if not image_url:
                    continue

                title = page.get("title", "").replace("File:", "").strip()
                item = {
                    "pageid": pageid,
                    "title": title,
                    "image_url": image_url,
                    "original_url": info.get("url", image_url),
                    "source_url": "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_"),
                    "source": "Wikimedia Commons",
                    "license": lic,
                    "artist": clean((meta.get("Artist") or {}).get("value", "")),
                    "description": clean((meta.get("ImageDescription") or {}).get("value", "")),
                    "query": query,
                    "region": "يافع" if any(k in query.lower() for k in ["yafa", "yafai"]) else "الجنوب",
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                }
                found.append(item)
                seen.add(pageid)

            time.sleep(0.4)
        except Exception as exc:
            print(f"Archive search failed for {query}: {exc}")

    combined = (found + existing)[:200]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"Archive images added: {len(found)}; total: {len(combined)}")


if __name__ == "__main__":
    collect()
