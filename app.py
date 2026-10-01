import streamlit as st
import feedparser
import urllib.parse
from pathlib import Path
import streamlit.components.v1 as components

# 1. ページ設定（和風なタイトル）
st.set_page_config(page_title="六十路の古年譜・預言書", layout="wide")

# ブラウザの端末時刻を取得し、取得後に描画する。
browser_year = components.declare_component(
    "browser_year", path=str(Path(__file__).parent / "browser_year")
)
current_year = browser_year(key="browser_year", default=None)
if current_year is None:
    st.info("ブラウザの現在年を取得しています。")
    st.stop()
if type(current_year) is not int or not 1900 <= current_year <= 9999:
    st.error("ブラウザの年を取得できません。端末の日付設定を確認してください。")
    st.stop()

past_start_year = current_year - 80
past_end_year = current_year - 60

# カスタムCSSで「古文書風」のデザインを適用
st.markdown("""
    <style>
    /* 全体の背景色を和紙風に */
    .main {
        background-color: #f4eade;
    }
    /* テキストの色を墨色に */
    h1, h2, h3, p, span, label {
        color: #2b2b2b !important;
        font-family: "Sawarabi Mincho", "Hiragino Mincho ProN", serif;
    }
    /* 枠線の装飾 */
    .stAlert {
        border: 2px solid #8b4513 !important;
        background-color: #fdf5e6 !important;
    }
    /* サイドバーの色 */
    [data-testid="stSidebar"] {
        background-color: #e0d5c1;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 歴史データベース（60年の因果関係を強化）
# 形式: { 過去年: (過去の出来事, 60年後のシンクロ理由) }
history_db = {
    1945: ("【終戦】国家の再建が始まる", "2005:【愛知万博】「自然の叡智」を掲げ、戦後60年で技術と自然の共生を世界へ示した。"),
    1946: ("【新憲法】国の「形」が決定", "2006:【第1回WBC】新しい日本の「誇り」がスポーツを通じて世界で証明された。"),
    1947: ("【給食開始】次世代の育成へ", "2007:【iPhone登場】教育と情報の形を根底から変える「魔法の杖」が普及し始めた。"),
    1953: ("【テレビ放送】情報の視覚化", "2013:【富士山世界遺産】日本の「象徴」が改めて世界に再定義された情報の転換期。"),
    1954: ("【ゴジラ】核の恐怖の具現化", "2014:【青色LED】「光」による革命。負のエネルギーへの懸念から、正の光の技術へ。"),
    1958: ("【東京タワー】高度成長の象徴", "2018:【大谷翔平】個の力が「塔」のように高く、世界から注目を浴びる象徴となった。"),
    1961: ("【人類初の宇宙へ】外の世界へ", "2021:【東京五輪】コロナ禍で「人類が繋がること」の意義を再び宇宙規模で問うた。"),
    1964: ("【前回の東京五輪】復興の証", "2024:【新紙幣・生成AI】経済の顔が変わり、人間以上の「知」が社会に浸透する新時代。"),
    1965: ("【日韓条約】外交の正常化", "2025:【大阪万博】「命の輝き」を掲げ、国境を超えた新たな人類共生を模索する。")
}

# 3. 今年の未来預言（古文・口語混じりの怪しい雰囲気）
predictions = [
    "「個の帝国」成る。一人の知が万の軍勢に匹敵する、稀有な年となるであろう。",
    "「言葉の壁」瓦解す。異国の民と意を通じるに、もはや術は不要なり。",
    "「空飛ぶ籠」街を往来せん。地上の喧騒を離れ、道は天へと伸びる。",
    "「機械の病治」確立。人の身に宿る不調、AIが瞬時に見抜き、癒やしをもたらさん。",
    "「虚実の境界」消失。夢か現か、メタバースなる鏡写しの世界が真実を凌駕せん。",
    "「宇宙の門」開く。富める者のみならず、民が星の海を渡る端緒となる年なり。",
    "「智慧の共有」加速。学びの場は四方の壁を失い、全人類が等しく知を得る。",
    "「自動の労働」定着。汗して働く意味、再定義されん。創造こそが人の本分となる。",
    "「無形なる貨幣」完成。紙に拠らぬ信用、万民の手に渡り、富の形が書き換わる。",
    "「感官の通信」成る。触れずして温もりを知り、味わわずして旨味を知る術、現れん。"
]

# 過去の出来事に対応する予言の主題（創作）
prediction_themes = {
    1945: 7, 1946: 8, 1947: 6, 1953: 9, 1954: 3,
    1958: 2, 1961: 5, 1964: 0, 1965: 1,
}

# 4. サイドバー
st.sidebar.title("📜 観測の栞")
search_query = st.sidebar.text_input("🔍 現在の動向（検索）", value="人工知能")
available_years = [
    year for year in history_db if past_start_year <= year <= past_end_year
]
target_past_year = st.sidebar.select_slider(
    f"⏳ 遡るべき年（{past_start_year}〜{past_end_year}年／80〜60年前）",
    options=list(range(past_start_year, past_end_year + 1)),
    value=max(available_years) if available_years else past_end_year,
    key=f"past_year_{current_year}",
)
st.sidebar.caption(f"ブラウザの現在年：{current_year}年")

# 5. メイン画面
st.markdown(f"# 🕰️ 歴史の連環：{target_past_year}年 ↔ {current_year}年")
st.write("―― 歴史は螺旋の如く、巡りて再び現る。")
st.caption(f"{current_year}年の80〜60年前（{past_start_year}〜{past_end_year}年）を参照")

st.header("🔄 シンクロニシティ（因果の結び目）")
col1, col2 = st.columns(2)
history = history_db.get(target_past_year)
with col1:
    st.markdown(f"### 🕯️ 過去：{target_past_year}年（{current_year - target_past_year}年前）")
    if history:
        st.info(history[0])
    else:
        st.info("この年の歴史データは未登録です。登録済みの年を選んでください。")

with col2:
    st.markdown(f"### ☀️ 今年：{current_year}年")
    if history:
        st.success(
            f"{target_past_year}年の「{history[0]}」を手掛かりに、"
            f"{current_year}年の変化を読み解きます。"
        )
        with st.expander("参考：過去の60年周期の対応"):
            st.write(history[1])
    else:
        st.write("歴史データが登録されると、この年を基に今年の予言を表示します。")

st.write("---")
st.header(f"🔮 {current_year}年 預言之書")
if history:
    selected_prediction = predictions[prediction_themes[target_past_year]]
    st.warning(
        f"**{target_past_year}年を手掛かりに、{current_year}年に起こると想像する事象：**"
        f"\n\n{selected_prediction}"
    )
    st.caption("過去の出来事を主題にした創作の予言です。")
else:
    st.info("選択した年の歴史データがないため、予言を生成できません。")
if not available_years:
    st.info(f"参照範囲（{past_start_year}〜{past_end_year}年）の歴史データを追加してください。")

# --- ニュース ---
st.header(f"📰 現在の瓦版（最新ニュース）")
encoded = urllib.parse.quote(search_query)
feed = feedparser.parse(f"https://news.google.com/rss/search?q={encoded}&hl=ja&gl=JP&ceid=JP:ja")

for entry in feed.entries[:5]:
    st.markdown(f'''
        <div style="background-color: #fdf5e6; padding: 10px; border-bottom: 1px solid #8b4513; margin-bottom: 10px;">
            <span style="font-weight: bold;">◆ {entry.title}</span>
        </div>
    ''', unsafe_allow_html=True)
    st.link_button("詳しく読む", entry.link)
