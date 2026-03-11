from unittest.mock import patch, MagicMock
from yap.transcribe import transcribe


def test_transcribe_returns_text():
    mock_model = MagicMock()
    mock_segment = MagicMock()
    mock_segment.text = "Hello world"
    mock_model.transcribe.return_value = ([mock_segment], None)

    with patch("yap.transcribe.WhisperModel", return_value=mock_model):
        result = transcribe("/tmp/test.wav", model_size="tiny.en")

    assert result == "Hello world"


def test_transcribe_empty_returns_empty():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = ([], None)

    with patch("yap.transcribe.WhisperModel", return_value=mock_model):
        result = transcribe("/tmp/test.wav", model_size="tiny.en")

    assert result == ""


def test_transcribe_multi_segment():
    mock_model = MagicMock()
    seg1 = MagicMock()
    seg1.text = " Hello"
    seg2 = MagicMock()
    seg2.text = " world"
    mock_model.transcribe.return_value = ([seg1, seg2], None)

    with patch("yap.transcribe.WhisperModel", return_value=mock_model):
        result = transcribe("/tmp/test.wav", model_size="tiny.en")

    assert result == "Hello world"


def test_transcribe_caches_model():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = ([], None)

    with patch("yap.transcribe.WhisperModel", return_value=mock_model) as mock_cls:
        transcribe("/tmp/test.wav", model_size="tiny.en")
        transcribe("/tmp/test.wav", model_size="tiny.en")
        assert mock_cls.call_count == 1


def test_transcribe_passes_language():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = ([], None)

    with patch("yap.transcribe.WhisperModel", return_value=mock_model):
        transcribe("/tmp/test.wav", model_size="tiny.en", language="zh")
        call_kwargs = mock_model.transcribe.call_args[1]
        assert call_kwargs["language"] == "zh"


def test_transcribe_omits_language_when_none():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = ([], None)

    with patch("yap.transcribe.WhisperModel", return_value=mock_model):
        transcribe("/tmp/test.wav", model_size="tiny.en")
        call_kwargs = mock_model.transcribe.call_args[1]
        assert "language" not in call_kwargs
