import streamlit as st
import feedparser
import urllib.parse
from datetime import datetime

# 1. ページ設定
st.set_page_config(page_title="歴史のタイムマシン・ニュース", layout="wide")

# 2. サイドバーの設定
st.sidebar.title("🎮 操作パネル")
search_query = st.sidebar.text_input("🔍 ニュース検索キーワード", value="人工知能")
past_years_back = st.sidebar.slider("⏳ 左側の年を何年前にしますか？", 1, 100, 61)

current_year = datetime.now().year
target_past_year = current_year - past_years_back
target_future_cycle = target_past_year + 60
prediction_year = target_future_cycle + 1

# 3. メイン画面
st.title(f"🕰️ 歴史の輪廻：{target_past_year}年 ↔ {target_future_cycle}年")

# --- セクション1: 歴史のリスト (内容を動的に生成) ---
st.header(f"🔄 繰り返す歴史のサイクル")
col1, col2 = st.columns(2)

# 年代に応じた説明文を生成する関数
def get_era_description(year):
    if year == 1965:
        return "**初の商業通信衛星打ち上げ成功**\n世界がリアルタイムで繋がる通信革命の年でした。"
    elif year == 2025:
        return "**AGI（汎用人工知能）の社会実装**\nAIが人間のパートナーとして本格化した歴史的転換点です。"
    elif year < 1945:
        return f"**激動の戦前・戦中（{year}年）**\n世界秩序が大きく揺れ動き、新しい時代の足音が聞こえ始めた頃です。"
    elif 1945 <= year < 1990:
        return f"**高度経済成長と東西冷戦（{year}年）**\n技術革新が次々と起こり、人々の生活が劇的に豊かになった黄金時代です。"
    else:
        return f"**デジタル革命の進展（{year}年）**\nインターネットとスマホが普及し、個人の発信力が最大化した時代です。"

with col1:
    st.subheader(f"🗓️ {target_past_year}年")
    st.info(get_era_description(target_past_year))

with col2:
    st.subheader(f"🗓️ {target_future_cycle}年")
    st.success(get_era_description(target_future_cycle))

# --- セクション2: 未来予想 ---
st.header(f"🔮 {prediction_year}年 未来予想")
st.warning(f"**【{prediction_year}年の展望】**\n{target_future_cycle}年の技術革新を受け、社会の仕組みが根本から書き換わります。個人の力が企業の力を上回る『超・分散型社会』への移行が加速するでしょう。")

# --- セクション3: 最新ニュース ---
st.header(f"📰 最新ニュース: {search_query}")
encoded = urllib.parse.quote(search_query)
feed = feedparser.parse(f"https://news.google.com/rss/search?q={encoded}&hl=ja&gl=JP&ceid=JP:ja")

for entry in feed.entries[:6]:
    st.markdown(f'<div style="background:#f0f2f6;padding:15px;border-radius:10px;border-left:5px solid #ff4b4b;margin-bottom:10px;">{entry.title}</div>', unsafe_allow_html=True)
    st.link_button("記事を読む", entry.link)
