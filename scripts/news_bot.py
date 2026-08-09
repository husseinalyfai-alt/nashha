import json, os, re
from datetime import datetime, timezone
import feedparser
import requests

FEEDS = [
    ("عدن الغد", "https://www.adenalghad.net/rss"),
    ("الأيام", "https://www.alayyam.info/rss"),
    ("المصدر أونلاين", "https://almasdaronline.com/rss"),
    ("سبأ", "https://www.sabanew.net/rss"),
    ("درع الجنوب", "https://deraalganoob.com/", "official_public")
]
SOUTH_KEYWORDS = ["عدن", "حضرموت", "شبوة", "أبين", "لحج", "الضالع", "المهرة", "سقطرى", "الجنوب", "الجنوبي", "المجلس الانتقالي"]
YEMEN_KEYWORDS = SOUTH_KEYWORDS + ["اليمن", "الحوثي", "صنعاء", "مأرب", "تعز"]
OUT = "data/news.json"
MAX_ITEMS = 100

def clean(value): return re.sub(r"\s+", " ", str(value or "")).strip()
def relevant(title, summary): return any(k in f"{title} {summary}".lower() for k in YEMEN_KEYWORDS)
def make_item(title, source, link, published, summary, platform=None, source_type="news"):
    title, link, summary = clean(title), clean(link), clean(summary)
    is_south = any(k in f"{title} {summary}".lower() for k in SOUTH_KEYWORDS)
    return {"id": link, "title": title, "source": source, "source_url": link, "link": link, "published": published, "collected_at": datetime.now(timezone.utc).isoformat(), "category": "الجنوب" if is_south else "اليمن", "status": "published", "confidence": "source_verified", "auto_published": True, "summary": summary, "content": summary, "platform": platform or "news", "source_type": source_type, "embed_url": link if platform in ("X", "Facebook") else ""}

os.makedirs("data", exist_ok=True)
try:
    with open(OUT, "r", encoding="utf-8") as f: existing = json.load(f)
except (FileNotFoundError, json.JSONDecodeError): existing = []
seen = {x.get("link") for x in existing if x.get("link")}
items = []

# Public-data demo, inserted once for testing the internal article page.
demo_link = "https://x.com/"
if not any(x.get("id") == "demo-video-2026-08-09" for x in existing):
    items.append({"id":"demo-video-2026-08-09","title":"مثال تجريبي: خبر نشهل مع مقطع من X","source":"X — مثال تجريبي","source_url":demo_link,"link":demo_link,"published":"2026-08-09","collected_at":datetime.now(timezone.utc).isoformat(),"category":"الجنوب","status":"demo","confidence":"demo","auto_published":False,"summary":"خبر تجريبي لاختبار عرض المقطع والمحتوى داخل صفحة الخبر في نشهل.","content":"هذا خبر تجريبي فقط لاختبار النظام. عند وصول منشور حقيقي من حساب موثوق، سيقوم البوت بإنشاء صفحة خبر داخل نشهل مع إبقاء رابط المنشور الأصلي للمصدر. المقطع في الأخبار الحقيقية سيُعرض من المنصة الأصلية عندما يكون التضمين متاحًا.","platform":"X","embed_url":"https://x.com/"})

# Public RSS/news sources. No operational or location-tracking data is collected.
for feed_info in FEEDS:
    source, url = feed_info[0], feed_info[1]
    source_type = feed_info[2] if len(feed_info) > 2 else "news"
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:30]:
            title, link, summary = clean(entry.get("title")), clean(entry.get("link")), clean(entry.get("summary"))
            if not title or not link or link in seen or not relevant(title, summary): continue
            items.append(make_item(title, source, link, entry.get("published", ""), summary, source_type=source_type)); seen.add(link)
    except Exception as exc: print(f"RSS source failed: {url}: {exc}")

# X: public posts only, limited to public-news keywords.
bearer = os.getenv("X_BEARER_TOKEN")
if bearer:
    try:
        params = {"query": "(عدن OR حضرموت OR شبوة OR أبين OR لحج OR الضالع OR المهرة OR سقطرى OR الجنوب) -is:retweet lang:ar", "max_results": 20, "tweet.fields": "created_at,author_id,text"}
        r = requests.get("https://api.x.com/2/tweets/search/recent", headers={"Authorization": f"Bearer {bearer}"}, params=params, timeout=20); r.raise_for_status()
        for post in r.json().get("data", []):
            text, pid = clean(post.get("text")), post.get("id"); link = f"https://x.com/i/web/status/{pid}"
            if not text or not relevant(text, "") or link in seen: continue
            items.append(make_item(text[:160], "X", link, post.get("created_at", ""), text, "X", "social_public")); seen.add(link)
    except Exception as exc: print(f"X API failed: {exc}")
else: print("X_BEARER_TOKEN not configured; skipping X.")

# Facebook: public posts from a configured public page only.
fb_page_id, fb_token = os.getenv("FACEBOOK_PAGE_ID"), os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
if fb_page_id and fb_token:
    try:
        params = {"access_token": fb_token, "fields": "id,message,created_time,permalink_url", "limit": 20}
        r = requests.get(f"https://graph.facebook.com/{fb_page_id}/posts", params=params, timeout=20); r.raise_for_status()
        for post in r.json().get("data", []):
            text, link = clean(post.get("message")), clean(post.get("permalink_url"))
            if not text or not link or link in seen or not relevant(text, ""): continue
            items.append(make_item(text[:160], "Facebook", link, post.get("created_time", ""), text, "Facebook", "social_public")); seen.add(link)
    except Exception as exc: print(f"Facebook Graph API failed: {exc}")
else: print("FACEBOOK_PAGE_ID / FACEBOOK_PAGE_ACCESS_TOKEN not configured; skipping Facebook.")

with open(OUT, "w", encoding="utf-8") as f: json.dump((items + existing)[:MAX_ITEMS], f, ensure_ascii=False, indent=2)
print(f"New public news items: {len(items)}")
