import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import importlib.metadata as md  # デバッグ用のバージョン表示に使う

# --- .env を読み込む（ローカル用。Cloudでは st.secrets を使う） ---
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# --- APIキー取得（ローカル=.env / 本番=Secrets の両対応） ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# --- 便利デバッグ（サイドバーに表示） ---
def show_debug():
    st.sidebar.header("🛠 Debug")

    def ver(name: str):
        try:
            return md.version(name)
        except Exception:
            return "(not installed)"

    st.sidebar.write({
        "streamlit": ver("streamlit"),
        "openai": ver("openai"),
        "langchain": ver("langchain"),
        "langchain-openai": ver("langchain-openai"),
        "httpx": ver("httpx"),
    })

    keys = [
        "HTTP_PROXY","HTTPS_PROXY","ALL_PROXY",
        "http_proxy","https_proxy","all_proxy",
        "OPENAI_PROXY","PROXIES","proxies",
    ]
    st.sidebar.subheader("Proxy envs (set only)")
    st.sidebar.json({k: os.environ.get(k) for k in keys if os.environ.get(k)})

# （必要なときだけチェックON）
if st.sidebar.checkbox("Show debug info", value=False):
    show_debug()

# --- ここからアプリ本体 ---
st.title("専門家AI相談アプリ")

# APIキーが無ければ止める（Cloud/ローカル共通）
if not OPENAI_API_KEY:
    st.error("OpenAI APIキーがありません。.env か Streamlit Secrets に設定してください。")
    st.stop()

# 専門家タイプごとのシステムメッセージ
EXPERT_SYSTEM_MESSAGES = {
    "健康": "あなたは健康分野の専門家です。ユーザーの健康に関する質問に専門的かつ分かりやすく答えてください。",
    "お金": "あなたは金融分野の専門家です。ユーザーのお金や投資に関する質問に専門的かつ分かりやすく答えてください。",
    "キャリア": "あなたはキャリアコンサルタントです。ユーザーの仕事やキャリアに関する相談に親身に答えてください。",
    "教育": "あなたは教育分野の専門家です。ユーザーの学習や教育に関する質問に分かりやすく答えてください。",
}

def get_llm_response(input_text: str, expert_type: str) -> str:
    system_message = EXPERT_SYSTEM_MESSAGES.get(expert_type, "あなたは優秀なアシスタントです。")
    # ★ v1系に合わせた正しい初期化：api_key だけ渡す（client/create は使わない）
    chat = ChatOpenAI(
        model="gpt-3.5-turbo",   # 必要なら "gpt-4o-mini" などに変更OK
        temperature=0.7,
        api_key=OPENAI_API_KEY,
    )
    messages = [SystemMessage(content=system_message), HumanMessage(content=input_text)]
    response = chat.invoke(messages)
    return response.content

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
