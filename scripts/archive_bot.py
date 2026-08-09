import json
import os
import re
import time
from datetime import datetime, timezone

import requests

OUT = "data/heritage-images.json"
SOURCES_OUT = "data/historical-sources.json"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
IA_API = "https://archive.org/advancedsearch.php"
IA_META = "https://archive.org/metadata/"

# Regions and historical entities. Queries are deliberately broad enough to
# catch books, reports, maps and archival descriptions without treating search
# results as facts until the source itself is inspected.
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

# Historical-event searches. These are for documentary indexing only; the bot
# does not generate operational military guidance or tactical instructions.
EVENT_QUERIES = [
    "Aden Protectorate tribal resistance British Yemen",
    "South Arabia British expeditions Yemen tribes",
    "Yafa British expedition Yemen",
    "Upper Yafa British relations conflict",
    "Lower Yafa British relations conflict",
    "Lahej British occupation history",
    "Dhala British campaign history",
    "Wahidi Balhaf British history",
    "Hadramaut British political history",
    "Mahra British protectorate history",
    "Aden British occupation 1839 history",
    "Yemen South Arabia British treaties tribes history",
    "عدن الاحتلال البريطاني تاريخ القبائل",
    "يافع الانجليز تاريخ المقاومة",
    "لحج الاحتلال البريطاني تاريخ",
    "الضالع الاحتلال البريطاني تاريخ",
    "حضرموت البريطاني تاريخ السلطنات",
    "المهرة البريطاني تاريخ السلطنة",
]

ALLOWED_LICENSE = (
    "public domain", "cc0", "cc by", "cc by-sa",
    "no known copyright", "no known restrictions"
)
HEADERS = {
    "User-Agent": "NashhalArchiveBot/4.0 (historical archive index for Nashhal; see repository for contact)"
}


def clean(v):
    if isinstance(v, list):
        v = " ".join(str(x) for x in v)
    return " ".join(str(v or "").split())


def request_json(url, params=None, retries=4):
    params = dict(params or {})
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


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            value = json.load(f)
            return value
    except Exception:
        return default


def license_ok(text):
    value = clean(text).lower()
    return any(x in value for x in ALLOWED_LICENSE)


def relevance_ok(title, description, terms):
    blob = clean(f"{title} {description}").lower()
    strong = [t.lower() for t in terms if len(t) >= 4]
    if not any(t in blob for t in strong):
        return False
    blocked = (
        "guantanamo", "saudi–iranian rivalry", "saudi-iranian rivalry",
        "detainee", "terrorism", "isis", "islamic state"
    )
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
                time.sleep(0.8)
            except Exception as exc:
                print(f"Commons search failed for {query}: {exc}")
    return found


def archive_text_excerpt(identifier, max_chars=700):
    """Fetch only a short OCR excerpt when a public-domain text file exists."""
    try:
        meta = request_json(IA_META + identifier)
        files = meta.get("files", [])
        candidates = []
        for f in files:
            name = clean(f.get("name"))
            if name.lower().endswith(("_djvu.txt", "_text.pdf.txt", ".txt")):
                candidates.append(name)
        if not candidates:
            return ""
        # Prefer the generated DjVu OCR text.
        candidates.sort(key=lambda x: ("_djvu.txt" not in x.lower(), len(x)))
        name = candidates[0]
        url = f"https://archive.org/download/{identifier}/{requests.utils.quote(name)}"
        r = requests.get(url, timeout=30, headers=HEADERS)
        r.raise_for_status()
        text = r.text
        text = re.sub(r"\\s+", " ", text)
        # Keep a compact excerpt only; do not mirror books into the repository.
        return text[:max_chars].strip()
    except Exception as exc:
        print(f"OCR unavailable for {identifier}: {exc}")
        return ""


def collect_archive_org(seen):
    found = []
    for region, queries in SEARCHES:
        for query in queries:
            try:
                data = request_json(IA_API, {
                    "q": f'(title:"{query}" OR description:"{query}" OR subject:"{query}") AND mediatype:(texts OR image)',
                    "fl[]": ["identifier", "title", "description", "date", "creator", "rights", "licenseurl", "mediatype", "subject"],
                    "rows": 8, "page": 1, "sort[]": "downloads desc",
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
                time.sleep(0.8)
            except Exception as exc:
                print(f"Internet Archive search failed for {query}: {exc}")
    return found


def collect_historical_sources(existing_sources):
    seen = {x.get("id") for x in existing_sources if x.get("id")}
    found = []
    for query in EVENT_QUERIES:
        try:
            data = request_json(IA_API, {
                "q": f'(title:"{query}" OR description:"{query}" OR subject:"{query}") AND mediatype:texts',
                "fl[]": ["identifier", "title", "description", "date", "creator", "rights", "licenseurl", "subject", "publisher"],
                "rows": 12, "page": 1, "sort[]": "downloads desc",
            })
            for doc in data.get("response", {}).get("docs", []):
                identifier = clean(doc.get("identifier"))
                item_id = f"ia-source:{identifier}"
                if not identifier or item_id in seen:
                    continue
                title = clean(doc.get("title", identifier))
                description = clean(doc.get("description", ""))
                subject = clean(doc.get("subject", ""))
                rights = clean(doc.get("rights", ""))
                license_url = clean(doc.get("licenseurl", ""))
                # Metadata may omit rights; keep the source index but mark the
                # reuse status as unknown. Only public-domain/CC text is OCRed.
                reusable = license_ok(f"{rights} {license_url}")
                if not relevance_ok(title, f"{description} {subject}", query.split()):
                    continue
                excerpt = archive_text_excerpt(identifier) if reusable else ""
                found.append({
                    "id": item_id,
                    "title": title,
                    "book_title": title,
                    "creator": clean(doc.get("creator", "")),
                    "publisher": clean(doc.get("publisher", "")),
                    "date": clean(doc.get("date", "")),
                    "region": infer_region(f"{query} {title} {subject}"),
                    "topic": "تاريخ العلاقة والمواجهات مع الاستعمار البريطاني",
                    "source": "Internet Archive",
                    "archive_identifier": identifier,
                    "source_url": f"https://archive.org/details/{identifier}",
                    "rights": rights,
                    "license_url": license_url,
                    "reusable_text": reusable,
                    "ocr_excerpt": excerpt,
                    "search_query": query,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                })
                seen.add(item_id)
            time.sleep(0.8)
        except Exception as exc:
            print(f"Historical source search failed for {query}: {exc}")
    combined = (found + existing_sources)[:1000]
    os.makedirs(os.path.dirname(SOURCES_OUT), exist_ok=True)
    with open(SOURCES_OUT, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"Historical sources added: {len(found)}; total: {len(combined)}")
    return found


def infer_region(text):
    q = clean(text).lower()
    mapping = [
        ("يافع", ("yafa", "yafai", "يافع")),
        ("لحج", ("lahij", "lahj", "lahej", "لحج")),
        ("القعيطي", ("qaiti", "quaiti", "mukalla", "القعيطي")),
        ("الكثيري", ("kathiri", "seiyun", "الكثيري")),
        ("المهرة", ("mahra", "mahrah", "المهرة")),
        ("سقطرى", ("socotra", "سقطرى")),
        ("شبوة", ("shabwa", "شبوة")),
        ("عدن", ("aden", "عدن")),
        ("الضالع", ("dhala", "dali", "الضالع")),
        ("الواحدي", ("wahidi", "balhaf", "الواحدي")),
    ]
    for region, terms in mapping:
        if any(t in q for t in terms):
            return region
    return "الجنوب"


def collect():
    existing_images = load_json(OUT, [])
    existing_sources = load_json(SOURCES_OUT, [])
    seen_images = {x.get("id") for x in existing_images if x.get("id")}
    found_images = collect_commons(seen_images) + collect_archive_org(seen_images)
    combined_images = (found_images + existing_images)[:500]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(combined_images, f, ensure_ascii=False, indent=2)
    print(f"Archive images added: {len(found_images)}; total: {len(combined_images)}")
    collect_historical_sources(existing_sources)


if __name__ == "__main__":
    collect()
