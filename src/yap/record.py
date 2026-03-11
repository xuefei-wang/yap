"""Audio recording via ffmpeg (Linux / macOS)."""

import os
import platform
import signal
import subprocess
import tempfile

TMPDIR = os.path.join(tempfile.gettempdir(), "yap")
AUDIO_PATH = os.path.join(TMPDIR, "recording.wav")


def get_ffmpeg_input_args():
    system = platform.system()
    if system == "Darwin":
        return ["-f", "avfoundation", "-i", ":default"]
    elif system == "Windows":
        return ["-f", "dshow", "-i", "audio=default"]
    else:  # Linux / other Unix
        return ["-f", "pulse", "-i", "default"]


def start_recording():
    os.makedirs(TMPDIR, exist_ok=True)
    input_args = get_ffmpeg_input_args()
    cmd = (
        ["ffmpeg", "-y"]
        + input_args
        + ["-ac", "1", "-ar", "16000", AUDIO_PATH, "-loglevel", "error"]
    )
    stdin = subprocess.PIPE if platform.system() == "Windows" else subprocess.DEVNULL
    proc = subprocess.Popen(cmd, stdin=stdin)
    return proc


def stop_recording(proc):
    if platform.system() == "Windows" and proc.stdin:
        proc.stdin.write(b"q\n")
        proc.stdin.flush()
    else:
        proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    return AUDIO_PATH


def cleanup_audio():
    try:
        os.remove(AUDIO_PATH)
    except FileNotFoundError:
        pass
