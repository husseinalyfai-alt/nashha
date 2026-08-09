import json, os, re
from datetime import datetime, timezone
import feedparser
import requests

# مصادر RSS العامة + X وFacebook عند توفير مفاتيح الوصول في GitHub Secrets.
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


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def relevant(title, summary):
    text = f"{title} {summary}".lower()
    return any(k in text for k in YEMEN_KEYWORDS)


def make_item(title, source, link, published, summary):
    title, link, summary = clean(title), clean(link), clean(summary)
    is_south = any(k in f"{title} {summary}".lower() for k in SOUTH_KEYWORDS)
    return {
        "id": link,
        "title": title,
        "source": source,
        "source_url": link,
        "link": link,
        "published": published,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "category": "الجنوب" if is_south else "اليمن",
        "status": "published",
        "confidence": "source_verified",
        "auto_published": True,
        "summary": summary,
        "content": summary,
    }


os.makedirs("data", exist_ok=True)
try:
    with open(OUT, "r", encoding="utf-8") as f:
        existing = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    existing = []

seen = {x.get("link") for x in existing if x.get("link")}
items = []

# RSS
for source, url in FEEDS:
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:30]:
            title = clean(entry.get("title"))
            link = clean(entry.get("link"))
            summary = clean(entry.get("summary"))
            if not title or not link or link in seen or not relevant(title, summary):
                continue
            items.append(make_item(title, source, link, entry.get("published", ""), summary))
            seen.add(link)
    except Exception as exc:
        print(f"RSS source failed: {url}: {exc}")

# X API v2: searches recent public posts matching Yemen/South Yemen terms.
bearer = os.getenv("X_BEARER_TOKEN")
if bearer:
    try:
        params = {
            "query": "(عدن OR حضرموت OR شبوة OR أبين OR لحج OR الضالع OR المهرة OR سقطرى OR الجنوب) -is:retweet lang:ar",
            "max_results": 20,
            "tweet.fields": "created_at,author_id,text",
        }
        r = requests.get(
            "https://api.x.com/2/tweets/search/recent",
            headers={"Authorization": f"Bearer {bearer}"},
            params=params,
            timeout=20,
        )
        r.raise_for_status()
        for post in r.json().get("data", []):
            text = clean(post.get("text"))
            if not text or not relevant(text, ""):
                continue
            pid = post.get("id")
            link = f"https://x.com/i/web/status/{pid}"
            if link in seen:
                continue
            items.append(make_item(text[:160], "X", link, post.get("created_at", ""), text))
            seen.add(link)
    except Exception as exc:
        print(f"X API failed: {exc}")
else:
    print("X_BEARER_TOKEN not configured; skipping X.")

# Facebook Graph API: reads posts from a configured Facebook Page.
fb_page_id = os.getenv("FACEBOOK_PAGE_ID")
fb_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
if fb_page_id and fb_token:
    try:
        params = {
            "access_token": fb_token,
            "fields": "id,message,created_time,permalink_url",
            "limit": 20,
        }
        r = requests.get(
            f"https://graph.facebook.com/{fb_page_id}/posts",
            params=params,
            timeout=20,
        )
        r.raise_for_status()
        for post in r.json().get("data", []):
            text = clean(post.get("message"))
            link = clean(post.get("permalink_url"))
            if not text or not link or link in seen or not relevant(text, ""):
                continue
            items.append(make_item(text[:160], "Facebook", link, post.get("created_time", ""), text))
            seen.add(link)
    except Exception as exc:
        print(f"Facebook Graph API failed: {exc}")
else:
    print("FACEBOOK_PAGE_ID / FACEBOOK_PAGE_ACCESS_TOKEN not configured; skipping Facebook.")

combined = (items + existing)[:MAX_ITEMS]
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)

print(f"New auto-published items: {len(items)}")
