import streamlit as st
import os
import hashlib
import json
from urllib.request import Request, urlopen
from urllib.error import URLError
from history_ai import fetch_history, generate_prediction, ServiceError, USER_AGENT
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

# サーバー側のSecretsまたは環境変数で設定する。
def setting(name, default=""):
    value = os.environ.get(name)
    if value:
        return value
    try:
        return str(st.secrets.get(name, default))
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return default


st.sidebar.title("📜 観測の栞")
search_query = st.sidebar.text_input("🔍 関心テーマ・ニュース検索", value="人工知能", max_chars=200)
target_past_year = st.sidebar.select_slider(
    f"⏳ 遡るべき年（{past_start_year}〜{past_end_year}年／80〜60年前）",
    options=list(range(past_start_year, past_end_year + 1)),
    value=past_end_year,
    key=f"past_year_{current_year}",
)
st.sidebar.caption(f"ブラウザの現在年：{current_year}年")
refresh = st.sidebar.button("🔄 歴史を再取得して予言を生成")
st.sidebar.caption("表示・年の変更・再取得のたびに、選択した年の歴史を取得します。")

st.markdown(f"# 🕰️ 歴史の連環：{target_past_year}年 ↔ {current_year}年")
st.write("―― 歴史は螺旋の如く、巡りて再び現る。")
st.caption(f"{current_year}年の80〜60年前（{past_start_year}〜{past_end_year}年）を参照")
history = None
try:
    with st.spinner(f"{target_past_year}年の歴史を取得しています…"):
        history = fetch_history(target_past_year)
except ServiceError as exc:
    st.error(str(exc))

st.header("📜 過去の出来事")
if history:
    st.subheader(f"{target_past_year}年（{current_year - target_past_year}年前）")
    for number, event in enumerate(history["events"], 1):
        st.write(f"[{number}] {event}")
    st.link_button("出典：Wikipedia（取得した版）", history["revision_url"])
    st.caption(
        f"取得時刻（UTC）：{history['retrieved_at']} ／ "
        "Wikipedia「出来事」節より抜粋。CC BY-SA。内容は出典で確認できます。"
    )

st.write("---")
st.header(f"🔮 {current_year}年 AI預言之書")
st.caption("取得した歴史を手掛かりにAIが考える創作の仮説です。")
api_key = setting("OPENAI_API_KEY")
model = setting("OPENAI_MODEL", "gpt-6-sol")
if not api_key:
    st.info("AI予言を有効にするには、アプリのSecretsにOPENAI_API_KEYを設定してください。")
elif history:
    # 同じ入力での画面操作では課金を繰り返さない。新しい歴史・年・主題で更新する。
    fingerprint = hashlib.sha256(json.dumps({
        "current_year": current_year, "past_year": target_past_year,
        "events": history["events"], "revision": history["revision"],
        "topic": search_query, "model": model,
    }, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    cached = st.session_state.get("ai_prediction")
    if refresh or not cached or cached["fingerprint"] != fingerprint:
        try:
            with st.spinner("AIが今年の予言を考えています…"):
                prediction = generate_prediction(current_year, history, search_query, api_key, model)
            cached = {"fingerprint": fingerprint, "text": prediction}
            st.session_state["ai_prediction"] = cached
        except ServiceError as exc:
            st.error(str(exc))
            cached = None
    if cached and cached["fingerprint"] == fingerprint:
        st.markdown(cached["text"])
        st.caption("同じ資料の予言は再利用します。新しく考え直すにはサイドバーの再取得ボタンを押してください。")
else:
    st.info("歴史データを取得できたら、その内容から予言を生成します。")

# --- ニュース ---
st.header(f"📰 現在の瓦版（最新ニュース）")
encoded = urllib.parse.quote(search_query)
try:
    request = Request(
        f"https://news.google.com/rss/search?q={encoded}&hl=ja&gl=JP&ceid=JP:ja",
        headers={"User-Agent": USER_AGENT},
    )
    with urlopen(request, timeout=15) as response:
        feed = feedparser.parse(response.read())
    for entry in feed.entries[:5]:
        st.write(f"◆ {entry.title}")
        if urllib.parse.urlparse(entry.link).scheme in ("https", "http"):
            st.link_button("詳しく読む", entry.link)
except (URLError, TimeoutError, OSError):
    st.info("ニュースを取得できません。時間をおいて再試行してください。")
