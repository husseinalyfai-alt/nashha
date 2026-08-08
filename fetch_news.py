#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
يسحب عناوين فقط (بدون نص المقال) من خلاصات RSS لمصادر عالمية وعربية موثوقة،
يفلترها بكلمات مفتاحية متعلقة باليمن/الجنوب، ويحدّث شريط الأخبار العاجلة
في index.html تلقائيًا. لا يُعاد نشر أي نص كامل — فقط العنوان + اسم المصدر.
"""

import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

# مصادر RSS حقيقية — تحقق من الروابط دوريًا لأنها قد تتغيّر من طرف المصدر
FEEDS = {
    "الجزيرة":     "https://www.aljazeera.net/xml/rss/all.xml",
    "فرانس 24":    "https://www.france24.com/ar/rss",
    "بي بي سي":    "https://feeds.bbci.co.uk/arabic/rss.xml",
    "رويترز عربي": "https://arabic.rt.com/rss/",
}

# كلمات الفلترة — عدّلها حسب المحافظات/المدن اللي تركّز عليها المنصة
KEYWORDS = ["اليمن", "عدن", "الجنوب", "حضرموت", "لحج", "أبين", "شبوة", "المهرة", "سقطرى"]

MAX_ITEMS = 6
TIMEOUT = 12

def fetch_feed(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (NahshalBot)"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()

def parse_items(xml_bytes, source_name):
    items = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return items
    for item in root.iter("item"):
        title_el = item.find("title")
        link_el = item.find("link")
        title = (title_el.text or "").strip() if title_el is not None else ""
        link = (link_el.text or "").strip() if link_el is not None else ""
        if title:
            items.append({"title": title, "link": link, "source": source_name})
    return items

def matches_keywords(title):
    return any(k in title for k in KEYWORDS)

def collect_headlines():
    collected = []
    for name, url in FEEDS.items():
        try:
            raw = fetch_feed(url)
            items = parse_items(raw, name)
            for it in items:
                if matches_keywords(it["title"]):
                    collected.append(it)
        except Exception as e:
            print(f"تحذير: تعذّر جلب {name} ({url}): {e}", file=sys.stderr)
    return collected[:MAX_ITEMS]

def build_ticker_html(headlines):
    if not headlines:
        return None
    parts = []
    for h in headlines:
        label = h["source"]
        text = h["title"]
        parts.append(f'<span>{label}</span>{text}')
    return "\n        ".join(parts)

def update_index_html(path, ticker_html):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    pattern = re.compile(r'(<div class="track">\n)(.*?)(\n\s*</div>\n\s*</div>\n\s*</div>)', re.S)
    m = pattern.search(html)
    if not m:
        print("لم يتم العثور على قسم الشريط العاجل داخل index.html", file=sys.stderr)
        return False

    new_html = html[:m.start(2)] + "        " + ticker_html + "\n      " + html[m.end(2):]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return True

if __name__ == "__main__":
    index_path = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    headlines = collect_headlines()
    ticker_html = build_ticker_html(headlines)
    if not ticker_html:
        print("ما فيه عناوين مطابقة الآن — الملف ما تغيّر.", file=sys.stderr)
        sys.exit(0)
    ok = update_index_html(index_path, ticker_html)
    print("تم التحديث." if ok else "فشل التحديث.")
