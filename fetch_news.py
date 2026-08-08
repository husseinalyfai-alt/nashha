#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

TIMEOUT = 20

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/151 Safari/537.36 "
    "NahshalNews/1.0"
)

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

YEMEN_KEYWORDS = [
    "اليمن",
    "اليمني",
    "اليمنية",
    "اليمنيين",
    "اليمنيون",
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
    "جنوب اليمن",
    "القضية الجنوبية",
    "الحوثي",
    "الحوثيين",
    "الحوثيون",
    "أنصار الله",
    "مليشيا الحوثي",
    "جماعة الحوثي",
    "مجلس القيادة الرئاسي",
    "الحكومة اليمنية",
    "المبعوث الأممي إلى اليمن",
]


def clean_text(value):
    if not value:
        return ""

    value = re.sub(
        r"<script[\s\S]*?</script>",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"<style[\s\S]*?</style>",
        "",
        value,
        flags=re.IGNORECASE,
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


def is_yemen_news(title, description=""):
    text = f"{title} {description}".lower()

    return any(
        keyword.lower() in text
        for keyword in YEMEN_KEYWORDS
    )


def fetch_url(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": (
                "application/rss+xml, "
                "application/xml, "
                "text/xml, "
                "text/html"
            ),
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=TIMEOUT,
    ) as response:
        return response.read()


def parse_date(value):
    if not value:
        return datetime.now(timezone.utc)

    try:
        return parsedate_to_datetime(value)
    except Exception:
        return datetime.now(timezone.utc)


def format_time(value):
    try:
        return value.astimezone().strftime("%H:%M")
    except Exception:
        return "الآن"


def parse_rss(data, source, source_type):
    articles = []

    try:
        root = ET.fromstring(data)
    except Exception as error:
        print(
            f"[WARN] تعذر تحليل RSS الخاص بـ {source}: {error}"
        )
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
                "description": description[:240],
                "link": link,
                "source": source,
                "type": source_type,
                "date": parse_date(date_raw),
            }
        )

    return articles


def remove_duplicates(articles):
    result = []
    seen = set()

    for article in articles:

        key = re.sub(
            r"\s+",
            " ",
            article["title"].lower(),
        ).strip()

        if key in seen:
            continue

        seen.add(key)
        result.append(article)

    result.sort(
        key=lambda item: item["date"],
        reverse=True,
    )

    return result


def collect_news():

    all_articles = []

    for source, url, source_type in RSS_FEEDS:

        print(f"[INFO] جلب أخبار {source}...")

        try:

            data = fetch_url(url)

            articles = parse_rss(
                data,
                source,
                source_type,
            )

            print(
                f"[INFO] {source}: "
                f"{len(articles)} خبر يمني"
            )

            all_articles.extend(articles)

        except Exception as error:

            print(
                f"[WARN] تعذر جلب {source}: {error}"
            )

    return remove_duplicates(
        all_articles
    )


def esc(value):
    return html.escape(
        str(value or ""),
        quote=True,
    )


def update_ticker(document, articles):

    if not articles:
        return document

    ticker_items = []

    for article in articles[:6]:

        ticker_items.append(
            f'''
    <span>{esc(article["source"])}</span>
    <a
      href="{esc(article["link"])}"
      target="_blank"
      rel="noopener noreferrer">
      {esc(article["title"])}
    </a>
'''
        )

    replacement = "\n".join(
        ticker_items
    )

    pattern = re.compile(
        r'(<div\s+class="track"\s*>)([\s\S]*?)(</div>)',
        re.IGNORECASE,
    )

    if not pattern.search(document):

        print(
            "[WARN] لم يتم العثور على .track"
        )

        return document

    return pattern.sub(
        lambda match:
            match.group(1)
            + "\n"
            + replacement
            + "\n"
            + match.group(3),
        document,
        count=1,
    )


def update_hero(document, article):

    title = esc(
        article["title"]
    )

    link = esc(
        article["link"]
    )

    source = esc(
        article["source"]
    )

    description = esc(
        article["description"]
        or
        "تغطية متواصلة لأحدث التطورات في اليمن."
    )

    time = format_time(
        article["date"]
    )

    new_title = f'''
<h1>
  <a
    href="{link}"
    target="_blank"
    rel="noopener noreferrer"
    style="color:inherit;">

    {title}

  </a>
</h1>
'''

    document = re.sub(
        r"<h1>[\s\S]*?</h1>",
        new_title,
        document,
        count=1,
        flags=re.IGNORECASE,
    )

    new_description = f'''
<p>
  {description}
</p>
'''

    document = re.sub(
        r"(<h1>[\s\S]*?</h1>\s*)<p>[\s\S]*?</p>",
        lambda match:
            match.group(1)
            + new_description,
        document,
        count=1,
        flags=re.IGNORECASE,
    )

    new_byline = f'''
<div class="byline">
  <span>
    المصدر: <b>{source}</b>
  </span>

  <span>
    {time}
  </span>

  <span>
    تحديث تلقائي
  </span>
</div>
'''

    document = re.sub(
        r'<div\s+class="byline"[^>]*>[\s\S]*?</div>',
        new_byline,
        document,
        count=1,
        flags=re.IGNORECASE,
    )

    return document


def build_cards(articles):

    cards = []

    for article in articles[:6]:

        title = esc(
            article["title"]
        )

        link = esc(
            article["link"]
        )

        source = esc(
            article["source"]
        )

        description = esc(
            article["description"]
            or
            "التفاصيل الكاملة عبر المصدر الأصلي."
        )

        time = format_time(
            article["date"]
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

            <span>
              {source}
            </span>

            <span>
              {time}
            </span>

          </div>

        </div>

      </article>
'''
        )

    return "\n".join(cards)


def update_cards(document, articles):

    if not articles:
        return document

    marker = "آخر أخبار اليمن"

    position = document.find(marker)

    if position == -1:

        print(
            "[WARN] لم يتم العثور على قسم آخر أخبار اليمن"
        )

        return document

    before = document[:position]
    after = document[position:]

    pattern = re.compile(
        r'(<div\s+class="card-grid"\s*>)([\s\S]*?)(</div>)',
        re.IGNORECASE,
    )

    if not pattern.search(after):

        print(
            "[WARN] لم يتم العثور على card-grid"
        )

        return document

    cards_html = build_cards(
        articles[1:]
    )

    after = pattern.sub(
        lambda match:
            match.group(1)
            + "\n"
            + cards_html
            + "\n"
            + match.group(3),
        after,
        count=1,
    )

    return before + after


def main():

    index_file = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "index.html"
    )

    print(
        "======================================"
    )

    print(
        "      Nahshal Yemen News Updater"
    )

    print(
        "======================================"
    )

    try:

        with open(
            index_file,
            "r",
            encoding="utf-8",
        ) as file:

            document = file.read()

    except FileNotFoundError:

        print(
            f"[ERROR] الملف غير موجود: {index_file}"
        )

        return 1

    articles = collect_news()

    if not articles:

        print(
            "[ERROR] لم يتم العثور على أخبار يمنية."
        )

        print(
            "لن يتم تعديل الموقع."
        )

        return 1

    print(
        f"[OK] إجمالي الأخبار اليمنية: {len(articles)}"
    )

    document = update_hero(
        document,
        articles[0],
    )

    document = update_ticker(
        document,
        articles,
    )

    document = update_cards(
        document,
        articles,
    )

    with open(
        index_file,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            document
        )

    print(
        "[SUCCESS] تم تحديث موقع نهشل."
    )

    return 0


if __name__ == "__main__":
    sys.exit(
        main()
    )
