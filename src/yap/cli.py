"""yap CLI entry point."""

import argparse
import os
import sys

from yap.record import (
    start_recording,
    stop_recording,
    cleanup_audio,
    AUDIO_PATH,
)
from yap.transcribe import transcribe
from yap.correct import llm_correct
from yap.config import load_config, run_config_wizard
from yap.output import type_text, copy_to_clipboard


def build_parser():
    parser = argparse.ArgumentParser(
        prog="yap",
        description="Talk is cheap. Voice dictation for the terminal.",
    )
    parser.add_argument(
        "-c",
        "--clipboard",
        action="store_true",
        help="Copy to clipboard instead of typing",
    )
    parser.add_argument(
        "-l", "--llm", action="store_true", help="Correct transcription with an LLM"
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Whisper model (default: small.en, env: WHISPER_MODEL)",
    )
    parser.add_argument(
        "--lang",
        default=None,
        help="Language code e.g. en, zh, ja (default: en, env: YAP_LANG)",
    )

    parser.add_argument(
        "-s",
        "--serve",
        action="store_true",
        help="Start the web UI server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for web UI server (default: 8765)",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("config", help="Configure LLM provider")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # --- Config subcommand ---
    if args.command == "config":
        run_config_wizard()
        return 0

    # --- Serve mode ---
    if args.serve:
        extra_flags = []
        if args.clipboard:
            extra_flags.append("--clipboard")
        if args.llm:
            extra_flags.append("--llm")
        if extra_flags:
            print(
                f"Warning: {', '.join(extra_flags)} ignored in serve mode. "
                f"Use the web UI settings instead."
            )
        from yap.server import run_server

        run_server(host="localhost", port=args.port)
        return 0

    model = args.model or os.environ.get("WHISPER_MODEL", "small.en")
    lang = args.lang or os.environ.get("YAP_LANG")

    # --- Interactive mode ---
    print("🎙️ Recording... Press Enter to stop.")
    proc = start_recording()
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass
    stop_recording(proc)
    print("✍️ Transcribing...")

    # --- Transcribe ---
    text = transcribe(AUDIO_PATH, model_size=model, language=lang)

    cleanup_audio()

    if not text:
        print("No speech detected.")
        return 1

    # --- LLM correction ---
    if args.llm:
        cfg = load_config()
        provider = cfg.get("llm_provider")
        if not provider:
            print("No LLM provider configured. Run 'yap config' to set one up.")
        else:
            print("🔧 Correcting...")
            text = llm_correct(text, provider, model=cfg.get("llm_model"))

    # --- Output ---
    print(text)

    if args.clipboard:
        copy_to_clipboard(text)
        print("(copied to clipboard)")
    else:
        if not type_text(text):
            copy_to_clipboard(text)
            print("(no typing tool found — copied to clipboard)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
