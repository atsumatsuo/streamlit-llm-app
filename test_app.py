import os
import pytest
from unittest.mock import patch, MagicMock
from app import get_llm_response, EXPERT_SYSTEM_MESSAGES

# Import the function to test

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

def test_get_llm_response_health(monkeypatch):
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "健康に関する回答"
    mock_chat.return_value = mock_response

    with patch("app.ChatOpenAI", return_value=mock_chat):
        result = get_llm_response("健康について教えて", "健康")
        assert result == "健康に関する回答"
        mock_chat.assert_called_once()

def test_get_llm_response_money(monkeypatch):
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "お金に関する回答"
    mock_chat.return_value = mock_response

    with patch("app.ChatOpenAI", return_value=mock_chat):
        result = get_llm_response("投資について教えて", "お金")
        assert result == "お金に関する回答"

def test_get_llm_response_default(monkeypatch):
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "デフォルトの回答"
    mock_chat.return_value = mock_response

    with patch("app.ChatOpenAI", return_value=mock_chat):
        result = get_llm_response("その他の質問", "未知の専門家")
        assert result == "デフォルトの回答"

def test_expert_system_messages_keys():
    expected_keys = {"健康", "お金", "キャリア", "教育"}
    assert set(EXPERT_SYSTEM_MESSAGES.keys()) == expected_keys