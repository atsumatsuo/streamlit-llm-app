import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

def show_debug():
    import importlib.metadata as md  # ← 関数内で確実に定義
    st.sidebar.header("🛠 Debug")

    def ver(name: str):
        try:
            return md.version(name)
        except Exception:
            return "(not installed)"

    # バージョン表示
    st.sidebar.write({
        "streamlit": ver("streamlit"),
        "openai": ver("openai"),
        "langchain": ver("langchain"),
        "langchain-openai": ver("langchain-openai"),
        "httpx": ver("httpx"),
    })

    # プロキシ系環境変数の有無を表示（値があるものだけ）
    keys = [
        "HTTP_PROXY","HTTPS_PROXY","ALL_PROXY",
        "http_proxy","https_proxy","all_proxy",
        "OPENAI_PROXY","PROXIES","proxies"
    ]
    st.sidebar.subheader("Proxy envs (set only)")
    st.sidebar.json({k: os.environ.get(k) for k in keys if os.environ.get(k)})


# チェックボックスでON/OFFできるように
if st.sidebar.checkbox("Show debug info", value=True):
    show_debug()

# --- ① .env 読み込み（ローカル用） ---
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# --- ② プロキシ環境変数を無効化（不要なら全部カット） ---
for k in ["HTTP_PROXY","HTTPS_PROXY","ALL_PROXY","http_proxy","https_proxy","all_proxy","OPENAI_PROXY","PROXIES","proxies"]:
    os.environ.pop(k, None)

# --- ③ APIキー取得（ローカル=.env / 本番=Secrets の両対応） ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OpenAI APIキーがありません（.env か Secrets を設定してください）")
    st.stop()

from openai import OpenAI
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

import importlib.metadata as md

# --- ④ OpenAI公式クライアントを自分で作って ChatOpenAI に渡す ---
# プロキシが不要ならそのまま
oai = OpenAI(api_key=OPENAI_API_KEY)

# （社内プロキシが必須の人だけ）
# http_client = httpx.Client(proxies="http://proxy.example.com:8080")
# oai = OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)

EXPERT_SYSTEM_MESSAGES = {
    "健康": "あなたは健康分野の専門家です。ユーザーの健康に関する質問に専門的かつ分かりやすく答えてください。",
    "お金": "あなたは金融分野の専門家です。ユーザーのお金や投資に関する質問に専門的かつ分かりやすく答えてください。",
    "キャリア": "あなたはキャリアコンサルタントです。ユーザーの仕事やキャリアに関する相談に親身に答えてください。",
    "教育": "あなたは教育分野の専門家です。ユーザーの学習や教育に関する質問に分かりやすく答えてください。"
}

def get_llm_response(input_text: str, expert_type: str) -> str:
    system_message = EXPERT_SYSTEM_MESSAGES.get(expert_type, "あなたは優秀なアシスタントです。")
    chat = ChatOpenAI(
        model="gpt-3.5-turbo",   # 例：軽めのモデル。必要に応じて変更OK
        temperature=0.7,
        client=oai               # ← ここが肝。自前の OpenAI クライアントを渡す
    )
    messages = [SystemMessage(content=system_message), HumanMessage(content=input_text)]
    resp = chat.invoke(messages)
    return resp.content

st.title("専門家AI相談アプリ")

expert_type = st.radio("相談したい専門家を選んでください", list(EXPERT_SYSTEM_MESSAGES.keys()))
input_text = st.text_area("質問を入力してください")

if st.button("送信"):
    if input_text.strip():
        try:
            with st.spinner("AIが回答中..."):
                answer = get_llm_response(input_text, expert_type)
            st.markdown("### 回答")
            st.write(answer)
        except Exception as e:
            st.error(f"AIの回答取得中にエラーが発生しました: {e}")
    else:
        st.warning("質問を入力してください。")
