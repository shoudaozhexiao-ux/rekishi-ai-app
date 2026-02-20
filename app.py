import streamlit as st
import feedparser
import urllib.parse
from datetime import datetime

# 1. ページ設定
st.set_page_config(page_title="歴史のタイムマシン・ニュース", layout="wide")

# 2. 厳選された歴史データ辞書（ここに事実がある年だけが選択肢になります）
# 都市伝説的に「60年周期」が面白い年を並べています
history_db = {
    1964: "**東京オリンピック開催・東海道新幹線開業**\n日本のインフラが劇的に進化し、世界に復興を示した象徴的な年です。",
    1965: "**初の商業通信衛星・日韓基本条約**\n「通信革命」と「外交の節目」が重なり、現在の国際社会の基礎ができました。",
    1969: "**アポロ11号が月面着陸成功**\n人類の活動範囲が宇宙へと広がった、テクノロジーの極致といえる年です。",
    1985: "**つくば万博・プラザ合意**\nハイテク技術への期待と、日本経済の大きな転換点が訪れた年です。",
    1991: "**バブル崩壊・インターネットの一般開放**\n一つの時代が終わり、デジタルという新しい波が押し寄せた分岐点です。",
    1995: "**Windows 95発売・阪神淡路大震災**\nIT革命の幕開けと、社会のあり方を問い直す大きな出来事が重なりました。",
    2024: "**新紙幣発行・生成AIの爆発普及**\n経済の象徴が変わると同時に、知能の定義が書き換わり始めた年です。",
    2025: "**大阪・関西万博・AGI（汎用人工知能）の進展**\n命を輝かせる未来社会のデザインと、AIとの共生が本格化した年です。"
}

# 登録されている年をリストにして、小さい順に並べる
available_years = sorted(list(history_db.keys()))

# 3. サイドバーの設定
st.sidebar.title("🎮 操作パネル")
search_query = st.sidebar.text_input("🔍 ニュース検索キーワード", value="人工知能")

# 【修正ポイント】辞書にある年だけをスライダーの選択肢にする
target_past_year = st.sidebar.select_slider(
    "⏳ 調査する「過去の年」を選択",
    options=available_years,
    value=1965  # 初期値
)

# 選択された年から60年後を計算
target_future_cycle = target_past_year + 60
prediction_year = target_future_cycle + 1

# 4. メイン画面
st.title(f"🕰️ 歴史の輪廻：{target_past_year}年 ↔ {target_future_cycle}年")
st.write(f"データが存在する特定の年代のみを抽出しています。")

# --- セクション1: 歴史のリスト ---
st.header(f"🔄 繰り返す歴史のサイクル")
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"🗓️ {target_past_year}年")
    st.info(history_db[target_past_year])

with col2:
    st.subheader(f"🗓️ {target_future_cycle}年")
    # 60年後のデータが辞書にあればそれを出し、なければ計算上のメッセージを出す
    if target_future_cycle in history_db:
        st.success(history_db[target_future_cycle])
    else:
        st.success(f"**歴史の螺旋（{target_future_cycle}年）**\n{target_past_year}年の出来事から60年が経過。歴史のサイクルが一周し、新しい進化が起きる年です。")

# --- セクション2: 未来予想 ---
st.header(f"🔮 {prediction_year}年 未来予想")
st.warning(f"**【{prediction_year}年の展望】**\n{target_future_cycle}年の大きな変化を受けて、この年は社会の「新しい常識」が定着するタイミングです。過去のサイクルを分析すると、ここから次の60年の基盤が作られます。")

# --- セクション3: 最新ニュース ---
st.header(f"📰 最新ニュース: {search_query}")
encoded = urllib.parse.quote(search_query)
feed = feedparser.parse(f"https://news.google.com/rss/search?q={encoded}&hl=ja&gl=JP&ceid=JP:ja")

for entry in feed.entries[:6]:
    st.markdown(f'''
        <div style="background:#f0f2f6; padding:15px; border-radius:10px; border-left:5px solid #ff4b4b; margin-bottom:10px;">
            <strong style="color:#333;">{entry.title}</strong>
        </div>
    ''', unsafe_allow_html=True)
    st.link_button("記事を読む", entry.link)
