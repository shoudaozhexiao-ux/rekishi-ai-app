import streamlit as st
import feedparser
import urllib.parse
from datetime import datetime

# 1. ページ設定
st.set_page_config(page_title="歴史のタイムマシン・ニュース", layout="wide")

# 2. サイドバーの設定
st.sidebar.title("🎮 操作パネル")

# 【機能1】ニュース検索
st.sidebar.subheader("🔍 ニュースを探す")
if 'search_word' not in st.session_state:
    st.session_state.search_word = "人工知能"

search_query = st.sidebar.text_input("キーワードを入力してEnter", value=st.session_state.search_word)
st.session_state.search_word = search_query

st.sidebar.divider()

# 【機能2】比較する年代の切り替え
st.sidebar.subheader("⏳ 歴史をさかのぼる")
past_years_back = st.sidebar.slider("何年前と比較しますか？", min_value=1, max_value=100, value=61)
current_year = datetime.now().year
target_past_year = current_year - past_years_back

st.sidebar.info(f"現在は {current_year}年 です。\n{past_years_back}年前の {target_past_year}年 と比較します。")

# 3. メイン画面
st.title(f"🕰️ 歴史の輪廻：{past_years_back}年前 ↔ 現在")

# --- セクション1: 歴史のリスト ---
st.header(f"🔄 繰り返す歴史のリスト ({target_past_year}年 ↔ {current_year-1}年)")
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"🗓️ {target_past_year}年頃")
    if past_years_back == 61:
        st.info("**初の商業通信衛星打ち上げ成功**\n世界が映像で繋がり、地球規模の通信革命が始まった瞬間です。")
        st.info("**日韓基本条約の調印と国交回復**\n戦後の外交に大きな区切りをつけ、アジアの新しい関係を作りました。")
    else:
        st.info(f"**{target_past_year}年の主な出来事**\nこの年は、今の時代に繋がる大きな社会の変化や技術の誕生がありました。")
        st.caption("※年代ごとの詳細データは、今後AIが自動生成するように拡張可能です。")

with col2:
    st.subheader(f"🗓️ {current_year-1}年（1年前）")
    st.success("**AGI（汎用人工知能）の社会実装**\nAIが人間のように思考し、最高のパートナーとして進化した年です。")
    st.success("**大阪・関西万博による国際交流**\n世界が知恵を出し合い、未来の命を救うための対話が行われました。")

# --- セクション2: 2026年の未来予想 ---
st.header(f"🔮 {current_year}年 未来予想")
st.warning("""
**【AIエージェントによる個人の帝国化】**
AIがあなたの分身として24時間働き、たった一人であっても世界中の人々へ価値を届けられる『超・個人時代』が本格的に幕を開けます。高度な自動化により、個人の創造力がかつてないほど試される一年となるでしょう。
""")

# --- セクション3: 最新ニュース ---
st.header(f"📰 最新の日本語ニュース: {search_query}")

encoded = urllib.parse.quote(search_query)
rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=ja&gl=JP&ceid=JP:ja"
feed = feedparser.parse(rss_url)

if not feed.entries:
    st.error("ニュースが見つかりませんでした。別の言葉を試してください。")
else:
    for entry in feed.entries[:8]:
        st.markdown(f'''
            <div style="background:#f0f2f6; padding:15px; border-radius:10px; border-left:5px solid #ff4b4b; margin-bottom:10px;">
                <small style="color:#666;">{entry.get('published', '')}</small><br>
                <strong style="font-size:1.1rem; color:#333;">{entry.title}</strong>
            </div>
        ''', unsafe_allow_html=True)
        st.link_button("記事を読む", entry.link)
