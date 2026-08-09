import json
import os
from datetime import datetime, timezone

import requests

OUT = "data/resistance-events.json"
IA_API = "https://archive.org/advancedsearch.php"
HEADERS = {"User-Agent": "NashhalHistoricalIndex/1.1"}

EVENT_QUERIES = [
    "Yafa British expedition Yemen history", "Upper Yafa British conflict history",
    "Lower Yafa British conflict history", "Lahej British occupation resistance history",
    "Dhala British campaign history", "Wahidi Balhaf British history resistance",
    "Aden Protectorate tribal resistance history", "South Arabia British expedition tribes history",
    "Mahra British protectorate resistance history", "Hadramaut British political military history",
    "Shabwa British history resistance", "Aden British occupation 1839 history",
    "يافع الانجليز المقاومة تاريخ", "لحج الاحتلال البريطاني المقاومة تاريخ",
    "الضالع الاحتلال البريطاني المقاومة تاريخ", "شبوة الاحتلال البريطاني المقاومة تاريخ",
    "المهرة الاحتلال البريطاني تاريخ", "حضرموت الاحتلال البريطاني تاريخ السلطنات",
]

REGIONS = {
    "يافع": ["yafa", "yafai", "upper yafa", "lower yafa", "يافع"],
    "لحج": ["lahij", "lahj", "lahej", "لحج"],
    "الضالع": ["dhala", "dali", "ad dali", "الضالع"],
    "شبوة": ["shabwa", "شبوة"], "المهرة": ["mahra", "mahrah", "المهرة"],
    "حضرموت": ["hadramaut", "hadhramaut", "حضرموت"], "عدن": ["aden", "عدن"],
    "الواحدي": ["wahidi", "balhaf", "الواحدي"],
    "القعيطي": ["qaiti", "quaiti", "mukalla", "القعيطي"],
    "الكثيري": ["kathiri", "seiyun", "الكثيري"],
}


def clean(v):
    if isinstance(v, list): v = " ".join(map(str, v))
    return " ".join(str(v or "").split())


def infer_region(text):
    t = clean(text).lower()
    for region, terms in REGIONS.items():
        if any(term in t for term in terms): return region
    return "الجنوب"


def get_json(params):
    p = dict(params)
    p.update({"output": "json", "format": "json", "formatversion": 2})
    last = None
    for delay in (0, 2, 5):
        try:
            r = requests.get(IA_API, params=p, headers=HEADERS, timeout=45)
            if r.status_code in (429, 500, 502, 503, 504):
                last = f"HTTP {r.status_code}"
                if delay: import time; time.sleep(delay)
                continue
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as exc:
            last = str(exc)
            if delay: import time; time.sleep(delay)
    raise RuntimeError(last or "invalid Archive.org response")


def load_existing():
    if not os.path.exists(OUT): return []
    try:
        with open(OUT, encoding="utf-8") as f: data = json.load(f)
    except Exception: return []
    if isinstance(data, dict):
        data = data.get("events", [])
    if not isinstance(data, list): return []
    return [x for x in data if isinstance(x, dict)]


def build():
    existing = load_existing()
    seen = {x.get("source_id") for x in existing if x.get("source_id")}
    events = []
    for query in EVENT_QUERIES:
        try:
            data = get_json({
                "q": f'(title:"{query}" OR description:"{query}" OR subject:"{query}") AND mediatype:texts',
                "fl[]": ["identifier", "title", "description", "date", "creator", "subject", "publisher"],
                "rows": 15, "sort[]": "downloads desc",
            })
            for doc in data.get("response", {}).get("docs", []):
                identifier = clean(doc.get("identifier"))
                if not identifier or identifier in seen: continue
                title = clean(doc.get("title", identifier))
                description = clean(doc.get("description", ""))
                subject = clean(doc.get("subject", ""))
                event = {
                    "id": f"ia-event:{identifier}", "source_id": identifier,
                    "status": "candidate", "title": title,
                    "region": infer_region(f"{query} {title} {description} {subject}"),
                    "period": clean(doc.get("date", "")), "summary": description[:1200],
                    "historical_note": "مرشح يحتاج مراجعة المصدر نفسه ومقارنته بمصادر أخرى قبل اعتماده كحقيقة نهائية.",
                    "participants": [], "date_start": None, "date_end": None,
                    "location": None, "outcome": None,
                    "source": {"name": "Internet Archive", "book_title": title,
                               "creator": clean(doc.get("creator", "")),
                               "publisher": clean(doc.get("publisher", "")),
                               "date": clean(doc.get("date", "")),
                               "identifier": identifier,
                               "url": f"https://archive.org/details/{identifier}"},
                    "search_query": query,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                }
                events.append(event); seen.add(identifier)
        except Exception as exc:
            print(f"Search failed: {query}: {exc}")
    combined = (events + existing)[:1500]
    payload = {"schema_version": 1, "title": "موسوعة المقاومة الجنوبية والأحداث التاريخية",
               "methodology": {"status_values": ["candidate", "verified", "disputed"],
               "note": "لا يتحول أي مرشح إلى مادة منشورة بوصفه حقيقة إلا بعد مراجعة المصدر ومقارنته بمصادر مستقلة عند الحاجة."},
               "events": combined}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f: json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Resistance candidates added: {len(events)}; total: {len(combined)}")


if __name__ == "__main__": build()
