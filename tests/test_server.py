import json
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_handle_correct_message():
    """LLM correction via WebSocket message."""
    from yap.server import handle_message

    msg = json.dumps({"type": "correct", "text": "hello wrold", "provider": "openai"})
    with patch("yap.server.llm_correct", return_value="hello world") as mock_correct:
        result = await handle_message(msg)
    parsed = json.loads(result)
    assert parsed["type"] == "corrected"
    assert parsed["text"] == "hello world"
    mock_correct.assert_called_once_with("hello wrold", "openai")


@pytest.mark.asyncio
async def test_handle_transcribe_message(tmp_path):
    """Local Whisper transcription via WebSocket."""
    from yap.server import handle_audio_message

    fake_audio = b"\x00" * 100
    with (
        patch("yap.server.transcribe", return_value="hello world"),
        patch("yap.server.TMPDIR", str(tmp_path)),
        patch("yap.server.subprocess.run"),
    ):
        result = await handle_audio_message(
            fake_audio, {"model": "small.en", "language": None}
        )
    parsed = json.loads(result)
    assert parsed["type"] == "transcription"
    assert parsed["text"] == "hello world"


@pytest.mark.asyncio
async def test_handle_clipboard_message():
    """Copy-to-clipboard via WebSocket message."""
    from yap.server import handle_message

    msg = json.dumps({"type": "clipboard", "text": "hello"})
    with patch("yap.server.copy_to_clipboard") as mock_clip:
        result = await handle_message(msg)
    parsed = json.loads(result)
    assert parsed["type"] == "copied"
    mock_clip.assert_called_once_with("hello")


@pytest.mark.asyncio
async def test_handle_unknown_message_type():
    """Unknown message types return an error."""
    from yap.server import handle_message

    msg = json.dumps({"type": "unknown"})
    result = await handle_message(msg)
    parsed = json.loads(result)
    assert parsed["type"] == "error"
