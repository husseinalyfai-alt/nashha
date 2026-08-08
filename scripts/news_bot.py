import json, os, re
from datetime import datetime, timezone
import feedparser

FEEDS = [
    ("عدن الغد", "https://www.adenalghad.net/rss"),
    ("الأيام", "https://www.alayyam.info/rss"),
    ("المصدر أونلاين", "https://almasdaronline.com/rss"),
    ("سبأ", "https://www.sabanew.net/rss"),
]

KEYWORDS = [
    "عدن", "حضرموت", "شبوة", "أبين", "لحج", "الضالع", "المهرة", "سقطرى",
    "الجنوب", "الجنوبي", "اليمن", "الحوثي"
]

OUT = "data/news.json"
os.makedirs("data", exist_ok=True)

try:
    with open(OUT, "r", encoding="utf-8") as f:
        existing = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    existing = []

seen = {x.get("link") for x in existing if x.get("link")}
items = []

for source, url in FEEDS:
    feed = feedparser.parse(url)
    for entry in feed.entries[:15]:
        title = re.sub(r"\s+", " ", entry.get("title", "")).strip()
        link = entry.get("link", "").strip()
        if not title or not link or link in seen:
            continue
        text = f"{title} {entry.get('summary','')}".lower()
        if not any(k in text for k in KEYWORDS):
            continue
        items.append({
            "title": title,
            "source": source,
            "link": link,
            "published": entry.get("published", ""),
            "collected_at": datetime.now(timezone.utc).isoformat()
        })
        seen.add(link)

combined = (items + existing)[:100]
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)

print(f"Collected {len(items)} new items")
