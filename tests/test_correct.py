import json
import os
from unittest.mock import patch, MagicMock
from yap.correct import (
    llm_correct,
    _correct_claude_api,
    _correct_openai,
    _correct_gemini,
)


def test_llm_correct_no_provider():
    assert llm_correct("hello wrold", None) == "hello wrold"


def test_llm_correct_unknown_provider():
    assert llm_correct("hello wrold", "unknown") == "hello wrold"


def test_llm_correct_exception_returns_original(capsys):
    with patch("yap.correct._correct_claude_api", side_effect=RuntimeError("boom")):
        result = llm_correct("hello wrold", "claude")
        assert result == "hello wrold"
        captured = capsys.readouterr()
        assert "LLM correction failed" in captured.err


def _mock_urlopen(response_body):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_body).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def test_correct_claude_api():
    body = {"content": [{"text": "hello world"}]}
    with (
        patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}),
        patch("yap.correct.urlopen", return_value=_mock_urlopen(body)),
    ):
        result = _correct_claude_api("hello wrold")
        assert result == "hello world"


def test_correct_openai():
    body = {"choices": [{"message": {"content": "hello world"}}]}
    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}),
        patch("yap.correct.urlopen", return_value=_mock_urlopen(body)),
    ):
        result = _correct_openai("hello wrold")
        assert result == "hello world"


def test_correct_gemini():
    body = {"candidates": [{"content": {"parts": [{"text": "hello world"}]}}]}
    with (
        patch.dict(os.environ, {"GEMINI_API_KEY": "AI-test"}),
        patch("yap.correct.urlopen", return_value=_mock_urlopen(body)),
    ):
        result = _correct_gemini("hello wrold")
        assert result == "hello world"
