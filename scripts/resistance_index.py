import json
import os
import re
from datetime import datetime, timezone

import requests

SOURCES = "data/historical-sources.json"
OUT = "data/resistance-events.json"
IA_API = "https://archive.org/advancedsearch.php"
HEADERS = {"User-Agent": "NashhalHistoricalIndex/1.0"}

EVENT_QUERIES = [
    "Yafa British expedition Yemen history",
    "Upper Yafa British conflict history",
    "Lower Yafa British conflict history",
    "Lahej British occupation resistance history",
    "Dhala British campaign history",
    "Wahidi Balhaf British history resistance",
    "Aden Protectorate tribal resistance history",
    "South Arabia British expedition tribes history",
    "Mahra British protectorate resistance history",
    "Hadramaut British political military history",
    "Shabwa British history resistance",
    "Aden British occupation 1839 history",
    "يافع الانجليز المقاومة تاريخ",
    "لحج الاحتلال البريطاني المقاومة تاريخ",
    "الضالع الاحتلال البريطاني المقاومة تاريخ",
    "شبوة الاحتلال البريطاني المقاومة تاريخ",
    "المهرة الاحتلال البريطاني تاريخ",
    "حضرموت الاحتلال البريطاني تاريخ السلطنات",
]

REGIONS = {
    "يافع": ["yafa", "yafai", "upper yafa", "lower yafa", "يافع"],
    "لحج": ["lahij", "lahj", "lahej", "لحج"],
    "الضالع": ["dhala", "dali", "ad dali", "الضالع"],
    "شبوة": ["shabwa", "شبوة"],
    "المهرة": ["mahra", "mahrah", "المهرة"],
    "حضرموت": ["hadramaut", "hadhramaut", "حضرموت"],
    "عدن": ["aden", "عدن"],
    "الواحدي": ["wahidi", "balhaf", "الواحدي"],
    "القعيطي": ["qaiti", "quaiti", "mukalla", "القعيطي"],
    "الكثيري": ["kathiri", "seiyun", "الكثيري"],
}


def clean(v):
    if isinstance(v, list):
        v = " ".join(map(str, v))
    return " ".join(str(v or "").split())


def infer_region(text):
    t = clean(text).lower()
    for region, terms in REGIONS.items():
        if any(term in t for term in terms):
            return region
    return "الجنوب"


def get_json(params):
    p = dict(params)
    p["format"] = "json"
    p["formatversion"] = 2
    r = requests.get(IA_API, params=p, headers=HEADERS, timeout=45)
    r.raise_for_status()
    return r.json()


def build():
    existing = []
    if os.path.exists(OUT):
        try:
            with open(OUT, encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []
    seen = {x.get("source_id") for x in existing if x.get("source_id")}
    events = []

    for query in EVENT_QUERIES:
        try:
            data = get_json({
                "q": f'(title:"{query}" OR description:"{query}" OR subject:"{query}") AND mediatype:texts',
                "fl[]": ["identifier", "title", "description", "date", "creator", "subject", "publisher"],
                "rows": 15,
                "sort[]": "downloads desc",
            })
            for doc in data.get("response", {}).get("docs", []):
                identifier = clean(doc.get("identifier"))
                if not identifier or identifier in seen:
                    continue
                title = clean(doc.get("title", identifier))
                description = clean(doc.get("description", ""))
                subject = clean(doc.get("subject", ""))
                blob = f"{query} {title} {description} {subject}"
                region = infer_region(blob)
                source_id = identifier
                event = {
                    "id": f"ia-event:{identifier}",
                    "source_id": source_id,
                    "status": "candidate",
                    "title": title,
                    "region": region,
                    "period": clean(doc.get("date", "")),
                    "summary": description[:1200],
                    "historical_note": "مرشح يحتاج مراجعة المصدر نفسه ومقارنته بمصادر أخرى قبل اعتماده كحقيقة نهائية.",
                    "participants": [],
                    "date_start": None,
                    "date_end": None,
                    "location": None,
                    "outcome": None,
                    "source": {
                        "name": "Internet Archive",
                        "book_title": title,
                        "creator": clean(doc.get("creator", "")),
                        "publisher": clean(doc.get("publisher", "")),
                        "date": clean(doc.get("date", "")),
                        "identifier": identifier,
                        "url": f"https://archive.org/details/{identifier}",
                    },
                    "search_query": query,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                }
                events.append(event)
                seen.add(source_id)
        except Exception as exc:
            print(f"Search failed: {query}: {exc}")

    combined = (events + existing)[:1500]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"Resistance candidates added: {len(events)}; total: {len(combined)}")


if __name__ == "__main__":
    build()
