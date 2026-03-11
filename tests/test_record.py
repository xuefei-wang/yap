import os
import signal
import subprocess
from unittest.mock import patch, MagicMock
from yap.record import (
    get_ffmpeg_input_args,
    start_recording,
    cleanup_audio,
    stop_recording,
)


def test_ffmpeg_args_linux():
    with patch("platform.system", return_value="Linux"):
        args = get_ffmpeg_input_args()
        assert args == ["-f", "pulse", "-i", "default"]


def test_ffmpeg_args_macos():
    with patch("platform.system", return_value="Darwin"):
        args = get_ffmpeg_input_args()
        assert args == ["-f", "avfoundation", "-i", ":default"]


def test_ffmpeg_args_windows():
    with patch("platform.system", return_value="Windows"):
        args = get_ffmpeg_input_args()
        assert args[0:2] == ["-f", "dshow"]
        assert "-i" in args


def test_cleanup_audio(tmp_path):
    audio = str(tmp_path / "recording.wav")
    with open(audio, "w") as f:
        f.write("fake")
    with patch("yap.record.AUDIO_PATH", audio):
        cleanup_audio()
        assert not os.path.exists(audio)


def test_cleanup_audio_missing(tmp_path):
    audio = str(tmp_path / "recording.wav")
    with patch("yap.record.AUDIO_PATH", audio):
        cleanup_audio()  # should not raise


def test_stop_recording_timeout():
    proc = MagicMock()
    proc.wait.side_effect = [subprocess.TimeoutExpired(cmd="ffmpeg", timeout=10), None]
    proc.kill.return_value = None
    stop_recording(proc)
    proc.send_signal.assert_called_once_with(signal.SIGTERM)
    proc.kill.assert_called_once()


def test_start_recording_windows_uses_pipe_stdin():
    with (
        patch("platform.system", return_value="Windows"),
        patch(
            "yap.record.get_ffmpeg_input_args",
            return_value=["-f", "dshow", "-i", "audio=default"],
        ),
        patch("subprocess.Popen") as mock_popen,
        patch("os.makedirs"),
    ):
        start_recording()
        _, kwargs = mock_popen.call_args
        assert kwargs.get("stdin") == subprocess.PIPE


def test_start_recording_unix_uses_devnull():
    with (
        patch("platform.system", return_value="Linux"),
        patch(
            "yap.record.get_ffmpeg_input_args",
            return_value=["-f", "pulse", "-i", "default"],
        ),
        patch("subprocess.Popen") as mock_popen,
        patch("os.makedirs"),
    ):
        start_recording()
        _, kwargs = mock_popen.call_args
        assert kwargs.get("stdin") == subprocess.DEVNULL


def test_stop_recording_windows_writes_q():
    proc = MagicMock()
    proc.stdin = MagicMock()
    proc.wait.return_value = 0
    with patch("platform.system", return_value="Windows"):
        stop_recording(proc)
    proc.stdin.write.assert_called_once_with(b"q\n")
    proc.stdin.flush.assert_called_once()
    proc.send_signal.assert_not_called()


def test_stop_recording_unix_sends_sigterm():
    proc = MagicMock()
    proc.stdin = None
    proc.wait.return_value = 0
    with patch("platform.system", return_value="Linux"):
        stop_recording(proc)
    proc.send_signal.assert_called_once_with(signal.SIGTERM)
