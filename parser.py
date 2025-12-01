import re
import csv
from datetime import datetime
from pathlib import Path

INPUT_PATH = Path("data/googleplay.txt")
OUTPUT_PATH = Path("data/googleplay.csv")

# 例: 2025年11月25日
DATE_RE = re.compile(r"^(\d{4})年(\d{1,2})月(\d{1,2})日$")
HELP_RE = re.compile(r"^(\d+)\s*人のユーザーが、このレビューが役立ったと評価しました$")

MARKER = "役に立ちましたか？"

def parse_reviews(lines):
    """
    Google Play からコピペしたテキストを行リストとして受け取り、
    レビュー dict のリストを返す。
    """
    # 空行は邪魔なのでここで削っておく
    clean = [l.strip() for l in lines if l.strip()]
    reviews = []
    i = 0
    n = len(clean)

    while i < n - 2:
        author = clean[i]
        m_date = DATE_RE.match(clean[i + 1])
        if not m_date:
            # 「アイコン画像」「評価とレビュー」みたいなノイズをスキップ
            i += 1
            continue

        # この author + date から始まるブロックの終端を探す
        j = i + 2
        while j < n and clean[j] != MARKER:
            j += 1

        if j == n:
            # 「役に立ちましたか？」 まで届かない = 開発元返信などとみなして捨てる
            i += 1
            continue

        # 本文 + helpful_vote 抽出
        body_lines = []
        helpful = 0

        for k in range(i + 2, j):
            m_help = HELP_RE.match(clean[k])
            if m_help:
                helpful = int(m_help.group(1))
            else:
                body_lines.append(clean[k])

        year, month, day = map(int, m_date.groups())
        date_iso = datetime(year, month, day).strftime("%Y-%m-%d")

        # ZOZO公式返信ぽいものは author で弾く（念のため）
        if author != "ZOZO, Inc.":
            reviews.append(
                {
                    "author": author,
                    "date": date_iso,
                    "year": year,
                    "helpful_votes": helpful,
                    "content": "\n".join(body_lines),
                    "source": "google_play_android",
                }
            )

        # 次の候補へ（「役に立ちましたか？」 の次の行から再開）
        i = j + 1

    return reviews


def main():
    text = INPUT_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()

    reviews = parse_reviews(lines)
    print(f"parsed reviews: {len(reviews)} 件")

    # CSV 出力
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["author", "date", "year", "helpful_votes", "content", "source"]

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reviews)


if __name__ == "__main__":
    main()