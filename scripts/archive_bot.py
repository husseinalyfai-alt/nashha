import json
import os
import time
from datetime import datetime, timezone

import requests

OUT = "data/heritage-images.json"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
IA_API = "https://archive.org/advancedsearch.php"

SEARCHES = [
    "Yafa Yemen historical", "Yafai Yemen historical", "Upper Yafa Yemen", "Lower Yafa Yemen",
    "Yafa Sultanate", "Yafa Yemen villages", "Yafa Yemen architecture", "Yafa Yemen map",
    "Aden Yemen old historical", "Aden old port Yemen", "Lahij Yemen historical",
    "Hadramaut historical Yemen", "Shabwa Yemen archaeological", "Socotra historical Yemen",
    "Al Mahrah Yemen historical", "Qaiti Sultanate", "Kathiri Sultanate", "Lahej Sultanate",
    "Sultanate of Yafa", "Sultanate of Lahej", "South Yemen history"
]

# Only material whose metadata indicates a reuse-friendly status is admitted.
ALLOWED_LICENSE = ("Public Domain", "CC0", "CC BY", "CC BY-SA", "No known copyright")
IA_RIGHTS = ("public domain", "cc0", "cc by", "cc by-sa", "no known copyright", "no known restrictions")


def clean(v):
    return " ".join(str(v or "").split())


def request(url, params):
    params = dict(params)
    params.update({"format": "json", "formatversion": 2})
    r = requests.get(url, params=params, timeout=30, headers={"User-Agent": "NashhalArchiveBot/2.0"})
    r.raise_for_status()
    return r.json()


def commons_license(meta):
    for key in ("LicenseShortName", "UsageTerms", "License"):
        value = meta.get(key, {})
        if isinstance(value, dict):
            value = value.get("value", "")
        if value:
            return clean(value)
    return ""


def allowed(text, choices):
    value = clean(text).lower()
    return any(x.lower() in value for x in choices)


def load_existing():
    if not os.path.exists(OUT):
        return []
    try:
        with open(OUT, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def region_for(query):
    q = query.lower()
    if "yafa" in q or "yafai" in q:
        return "يافع"
    if "qaiti" in q:
        return "القعيطي"
    if "kathiri" in q:
        return "الكثيري"
    if "lahij" in q or "lahej" in q:
        return "لحج"
    if "mahrah" in q:
        return "المهرة"
    if "aden" in q:
        return "عدن"
    return "الجنوب"


def collect_commons(seen):
    found = []
    for query in SEARCHES:
        try:
            data = request(COMMONS_API, {
                "action": "query", "generator": "search", "gsrsearch": query,
                "gsrnamespace": 6, "gsrlimit": 10, "prop": "imageinfo",
                "iiprop": "url|extmetadata", "iiurlwidth": 1400,
            })
            for page in data.get("query", {}).get("pages", []):
                pageid = page.get("pageid")
                if not pageid or f"commons:{pageid}" in seen:
                    continue
                info = (page.get("imageinfo") or [{}])[0]
                meta = info.get("extmetadata") or {}
                lic = commons_license(meta)
                if not allowed(lic, ALLOWED_LICENSE):
                    continue
                image_url = info.get("thumburl") or info.get("url")
                if not image_url:
                    continue
                title = page.get("title", "").replace("File:", "").strip()
                found.append({
                    "id": f"commons:{pageid}", "title": title,
                    "image_url": image_url, "source_url": "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_"),
                    "source": "Wikimedia Commons", "license": lic,
                    "artist": clean((meta.get("Artist") or {}).get("value", "")),
                    "description": clean((meta.get("ImageDescription") or {}).get("value", "")),
                    "region": region_for(query), "query": query,
                    "collected_at": datetime.now(timezone.utc).isoformat()
                })
                seen.add(f"commons:{pageid}")
            time.sleep(0.3)
        except Exception as exc:
            print(f"Commons search failed for {query}: {exc}")
    return found


def collect_archive_org(seen):
    found = []
    for query in SEARCHES:
        try:
            data = request(IA_API, {
                "q": f'(title:({query}) OR description:({query})) AND mediatype:texts',
                "fl[]": ["identifier", "title", "description", "date", "creator", "rights", "licenseurl", "mediatype"],
                "rows": 8, "page": 1,
                "sort[]": "downloads desc"
            })
            docs = data.get("response", {}).get("docs", [])
            for doc in docs:
                identifier = doc.get("identifier")
                if not identifier or f"ia:{identifier}" in seen:
                    continue
                rights = clean(doc.get("rights", ""))
                license_url = clean(doc.get("licenseurl", ""))
                rights_blob = f"{rights} {license_url}"
                if not allowed(rights_blob, IA_RIGHTS):
                    continue
                title = clean(doc.get("title", identifier))
                # Archive.org's item thumbnail is stable and does not expose an external image link in the UI.
                image_url = f"https://archive.org/services/img/{identifier}"
                source_url = f"https://archive.org/details/{identifier}"
                found.append({
                    "id": f"ia:{identifier}", "title": title,
                    "image_url": image_url, "source_url": source_url,
                    "source": "Internet Archive", "license": rights or "No known restrictions",
                    "artist": clean(doc.get("creator", "")),
                    "description": clean(doc.get("description", "")),
                    "year": clean(doc.get("date", "")), "region": region_for(query),
                    "query": query, "archive_identifier": identifier,
                    "text_source": source_url,
                    "collected_at": datetime.now(timezone.utc).isoformat()
                })
                seen.add(f"ia:{identifier}")
            time.sleep(0.5)
        except Exception as exc:
            print(f"Internet Archive search failed for {query}: {exc}")
    return found


def collect():
    existing = load_existing()
    seen = {x.get("id") for x in existing if x.get("id")}
    found = collect_commons(seen) + collect_archive_org(seen)
    combined = (found + existing)[:300]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"Archive items added: {len(found)}; total: {len(combined)}")


if __name__ == "__main__":
    collect()
