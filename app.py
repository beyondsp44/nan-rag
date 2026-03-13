import os

import streamlit as st
from sentence_transformers import SentenceTransformer
from supabase import Client, create_client


st.set_page_config(
    page_title="醫美 QA 檢索",
    page_icon="💬",
    layout="centered",
)


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"


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


@st.cache_resource(show_spinner="載入語意模型中，第一次會稍久一點...")
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def search_qa(query: str, match_count: int) -> list[dict]:
    model = get_model()
    supabase = get_supabase_client()
    query_text = f"問題：{query.strip()}\n答案："
    query_embedding = model.encode(query_text).tolist()
    response = supabase.rpc(
        "match_qa",
        {
            "query_embedding": query_embedding,
            "match_count": match_count,
        },
    ).execute()
    return response.data or []


st.title("醫美 QA 檢索")
st.caption("輸入問題後，系統會用詞向量到 Supabase 找最相近的問答。")

with st.sidebar:
    st.subheader("設定")
    match_count = st.slider("顯示幾筆結果", min_value=1, max_value=5, value=3)
    st.markdown(
        "需要在 Streamlit Secrets 設定：`SUPABASE_URL`、`SUPABASE_KEY`"
    )

query = st.text_input(
    "請輸入問題",
    placeholder="例如：醫美價格怎麼算？",
)

search_clicked = st.button("開始檢索", type="primary", use_container_width=True)

if search_clicked:
    if not query.strip():
        st.warning("請先輸入問題。")
    else:
        try:
            with st.spinner("檢索中..."):
                results = search_qa(query, match_count)
        except KeyError as exc:
            st.error(f"缺少設定：{exc.args[0]}。請到 Streamlit Secrets 補上。")
            st.stop()
        except Exception as exc:
            st.error(f"檢索失敗：{exc}")
            st.stop()

        if not results:
            st.info("目前查不到結果。請確認資料表已有 embedding，且 `match_qa` 函式已建立。")
        else:
            st.success(f"找到 {len(results)} 筆結果")
            for index, item in enumerate(results, start=1):
                similarity = item.get("similarity")
                with st.container(border=True):
                    st.markdown(f"### Top {index}")
                    st.write(f"**問題：** {item.get('question', '')}")
                    st.write(f"**答案：** {item.get('answer', '')}")
                    if similarity is not None:
                        st.caption(f"相似度：{similarity:.4f}")
