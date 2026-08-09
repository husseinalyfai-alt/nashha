import json
import os
import re
import time
from datetime import datetime, timezone

import requests

OUT = "data/heritage-images.json"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
IA_API = "https://archive.org/advancedsearch.php"

SEARCHES = [
    ("يافع", ["Yafa Yemen", "Upper Yafa", "Lower Yafa", "Yafa Sultanate", "Yafa Yemen history"]),
    ("لحج", ["Lahej Sultanate", "Lahij Yemen", "Lahj Yemen history"]),
    ("القعيطي", ["Qaiti Sultanate", "Quaiti State", "Al Mukalla Qaiti"]),
    ("الكثيري", ["Kathiri Sultanate", "Kathiri State", "Seiyun Kathiri"]),
    ("المهرة", ["Mahra Sultanate", "Al Mahrah Yemen history"]),
    ("سقطرى", ["Socotra Yemen history", "Socotra historical"]),
    ("شبوة", ["Shabwa Yemen history", "Shabwa archaeology"]),
    ("عدن", ["Aden Yemen history", "Old Aden", "Aden Protectorate"]),
    ("الضالع", ["Dhala Yemen history", "Ad Dali Yemen"]),
    ("الواحدي", ["Wahidi Sultanate", "Wahidi Balhaf"]),
    ("الجنوب", ["South Yemen history", "Aden Protectorate", "South Arabia history"]),
]

ALLOWED_LICENSE = ("public domain", "cc0", "cc by", "cc by-sa", "no known copyright", "no known restrictions")
HEADERS = {
    "User-Agent": "NashhalArchiveBot/3.0 (historical archive for Nashhal; contact via GitHub repository)"
}


def clean(v):
    if isinstance(v, list):
        v = " ".join(str(x) for x in v)
    return " ".join(str(v or "").split())


def request_json(url, params, retries=4):
    params = dict(params)
    params.setdefault("format", "json")
    params.setdefault("formatversion", 2)
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=45, headers=HEADERS)
            if r.status_code in (429, 500, 502, 503, 504):
                last = f"HTTP {r.status_code}"
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as exc:
            last = str(exc)
            time.sleep(2 ** attempt)
    raise RuntimeError(last or "invalid response")


def load_existing():
    if not os.path.exists(OUT):
        return []
    try:
        with open(OUT, "r", encoding="utf-8") as f:
            value = json.load(f)
            return value if isinstance(value, list) else []
    except Exception:
        return []


def license_ok(text):
    value = clean(text).lower()
    return any(x in value for x in ALLOWED_LICENSE)


def relevance_ok(title, description, terms):
    blob = clean(f"{title} {description}").lower()
    # Require at least one strong geographical/historical term. This prevents
    # names such as Yafai/Yahia from pulling unrelated modern documents.
    strong = [t.lower() for t in terms]
    if not any(t in blob for t in strong):
        return False
    blocked = ("guantanamo", "saudi–iranian rivalry", "saudi-iranian rivalry", "detainee", "terrorism")
    return not any(x in blob for x in blocked)


def commons_license(meta):
    for key in ("LicenseShortName", "UsageTerms", "License"):
        value = meta.get(key, {})
        if isinstance(value, dict):
            value = value.get("value", "")
        if value:
            return clean(value)
    return ""


def collect_commons(seen):
    found = []
    for region, queries in SEARCHES:
        for query in queries:
            try:
                data = request_json(COMMONS_API, {
                    "action": "query", "generator": "search", "gsrsearch": query,
                    "gsrnamespace": 6, "gsrlimit": 8, "prop": "imageinfo",
                    "iiprop": "url|extmetadata", "iiurlwidth": 1400,
                })
                for page in data.get("query", {}).get("pages", []):
                    pageid = page.get("pageid")
                    item_id = f"commons:{pageid}"
                    if not pageid or item_id in seen:
                        continue
                    info = (page.get("imageinfo") or [{}])[0]
                    meta = info.get("extmetadata") or {}
                    title = clean(page.get("title", "").replace("File:", ""))
                    description = clean((meta.get("ImageDescription") or {}).get("value", ""))
                    lic = commons_license(meta)
                    if not license_ok(lic) or not relevance_ok(title, description, query.split()):
                        continue
                    image_url = info.get("thumburl") or info.get("url")
                    if not image_url:
                        continue
                    found.append({
                        "id": item_id, "title": title, "image_url": image_url,
                        "source_url": "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_"),
                        "source": "Wikimedia Commons", "license": lic,
                        "artist": clean((meta.get("Artist") or {}).get("value", "")),
                        "description": description, "region": region, "query": query,
                        "collected_at": datetime.now(timezone.utc).isoformat()
                    })
                    seen.add(item_id)
                time.sleep(1.0)
            except Exception as exc:
                print(f"Commons search failed for {query}: {exc}")
    return found


def collect_archive_org(seen):
    found = []
    for region, queries in SEARCHES:
        for query in queries:
            try:
                # Search the item metadata first; Archive.org can return HTML
                # during throttling, so request_json retries before giving up.
                data = request_json(IA_API, {
                    "q": f'(title:"{query}" OR description:"{query}" OR subject:"{query}") AND mediatype:(texts OR image)',
                    "fl[]": ["identifier", "title", "description", "date", "creator", "rights", "licenseurl", "mediatype", "subject"],
                    "rows": 6, "page": 1, "sort[]": "downloads desc",
                })
                docs = data.get("response", {}).get("docs", [])
                for doc in docs:
                    identifier = clean(doc.get("identifier"))
                    item_id = f"ia:{identifier}"
                    if not identifier or item_id in seen:
                        continue
                    title = clean(doc.get("title", identifier))
                    description = clean(doc.get("description", ""))
                    subject = clean(doc.get("subject", ""))
                    if not relevance_ok(title, f"{description} {subject}", query.split()):
                        continue
                    rights = clean(doc.get("rights", ""))
                    license_url = clean(doc.get("licenseurl", ""))
                    if not license_ok(f"{rights} {license_url}"):
                        continue
                    found.append({
                        "id": item_id, "title": title,
                        "image_url": f"https://archive.org/services/img/{identifier}",
                        "source_url": f"https://archive.org/details/{identifier}",
                        "source": "Internet Archive", "license": rights or "No known restrictions",
                        "artist": clean(doc.get("creator", "")),
                        "description": description, "year": clean(doc.get("date", "")),
                        "region": region, "query": query, "archive_identifier": identifier,
                        "text_source": f"https://archive.org/details/{identifier}",
                        "collected_at": datetime.now(timezone.utc).isoformat()
                    })
                    seen.add(item_id)
                time.sleep(1.0)
            except Exception as exc:
                print(f"Internet Archive search failed for {query}: {exc}")
    return found


def collect():
    existing = load_existing()
    seen = {x.get("id") for x in existing if x.get("id")}
    found = collect_commons(seen) + collect_archive_org(seen)
    combined = (found + existing)[:500]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"Archive items added: {len(found)}; total: {len(combined)}")


if __name__ == "__main__":
    collect()
