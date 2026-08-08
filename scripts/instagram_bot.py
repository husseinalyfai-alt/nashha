import json, os
from datetime import datetime, timezone
import urllib.parse, urllib.request

TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
USER_ID = os.environ.get("INSTAGRAM_USER_ID")
OUT = "data/instagram.json"

if not TOKEN or not USER_ID:
    print("Instagram secrets are not configured yet; keeping existing data.")
    raise SystemExit(0)

params = urllib.parse.urlencode({
    "fields": "id,caption,media_type,media_url,permalink,timestamp,thumbnail_url",
    "access_token": TOKEN,
    "limit": "20",
})
url = f"https://graph.instagram.com/{USER_ID}/media?{params}"

try:
    with urllib.request.urlopen(url, timeout=20) as response:
        payload = json.load(response)
except Exception as exc:
    print(f"Instagram API request failed: {exc}")
    raise SystemExit(1)

items = []
for item in payload.get("data", []):
    items.append({
        "id": item.get("id"),
        "caption": item.get("caption", ""),
        "media_type": item.get("media_type"),
        "media_url": item.get("media_url") or item.get("thumbnail_url", ""),
        "permalink": item.get("permalink", ""),
        "timestamp": item.get("timestamp", ""),
        "collected_at": datetime.now(timezone.utc).isoformat(),
    })

os.makedirs("data", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"Saved {len(items)} Instagram posts")
