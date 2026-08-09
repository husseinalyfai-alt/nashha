import json, os, re
from datetime import datetime, timezone
import feedparser

# مصادر عامة موثوقة. نستخدم RSS/صفحات الأخبار العامة بدل الاعتماد على تسجيل دخول X.
FEEDS = [
    ("عدن الغد", "https://www.adenalghad.net/rss"),
    ("الأيام", "https://www.alayyam.info/rss"),
    ("المصدر أونلاين", "https://almasdaronline.com/rss"),
    ("سبأ", "https://www.sabanew.net/rss"),
]

SOUTH_KEYWORDS = [
    "عدن", "حضرموت", "شبوة", "أبين", "لحج", "الضالع", "المهرة", "سقطرى",
    "الجنوب", "الجنوبي", "المجلس الانتقالي"
]
YEMEN_KEYWORDS = SOUTH_KEYWORDS + ["اليمن", "الحوثي", "صنعاء", "مأرب", "تعز"]
OUT = "data/news.json"
MAX_ITEMS = 100

os.makedirs("data", exist_ok=True)
try:
    with open(OUT, "r", encoding="utf-8") as f:
        existing = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    existing = []

seen = {x.get("link") for x in existing if x.get("link")}
items = []

for source, url in FEEDS:
    try:
        feed = feedparser.parse(url)
    except Exception:
        continue
    for entry in feed.entries[:30]:
        title = re.sub(r"\s+", " ", entry.get("title", "")).strip()
        link = entry.get("link", "").strip()
        summary = re.sub(r"\s+", " ", entry.get("summary", "")).strip()
        if not title or not link or link in seen:
            continue
        text = f"{title} {summary}".lower()
        if not any(k in text for k in YEMEN_KEYWORDS):
            continue
        is_south = any(k in text for k in SOUTH_KEYWORDS)
        items.append({
            "id": link,
            "title": title,
            "source": source,
            "source_url": link,
            "link": link,
            "published": entry.get("published", ""),
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "category": "الجنوب" if is_south else "اليمن",
            "status": "published",
            "confidence": "source_verified",
            "auto_published": True,
            "summary": summary,
            "content": summary
        })
        seen.add(link)

combined = (items + existing)[:MAX_ITEMS]
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)

print(f"New auto-published items: {len(items)}")
