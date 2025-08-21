

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Streamlit CloudのSecretsからAPIキーを取得
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")

# 専門家タイプごとのシステムメッセージ
EXPERT_SYSTEM_MESSAGES = {
    "健康": "あなたは健康分野の専門家です。ユーザーの健康に関する質問に専門的かつ分かりやすく答えてください。",
    "お金": "あなたは金融分野の専門家です。ユーザーのお金や投資に関する質問に専門的かつ分かりやすく答えてください。",
    "キャリア": "あなたはキャリアコンサルタントです。ユーザーの仕事やキャリアに関する相談に親身に答えてください。",
    "教育": "あなたは教育分野の専門家です。ユーザーの学習や教育に関する質問に分かりやすく答えてください。"
}



def get_llm_response(input_text: str, expert_type: str) -> str:
    system_message = EXPERT_SYSTEM_MESSAGES.get(expert_type, "あなたは優秀なアシスタントです。")
    chat = ChatOpenAI(
        model="gpt-4.0-mini",
        temperature=0.7,
        api_key=OPENAI_API_KEY
    )
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=input_text)
    ]
    response = chat.invoke(messages)
    return response.content



st.title("専門家AI相談アプリ")

# APIキー確認
if not OPENAI_API_KEY:
    st.error("OpenAI APIキーが設定されていません。環境変数または.envファイルを確認してください。")

expert_type = st.radio(
    "相談したい専門家を選んでください",
    list(EXPERT_SYSTEM_MESSAGES.keys())
)

input_text = st.text_area("質問を入力してください")

if st.button("送信"):
    if not OPENAI_API_KEY:
        st.error("OpenAI APIキーが設定されていません。")
    elif input_text.strip():
        try:
            with st.spinner("AIが回答中..."):
                answer = get_llm_response(input_text, expert_type)
            st.markdown("### 回答")
            st.write(answer)
        except Exception as e:
            st.error(f"AIの回答取得中にエラーが発生しました: {e}")
    else:
        st.warning("質問を入力してください。")