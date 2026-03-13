import html
import os

import streamlit as st
from sentence_transformers import SentenceTransformer
from supabase import Client, create_client


st.set_page_config(
    page_title="NAN Aesthetics RAG",
    page_icon="✨",
    layout="wide",
)


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #fffaf6;
                --surface: rgba(255, 250, 246, 0.82);
                --surface-strong: rgba(255, 255, 255, 0.92);
                --border: rgba(201, 167, 141, 0.32);
                --text: #4e423f;
                --muted: #7d6b66;
                --rose: #dca79a;
                --rose-deep: #bf8274;
                --gold: #d7b98b;
                --shadow: 0 24px 60px rgba(191, 130, 116, 0.13);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(247, 223, 216, 0.85), transparent 32%),
                    radial-gradient(circle at top right, rgba(244, 230, 204, 0.7), transparent 28%),
                    linear-gradient(180deg, #fffdfa 0%, #fff8f3 42%, #fffaf6 100%);
                color: var(--text);
            }

            [data-testid="stHeader"] {
                background: rgba(255, 255, 255, 0);
            }

            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(255, 248, 243, 0.96) 0%, rgba(255, 253, 249, 0.94) 100%);
                border-right: 1px solid var(--border);
            }

            [data-testid="stSidebar"] > div:first-child {
                padding-top: 2rem;
            }

            div[data-baseweb="input"] > div,
            div[data-baseweb="textarea"] > div {
                border-radius: 18px !important;
                border: 1px solid rgba(201, 167, 141, 0.35) !important;
                background: rgba(255, 255, 255, 0.8) !important;
            }

            .stTextInput label,
            .stSlider label {
                color: var(--text) !important;
                font-weight: 600 !important;
            }

            .stButton > button {
                border-radius: 999px;
                min-height: 3rem;
                border: none;
                color: white;
                font-weight: 700;
                background: linear-gradient(135deg, #c9867a 0%, #dca79a 52%, #e7c4a1 100%);
                box-shadow: 0 18px 35px rgba(201, 134, 122, 0.22);
            }

            .stButton > button:hover {
                filter: brightness(1.02);
                transform: translateY(-1px);
            }

            .hero-shell {
                padding: 2.6rem 2.8rem;
                border-radius: 30px;
                background:
                    linear-gradient(135deg, rgba(255, 255, 255, 0.88), rgba(255, 247, 241, 0.92)),
                    linear-gradient(135deg, rgba(220, 167, 154, 0.10), rgba(215, 185, 139, 0.12));
                border: 1px solid var(--border);
                box-shadow: var(--shadow);
                overflow: hidden;
                position: relative;
            }

            .hero-shell::after {
                content: "";
                position: absolute;
                inset: auto -80px -120px auto;
                width: 240px;
                height: 240px;
                border-radius: 999px;
                background: radial-gradient(circle, rgba(220, 167, 154, 0.16), transparent 70%);
            }

            .eyebrow {
                display: inline-block;
                padding: 0.42rem 0.9rem;
                border-radius: 999px;
                background: rgba(220, 167, 154, 0.16);
                color: var(--rose-deep);
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .hero-title {
                margin: 1rem 0 0.7rem 0;
                font-size: 3rem;
                line-height: 1.1;
                color: #5b4641;
            }

            .hero-copy {
                max-width: 760px;
                color: var(--muted);
                font-size: 1.04rem;
                line-height: 1.85;
            }

            .pill-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.75rem;
                margin-top: 1.4rem;
            }

            .pill {
                padding: 0.78rem 1rem;
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid rgba(201, 167, 141, 0.26);
                color: var(--text);
                font-size: 0.95rem;
            }

            .section-card {
                margin-top: 1.4rem;
                padding: 1.35rem 1.4rem;
                border-radius: 24px;
                border: 1px solid var(--border);
                background: var(--surface);
                box-shadow: 0 16px 36px rgba(124, 90, 77, 0.07);
            }

            .section-title {
                margin: 0 0 0.35rem 0;
                color: #5b4641;
                font-size: 1.15rem;
                font-weight: 700;
            }

            .section-copy {
                margin: 0;
                color: var(--muted);
                line-height: 1.8;
            }

            .sidebar-card {
                padding: 1.15rem 1rem;
                border-radius: 22px;
                border: 1px solid rgba(201, 167, 141, 0.26);
                background: rgba(255, 255, 255, 0.7);
                box-shadow: 0 14px 30px rgba(124, 90, 77, 0.06);
            }

            .sidebar-title {
                margin: 0;
                color: #5b4641;
                font-size: 1.02rem;
                font-weight: 700;
            }

            .sidebar-copy {
                margin: 0.55rem 0 0 0;
                color: var(--muted);
                font-size: 0.93rem;
                line-height: 1.7;
            }

            .result-card {
                padding: 1.3rem 1.35rem;
                border-radius: 24px;
                border: 1px solid rgba(201, 167, 141, 0.24);
                background: rgba(255, 255, 255, 0.80);
                box-shadow: 0 16px 40px rgba(124, 90, 77, 0.08);
            }

            .result-head {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                margin-bottom: 0.9rem;
            }

            .result-rank {
                color: #bf8274;
                font-size: 0.85rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .result-score {
                padding: 0.35rem 0.72rem;
                border-radius: 999px;
                background: rgba(220, 167, 154, 0.16);
                color: #a26557;
                font-size: 0.84rem;
                font-weight: 700;
            }

            .result-label {
                margin: 0.95rem 0 0.35rem 0;
                color: #8e6f68;
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .result-text {
                margin: 0;
                color: var(--text);
                line-height: 1.9;
            }

            .empty-card {
                padding: 1.6rem 1.45rem;
                border-radius: 24px;
                border: 1px dashed rgba(201, 167, 141, 0.45);
                background: rgba(255, 255, 255, 0.58);
                text-align: center;
                color: var(--muted);
                line-height: 1.9;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_secret(name: str) -> str:
    if name in st.secrets:
        return str(st.secrets[name])

    value = os.getenv(name)
    if value:
        return value

    raise KeyError(name)


@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Client:
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")
    return create_client(url, key)


@st.cache_resource(show_spinner="正在喚醒醫美知識庫，請稍候片刻...")
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def build_query_embedding(query: str) -> list[float]:
    prompt = f"為這段醫美客服問題建立檢索向量：{query.strip()}"
    return get_model().encode(prompt).tolist()


def search_qa(query: str, match_count: int) -> list[dict]:
    supabase = get_supabase_client()
    query_embedding = build_query_embedding(query)
    response = supabase.rpc(
        "match_qa",
        {
            "query_embedding": query_embedding,
            "match_count": match_count,
        },
    ).execute()
    return response.data or []


def render_hero() -> None:
    st.markdown(
        """
        <section class="hero-shell">
            <span class="eyebrow">NAN Aesthetics Knowledge Concierge</span>
            <h1 class="hero-title">醫美顧問問答，像接待現場一樣柔和又專業。</h1>
            <p class="hero-copy">
                這個展示頁把 RAG 查詢包裝成更有醫美氛圍的體驗，讓廠商一進來就能感受到
                「溫暖、安心、精緻」的品牌氣質，同時快速看到知識檢索的速度與準確度。
            </p>
            <div class="pill-row">
                <div class="pill">療程諮詢語氣更自然</div>
                <div class="pill">問答結果更適合現場 demo</div>
                <div class="pill">適合醫美客服與顧問知識庫展示</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_intro_panels() -> None:
    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.markdown(
            """
            <div class="section-card">
                <p class="section-title">展示建議情境</p>
                <p class="section-copy">
                    可以直接輸入顧客常問的療程、安全性、恢復期、價格帶或術後照護問題，
                    讓廠商快速理解這套系統如何協助第一線回應更一致、更即時。
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="section-card">
                <p class="section-title">推薦提問方向</p>
                <p class="section-copy">
                    例如：玻尿酸維持多久、皮秒雷射恢復期、電音波差異、術前注意事項、
                    術後保養禁忌、療程適合族群。
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_result_card(index: int, item: dict) -> None:
    question = item.get("question", "未提供問題")
    answer = item.get("answer", "未提供答案")
    escaped_question = html.escape(str(question))
    escaped_answer = html.escape(str(answer))
    similarity = item.get("similarity")
    similarity_html = ""
    if similarity is not None:
        similarity_html = f'<div class="result-score">相似度 {similarity:.4f}</div>'

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-head">
                <div class="result-rank">Top {index}</div>
                {similarity_html}
            </div>
            <p class="result-label">顧客問題</p>
            <p class="result-text">{escaped_question}</p>
            <p class="result-label">知識庫回答</p>
            <p class="result-text">{escaped_answer}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_styles()
    render_hero()
    render_intro_panels()

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-card">
                <p class="sidebar-title">展示模式</p>
                <p class="sidebar-copy">
                    這頁偏向廠商 demo 與提案情境，強調溫暖感、信任感與醫美品牌氣質。
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        match_count = st.slider("顯示幾筆最相關結果", min_value=1, max_value=5, value=3)
        st.caption("請先在 Streamlit Secrets 或環境變數中設定 `SUPABASE_URL` 與 `SUPABASE_KEY`。")

    st.markdown("")
    st.markdown(
        """
        <div class="section-card">
            <p class="section-title">開始模擬顧客提問</p>
            <p class="section-copy">
                輸入一個醫美顧客會問的真實問題，看看系統如何從知識庫中找到最貼近的回答。
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("search_form"):
        query = st.text_input(
            "想查詢什麼問題？",
            placeholder="例如：音波拉提做完多久可以上妝？",
        )
        search_clicked = st.form_submit_button("開始查詢", use_container_width=True)

    if not search_clicked:
        st.markdown(
            """
            <div class="empty-card">
                輸入問題後就能看到知識庫回傳結果。<br>
                這個版面已經調整成更適合對外展示的醫美風格，你可以直接拿來 demo。
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if not query.strip():
        st.warning("請先輸入想查詢的醫美問題。")
        return

    try:
        with st.spinner("正在比對最合適的醫美知識內容..."):
            results = search_qa(query, match_count)
    except KeyError as exc:
        st.error(f"缺少必要設定：{exc.args[0]}。請補上 Streamlit Secrets 或環境變數。")
        return
    except Exception as exc:
        st.error(f"查詢時發生錯誤：{exc}")
        return

    st.markdown("")
    if not results:
        st.info("目前沒有找到相符結果，可能需要確認向量資料、RPC 函式或 QA 資料是否已正確建立。")
        return

    st.success(f"已找到 {len(results)} 筆相近內容。")
    for index, item in enumerate(results, start=1):
        render_result_card(index, item)
        st.write("")


if __name__ == "__main__":
    main()
