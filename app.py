import streamlit as st
import feedparser
import urllib.parse
import random
from datetime import datetime

# 1. ページ設定
st.set_page_config(page_title="歴史のタイムマシン・2026予言", layout="wide")

# 2. 歴史データベース
history_db = {
    1945: ("終戦・国際連合設立", "2005: 愛知万博・YouTube誕生"),
    1946: ("日本国憲法公布", "2006: 第1回WBC優勝・Twitter開始"),
    1947: ("学校給食の開始", "2007: 初代iPhone発売・ニコニコ動画ブーム"),
    1948: ("海上保安庁の発足", "2008: iPhone 3G日本上陸・リーマンショック"),
    1949: ("湯川秀樹氏がノーベル賞受賞", "2009: 裁判員制度開始・オバマ大統領就任"),
    1950: ("金閣寺焼失・公営ギャンブル開始", "2010: iPad発売・はやぶさ帰還"),
    1951: ("サンフランシスコ平和条約調印", "2011: 東日本大震災・LINEサービス開始"),
    1952: ("手塚治虫「鉄腕アトム」連載開始", "2012: 東京スカイツリー開業・iPS細胞ノーベル賞"),
    1953: ("テレビ放送開始", "2013: 富士山が世界遺産に・東京五輪決定"),
    1954: ("映画「ゴジラ」第1作公開", "2014: 青色LEDノーベル賞・笑っていいとも終了"),
    1955: ("1円硬貨発行・自由民主党結党", "2015: マイナンバー法成立・ラグビーW杯快進撃"),
    1956: ("もはや戦後ではない（経済白書）", "2016: リオ五輪・ポケモンGO社会現象"),
    1957: ("南極観測隊が昭和基地設営", "2017: 将棋・藤井聡太四段29連勝"),
    1958: ("東京タワー完成・チキンラーメン発売", "2018: 大谷翔平メジャー新人王・安室奈美恵引退"),
    1959: ("岩戸景気・少年マガジン/サンデー創刊", "2019: 令和への改元・ラグビーW杯日本開催"),
    1960: ("カラーテレビ放送開始", "2020: 新型コロナ流行・リモートワーク普及"),
    1961: ("ガガーリン人類初の宇宙飛行", "2021: 東京2020オリンピック開催"),
    1962: ("堀江謙一氏がヨットで太平洋単独横断", "2022: 北京冬季五輪・鉄道開業150周年"),
    1963: ("鉄腕アトム放送開始・ケネディ暗殺", "2023: 将棋・藤井聡太八冠・ChatGPTブーム"),
    1964: ("東京オリンピック・東海道新幹線開業", "2024: 新紙幣発行・生成AIの爆発的普及"),
    1965: ("商業通信衛星成功・日韓基本条約", "2025: 大阪・関西万博・AGI（汎用AI）の実装")
}

# 3. 未来予想
predictions_2026 = [
    "**【AIエージェントによる個人の帝国化】** 一人がAIを使いこなし、大企業並みの価値を生む時代へ。",
    "**【バーチャル経済の完全自立】** メタバース内での経済圏が現物経済を凌駕し始める。",
    "**【分散型エネルギー革命】** 家庭ごとの小型発電が主流となり、電力供給の形が激変する。",
    "**【AIによる医療診断の標準化】** 家庭用デバイスで病気の兆候をAIが完璧に予見する。",
    "**【空飛ぶクルマの日常化】** 都市部での短距離移動に革命が起き、渋滞という言葉が死語に。",
    "**【言語の壁が消滅】** リアルタイム翻訳が完璧になり、世界中の人が母国語で対話する。",
    "**【宇宙旅行時代の幕開け】** 民間人による月周回旅行が現実のものとなり、宇宙が身近に。",
    "**【スマート衣料の普及】** 着るだけで健康状態を管理し、温度を自動調整する服が一般化。",
    "**【教育のパーソナル化】** AI教師が一人ひとりの才能を最短距離で伸ばす教育システムへ。",
    "**【五感を送る通信技術】** 映像だけでなく、味覚や触覚もデジタルで送れるようになる。"
]

# 4. サイドバー
st.sidebar.title("🎮 操作パネル")
search_query = st.sidebar.text_input("🔍 最新ニュース検索", value="人工知能")
target_past_year = st.sidebar.select_slider(
    "⏳ 過去の年を選択",
    options=list(history_db.keys()),
    value=1965
)

# 5. メイン画面
target_future_cycle = target_past_year + 60
st.title(f"🕰️ 歴史の輪廻：{target_past_year}年 ↔ {target_future_cycle}年")

col1, col2 = st.columns(2)
past_fact, future_fact = history_db[target_past_year]
with col1:
    st.subheader(f"🗓️ {target_past_year}年")
    st.info(past_fact)
with col2:
    st.subheader(f"🗓️ {target_future_cycle}年")
    st.success(future_fact)

st.write("---")
st.header("🔮 2026年 未来予言（おみくじ）")
st.warning(random.choice(predictions_2026))

st.header(f"📰 最新ニュース: {search_query}")
encoded = urllib.parse.quote(search_query)
feed = feedparser.parse(f"https://news.google.com/rss/search?q={encoded}&hl=ja&gl=JP&ceid=JP:ja")
for entry in feed.entries[:5]:
    st.markdown(f'<div style="background:#f0f2f6;padding:10px;border-radius:10px;margin-bottom:5px;">{entry.title}</div>', unsafe_allow_html=True)
    st.link_button("読む", entry.link)
