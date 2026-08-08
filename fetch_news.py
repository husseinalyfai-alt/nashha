name: تحديث أخبار نهشل

on:
  workflow_dispatch:

  schedule:
    - cron: "*/10 * * * *"

permissions:
  contents: write

jobs:

  update-news:

    runs-on: ubuntu-latest

    steps:

      - name: تحميل المشروع
        uses: actions/checkout@v4

      - name: تشغيل تحديث الأخبار
        run: |
          python3 update_news.py index.html

      - name: حفظ التحديثات
        run: |

          git config user.name "Nahshal News Bot"

          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add index.html

          if git diff --cached --quiet; then

            echo "لا توجد أخبار جديدة."

          else

            git commit -m "تحديث أخبار اليمن"

            git push

          fi
