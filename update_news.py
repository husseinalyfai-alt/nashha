# -*- coding: utf-8 -*-

import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


# ============================================================
# مصادر الأخبار
# ============================================================

RSS_FEEDS = [
    (
        "بي بي سي عربي",
        "https://feeds.bbci.co.uk/arabic/rss.xml",
        "دولي",
    ),
    (
        "فرانس 24",
        "https://www.france24.com/ar/rss",
        "دولي",
    ),
    (
        "الجزيرة",
        "https://www.aljazeera.net/xml/rss/all.xml",
        "عربي",
    ),
    (
        "سبأ",
        "https://www.sabanew.net/rss.php?lang=ar",
        "يمني",
    ),
]


# ============================================================
# مصادر يمنية لا تعتمد RSS
# ============================================================

HTML_SOURCES = [
    (
        "المركز الإعلامي لألوية العمالقة الجنوبية",
        "https://alamalika.net/site/category/news/",
        "يمني",
    ),
    (
        "الأمم المتحدة في اليمن",
        "https://yemen.un.org/en/press-centre/press-releases",
        "أممي",
    ),
]


# ============================================================
# كلمات اليمن
# ============================================================

YEMEN_KEYWORDS = [
    "اليمن",
    "اليمني",
    "اليمنية",
    "عدن",
    "حضرموت",
    "شبوة",
    "أبين",
    "لحج",
    "الضالع",
    "المهرة",
    "سقطرى",
    "تعز",
    "مأرب",
    "الحديدة",
    "صنعاء",
    "صعدة",
    "حجة",
    "إب",
    "البيضاء",
    "الجوف",
    "ريمة",
    "ذمار",
    "المحويت",
    "باب المندب",
    "البحر الأحمر",
    "الجنوب اليمني",
    "القضية الجنوبية",
    "الحوثي",
    "الحوثيين",
    "الحوثيون",
    "أنصار الله",
]


USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/151 Safari/537.36 "
    "NahshalNews/1.0"
)

TIMEOUT = 20


# ============================================================
# تنظيف النص
# ============================================================

def clean_text(value):
    if not value:
        return ""

    value = re.sub(
        r"<script[\s\S]*?</script>",
        "",
        value,
        flags=re.I,
    )

    value = re.sub(
        r"<style[\s\S]*?</style>",
        "",
        value,
        flags=re.I,
    )

    value = re.sub(
        r"<[^>]+>",
        " ",
        value,
    )

    value = html.unescape(value)

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


# ============================================================
# التحقق من أن الخبر يمني
# ============================================================

def is_yemen_news(title, description=""):
    text = (
        f"{title} {description}"
    ).lower()

    return any(
        keyword.lower() in text
        for keyword in YEMEN_KEYWORDS
    )


# ============================================================
# جلب صفحة
# ============================================================

def fetch(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": (
                "text/html, "
                "application/rss+xml, "
                "application/xml, "
                "text/xml"
            ),
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=TIMEOUT,
    ) as response:
        return response.read()


# ============================================================
# قراءة RSS
# ============================================================

def parse_rss(data, source, source_type):
    articles = []

    try:
        root = ET.fromstring(data)
    except Exception:
        return articles

    for item in root.iter("item"):

        title_element = item.find("title")
        link_element = item.find("link")
        description_element = item.find("description")
        date_element = item.find("pubDate")

        title = clean_text(
            title_element.text
            if title_element is not None
            else ""
        )

        link = (
            link_element.text.strip()
            if link_element is not None
            and link_element.text
            else ""
        )

        description = clean_text(
            description_element.text
            if description_element is not None
            else ""
        )

        date_raw = (
            date_element.text
            if date_element is not None
            else ""
        )

        if not title or not link:
            continue

        if not is_yemen_news(
            title,
            description,
        ):
            continue

        articles.append(
            {
                "title": title,
                "description": description[:220],
                "link": link,
                "source": source,
                "type": source_type,
                "date": parse_date(date_raw),
            }
        )

    return articles


# ============================================================
# قراءة صفحات HTML مثل العمالقة والأمم المتحدة
# ============================================================

def parse_html_page(
    data,
    source,
    source_type,
    base_url,
):
    text = data.decode(
        "utf-8",
        errors="ignore",
    )

    articles = []

    pattern = re.compile(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>'
        r'([\s\S]*?)'
        r'</a>',
        re.I,
    )

    seen = set()

    for match in pattern.finditer(text):

        link = match.group(1)

        title = clean_text(
            match.group(2)
        )

        if not title:
            continue

        if len(title) < 20:
            continue

        if not is_yemen_news(
            title
        ):
            continue

        if title in seen:
            continue

        seen.add(title)

        if link.startswith("/"):
            link = (
                base_url.rstrip("/")
                + link
            )

        elif link.startswith("#"):
            continue

        elif not link.startswith("http"):
            continue

        articles.append(
            {
                "title": title,
                "description": "",
                "link": link,
                "source": source,
                "type": source_type,
                "date": datetime.now(
                    timezone.utc
                ),
            }
        )

    return articles[:15]


# ============================================================
# التاريخ
# ============================================================

def parse_date(value):

    if not value:
        return datetime.now(
            timezone.utc
        )

    try:
        return parsedate_to_datetime(
            value
        )
    except Exception:
        return datetime.now(
            timezone.utc
        )


# ============================================================
# جلب كل الأخبار
# ============================================================

def collect_news():

    all_news = []

    for source, url, source_type in RSS_FEEDS:

        try:

            print(
                f"[RSS] {source}"
            )

            data = fetch(url)

            all_news.extend(
                parse_rss(
                    data,
                    source,
                    source_type,
                )
            )

        except Exception as error:

            print(
                f"[WARN] {source}: {error}"
            )


    for source, url, source_type in HTML_SOURCES:

        try:

            print(
                f"[WEB] {source}"
            )

            data = fetch(url)

            base_url = (
                "/".join(
                    url.split("/")[:3]
                )
            )

            all_news.extend(
                parse_html_page(
                    data,
                    source,
                    source_type,
                    base_url,
                )
            )

        except Exception as error:

            print(
                f"[WARN] {source}: {error}"
            )


    return remove_duplicates(
        all_news
    )


# ============================================================
# إزالة التكرار
# ============================================================

def remove_duplicates(news):

    result = []

    seen = set()

    for item in news:

        key = re.sub(
            r"\s+",
            " ",
            item["title"].lower(),
        ).strip()

        if key in seen:
            continue

        seen.add(key)

        result.append(item)

    result.sort(
        key=lambda x: x["date"],
        reverse=True,
    )

    return result


# ============================================================
# HTML آمن
# ============================================================

def esc(value):
    return html.escape(
        str(value or ""),
        quote=True,
    )


# ============================================================
# الوقت
# ============================================================

def format_time(date):

    try:

        return date.astimezone().strftime(
            "%H:%M"
        )

    except Exception:

        return "الآن"


# ============================================================
# تحديث الشريط العاجل
# ============================================================

def update_ticker(document, news):

    items = []

    for item in news[:6]:

        items.append(
            f'''
    <span>{esc(item["source"])}</span>
    <a href="{esc(item["link"])}"
       target="_blank"
       rel="noopener noreferrer">
       {esc(item["title"])}
    </a>
'''
        )

    replacement = "\n".join(items)

    pattern = re.compile(
        r'(<div\s+class="track"\s*>)([\s\S]*?)(</div>)',
        re.I,
    )

    return pattern.sub(
        lambda m:
            m.group(1)
            + "\n"
            + replacement
            + "\n"
            + m.group(3),
        document,
        count=1,
    )


# ============================================================
# تحديث الخبر الرئيسي
# ============================================================

def update_hero(document, item):

    link = esc(item["link"])
    title = esc(item["title"])
    source = esc(item["source"])
    description = esc(
        item["description"]
        or
        "تغطية ومتابعة لأحدث التطورات المتعلقة باليمن."
    )
    time = format_time(
        item["date"]
    )

    new_h1 = f'''
<h1>
  <a href="{link}"
     target="_blank"
     rel="noopener noreferrer"
     style="color:inherit;">
     {title}
  </a>
</h1>
'''

    document = re.sub(
        r'<h1>[\s\S]*?</h1>',
        new_h1,
        document,
        count=1,
        flags=re.I,
    )

    new_byline = f'''
<div class="byline">
  <span>المصدر: <b>{source}</b></span>
  <span>{time}</span>
  <span>تحديث تلقائي</span>
</div>
'''

    document = re.sub(
        r'<div\s+class="byline"[^>]*>[\s\S]*?</div>',
        new_byline,
        document,
        count=1,
        flags=re.I,
    )

    return document


# ============================================================
# بطاقات آخر الأخبار
# ============================================================

def build_cards(news):

    cards = []

    for item in news[:6]:

        link = esc(item["link"])
        title = esc(item["title"])
        source = esc(item["source"])
        description = esc(
            item["description"]
            or
            "التفاصيل الكاملة عبر المصدر الأصلي."
        )
        time = format_time(
            item["date"]
        )

        cards.append(
            f'''
      <article class="card">

        <div class="card-figure">
          <span class="tag">
            {source}
          </span>
        </div>

        <div class="card-body">

          <h3>
            <a
              href="{link}"
              target="_blank"
              rel="noopener noreferrer"
              style="color:inherit;">

              {title}

            </a>
          </h3>

          <p>
            {description}
          </p>

          <div class="meta">
            <span>{source}</span>
            <span>{time}</span>
          </div>

        </div>

      </article>
'''
        )

    return "\n".join(cards)


def update_cards(document, news):

    cards_html = build_cards(
        news
    )

    # نحدد card-grid الخاصة بـ
    # "آخر أخبار اليمن" وليس قسم التقارير.

    section_position = document.find(
        "آخر أخبار اليمن"
    )

    if section_position == -1:
        print(
            "[WARN] لم يتم العثور على قسم آخر أخبار اليمن"
        )
        return document

    before = document[
        :section_position
    ]

    after = document[
        section_position:
    ]

    pattern = re.compile(
        r'(<div\s+class="card-grid"\s*>)([\s\S]*?)(</div>)',
        re.I,
    )

    updated_after = pattern.sub(
        lambda m:
            m.group(1)
            + "\n"
            + cards_html
            + "\n"
            + m.group(3),
        after,
        count=1,
    )

    return before + updated_after


# ============================================================
# البرنامج الرئيسي
# ============================================================

def main():

    path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "index.html"
    )

    try:

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:

            document = file.read()

    except FileNotFoundError:

        print(
            f"[ERROR] لم يتم العثور على {path}"
        )

        return 1


    news = collect_news()

    if not news:

        print(
            "[ERROR] لم يتم العثور على أخبار يمنية."
        )

        return 1


    print(
        f"[OK] تم العثور على {len(news)} خبرًا يمنيًا."
    )


    # الخبر الرئيسي
    document = update_hero(
        document,
        news[0],
    )


    # العاجل
    document = update_ticker(
        document,
        news,
    )


    # آخر الأخبار
    document = update_cards(
        document,
        news,
    )


    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            document
        )


    print(
        "[OK] تم تحديث نهشل بنجاح."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
