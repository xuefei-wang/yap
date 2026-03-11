"""Web UI server for yap — serves HTML + handles WebSocket messages."""

import asyncio
import json
import os
import subprocess
import tempfile
import uuid

from yap.transcribe import transcribe
from yap.correct import llm_correct
from yap.output import copy_to_clipboard

TMPDIR = os.path.join(tempfile.gettempdir(), "yap")


async def handle_message(raw):
    """Handle a JSON WebSocket message, return a JSON response string."""
    msg = json.loads(raw)
    msg_type = msg.get("type")

    if msg_type == "correct":
        text = await asyncio.to_thread(llm_correct, msg["text"], msg["provider"])
        return json.dumps({"type": "corrected", "text": text})

    elif msg_type == "clipboard":
        await asyncio.to_thread(copy_to_clipboard, msg["text"])
        return json.dumps({"type": "copied"})

    else:
        return json.dumps({"type": "error", "message": f"Unknown type: {msg_type}"})


async def handle_audio_message(audio_bytes, settings):
    """Handle binary audio data: convert to WAV, transcribe, return JSON."""
    os.makedirs(TMPDIR, exist_ok=True)
    uid = uuid.uuid4().hex[:8]
    webm_path = os.path.join(TMPDIR, f"upload-{uid}.webm")
    wav_path = os.path.join(TMPDIR, f"upload-{uid}.wav")

    with open(webm_path, "wb") as f:
        f.write(audio_bytes)

    await asyncio.to_thread(
        subprocess.run,
        [
            "ffmpeg",
            "-y",
            "-i",
            webm_path,
            "-ar",
            "16000",
            "-ac",
            "1",
            wav_path,
            "-loglevel",
            "error",
        ],
        check=True,
    )

    text = await asyncio.to_thread(
        transcribe,
        wav_path,
        model_size=settings.get("model", "small.en"),
        language=settings.get("language"),
    )

    for path in (webm_path, wav_path):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    return json.dumps({"type": "transcription", "text": text})


def _get_static_dir():
    return os.path.join(os.path.dirname(__file__), "static")


async def _serve(host, port):
    """Start the WebSocket + HTTP server."""
    try:
        from websockets.asyncio.server import serve
        from websockets.http11 import Response
        from websockets.datastructures import Headers
    except ImportError:
        print("Web UI requires the 'websockets' package.")
        print("Install it with: pip install yap-dictation[web]")
        raise SystemExit(1)

    static_dir = _get_static_dir()
    index_path = os.path.join(static_dir, "index.html")

    with open(index_path, "rb") as f:
        index_html = f.read()

    async def handler(websocket):
        settings = {}
        async for message in websocket:
            if isinstance(message, bytes):
                response = await handle_audio_message(message, settings)
            else:
                parsed = json.loads(message)
                if parsed.get("type") == "settings":
                    settings = parsed.get("settings", {})
                    continue
                response = await handle_message(message)
            await websocket.send(response)

    async def process_request(connection, request):
        """Serve index.html for HTTP GET requests, 404 for other non-WS paths."""
        # Let WebSocket upgrade requests through
        if any(
            h.lower() == "upgrade"
            for h in request.headers.get_all("Connection")
        ):
            return None
        # Serve HTML for root
        if request.path == "/" or request.path == "/index.html":
            headers = Headers([("Content-Type", "text/html; charset=utf-8")])
            return Response(200, "OK", headers, index_html)
        # Serve static files
        MIME_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml"}
        safe_name = os.path.basename(request.path)
        ext = os.path.splitext(safe_name)[1].lower()
        if ext in MIME_TYPES:
            file_path = os.path.join(static_dir, safe_name)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as sf:
                    data = sf.read()
                headers = Headers([("Content-Type", MIME_TYPES[ext])])
                return Response(200, "OK", headers, data)
        # 404 for everything else (favicon.ico, etc.)
        headers = Headers([("Content-Type", "text/plain")])
        return Response(404, "Not Found", headers, b"Not Found")

    url = f"http://{host}:{port}"
    print(f"yap web UI running at {url}")

    import webbrowser

    asyncio.get_running_loop().call_later(1.0, webbrowser.open, url)

    async with serve(
        handler,
        host,
        port,
        process_request=process_request,
        max_size=10 * 1024 * 1024,
    ):
        await asyncio.Future()


def run_server(host="localhost", port=8765):
    """Entry point called from CLI."""
    try:
        asyncio.run(_serve(host, port))
    except KeyboardInterrupt:
        if os.path.isdir(TMPDIR):
            for f in os.listdir(TMPDIR):
                if f.startswith("upload-"):
                    try:
                        os.remove(os.path.join(TMPDIR, f))
                    except FileNotFoundError:
                        pass
        print("\nServer stopped.")
