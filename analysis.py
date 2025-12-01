import matplotlib
matplotlib.use("Agg")  # 画像だけ保存する用

import pandas as pd
from fugashi import Tagger
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# ========= 0. 設定 =========
CSV_PATH = "data/googleplay.csv"
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"  # Codespaces だとだいたいコレ

# ストップワード（ワードクラウド用）
STOPWORDS = set([
    "アプリ", "WEAR", "wear", "ゾゾ", "ZOZOTOWN", "ZOZO",
    "です", "ます", "する", "いる", "ある", "こと",
    "これ", "それ", "ため", "よう", "とても", "なっ",
    "でき", "できない", "ない", "する", "いる",
    "さん", "です", "ます", "する", "なる",
    "使う", "使っ", "使い", "思う", "思っ", "感じ",
    "方", "人", "自分", "今回", "最近", "もの", "ところ",
    "欲しい","ほしい","しまっ","下さい","ください","しまう","アイテム",
    "コーデ", "コーディネート", "ファッション", "服", "洋服",
])

# ポジティブ・ネガティブワード（超シンプル辞書）
POSITIVE_WORDS = {
    "良い", "いい", "便利", "助かる", "最高", "好き",
    "使いやすい", "見やすい", "参考", "楽しい", "お気に入り",
    "ありがたい", "満足", "助かって", "役立つ", "オシャレ",
    "可愛い", "見やすく", "使いやすく", "楽しく",
    "かわいい","カッコいい","かっこいい","おしゃれ","分かりやすい",
}

NEGATIVE_WORDS = {
    "悪い", "微妙", "最悪", "ダメ", "嫌い",
    "使いづらい", "使いにくい", "見づらい", "重い", "落ちる",
    "エラー", "バグ", "フリーズ", "開けない", "起動", "ログインできない",
    "改悪", "鬱陶しい", "邪魔", "イライラ", "困る", "不便",
    "うざい", "壊れて", "強制終了", "エラーメッセージ",
    "ブス","ひどい","わからない","分かりにくい",
}

tagger = Tagger()


# ========= 1. トークナイザ =========
def tokenize_for_wc(text: str):
    """ワードクラウド用：名詞・形容詞・動詞のみ＋ストップワード除去"""
    tokens = []
    for word in tagger(text):
        pos = word.feature.pos1  # 品詞
        if pos in ["名詞", "形容詞", "動詞"]:
            surface = word.surface
            if surface in STOPWORDS:
                continue
            if len(surface.strip()) <= 1:
                continue
            tokens.append(surface)
    return tokens


def tokenize_for_sentiment(text: str):
    """感情判定用：そのまま表層形だけ返す"""
    return [w.surface for w in tagger(text)]


# ========= 2. CSV読み込み =========
df = pd.read_csv(CSV_PATH)
df["content"] = df["content"].astype(str)

# ========= 3. 全体ワードクラウド =========
all_tokens = []
for t in df["content"]:
    all_tokens.extend(tokenize_for_wc(t))

text_for_wc = " ".join(all_tokens)

wc_all = WordCloud(
    width=800,
    height=400,
    font_path=FONT_PATH,
    background_color="white"
).generate(text_for_wc)

plt.figure(figsize=(10, 5))
plt.imshow(wc_all)
plt.axis("off")
plt.tight_layout()
plt.savefig("wordcloud_all.png", dpi=150)
plt.close()


# ========= 4. 簡易ポジネガ判定 =========
def sentiment_score(tokens):
    score = 0
    for t in tokens:
        if t in POSITIVE_WORDS:
            score += 1
        if t in NEGATIVE_WORDS:
            score -= 1
    return score


def label_from_score(score: int) -> str:
    if score >= 1:
        return "pos"
    elif score <= -1:
        return "neg"
    else:
        return "neu"


df["tokens"] = df["content"].apply(tokenize_for_sentiment)
df["sentiment_score"] = df["tokens"].apply(sentiment_score)
df["sentiment"] = df["sentiment_score"].apply(label_from_score)

print(df["sentiment"].value_counts())


# ========= 5. センチメント別ワードクラウド =========
def build_wordcloud(texts, out_path: str):
    counts = Counter()
    for text in texts:
        for t in tokenize_for_wc(text):
            counts[t] += 1

    if not counts:
        print(f"[WARN] {out_path}: 有効なトークンがありません")
        return

    wc = WordCloud(
        font_path=FONT_PATH,
        background_color="white",
        width=1200,
        height=600
    ).generate_from_frequencies(counts)

    wc.to_file(out_path)
    print(f"[INFO] saved {out_path}")


pos_texts = df.loc[df["sentiment"] == "pos", "content"]
neg_texts = df.loc[df["sentiment"] == "neg", "content"]

build_wordcloud(pos_texts, "wordcloud_pos.png")
build_wordcloud(neg_texts, "wordcloud_neg.png")