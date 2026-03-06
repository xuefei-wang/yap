#!/bin/bash
# yap - Voice dictation using Whisper
# Records audio, transcribes with faster-whisper, and types or copies the result
#
# Usage:
#   yap        # Record until Enter, transcribe, type into active window
#   yap -c     # Same but copy to clipboard instead of typing
#
# Environment:
#   WHISPER_MODEL  Whisper model size (default: base.en)
#                  Options: tiny.en, base.en, small.en, medium.en

set -e

TMPDIR_YAP="${TMPDIR:-/tmp}/yap"
TEMP_AUDIO="$TMPDIR_YAP/recording.wav"
WHISPER_MODEL="${WHISPER_MODEL:-base.en}"
COPY_MODE=false

mkdir -p "$TMPDIR_YAP"

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        -c|--clipboard) COPY_MODE=true; shift ;;
        -h|--help)
            echo "Usage: yap [-c|--clipboard] [-h|--help]"
            echo ""
            echo "Record audio, transcribe with Whisper, and type the result."
            echo ""
            echo "Options:"
            echo "  -c, --clipboard  Copy to clipboard instead of typing"
            echo "  -h, --help       Show this help"
            echo ""
            echo "Environment:"
            echo "  WHISPER_MODEL    Model size (default: base.en)"
            echo "                   Options: tiny.en, base.en, small.en, medium.en"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Check dependencies
for cmd in ffmpeg python3; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: $cmd not found. Run: ./install.sh"
        exit 1
    fi
done

# Record audio (press Enter to stop)
echo "Recording... Press Enter to stop."
ffmpeg -y -f pulse -i default -ac 1 -ar 16000 "$TEMP_AUDIO" -loglevel error &
FFMPEG_PID=$!

read -r
kill "$FFMPEG_PID" 2>/dev/null || true
wait "$FFMPEG_PID" 2>/dev/null || true

echo "Transcribing..."

# Transcribe with faster-whisper (preferred) or openai-whisper
if python3 -c "import faster_whisper" 2>/dev/null; then
    TEXT=$(python3 << PYEOF
from faster_whisper import WhisperModel
model = WhisperModel("$WHISPER_MODEL", device="auto", compute_type="auto")
segments, _ = model.transcribe("$TEMP_AUDIO", beam_size=5)
print("".join(segment.text for segment in segments).strip())
PYEOF
)
elif python3 -c "import whisper" 2>/dev/null; then
    TEXT=$(python3 << PYEOF
import whisper
model = whisper.load_model("$WHISPER_MODEL")
result = model.transcribe("$TEMP_AUDIO")
print(result["text"].strip())
PYEOF
)
else
    echo "Error: No whisper library found. Run: ./install.sh"
    exit 1
fi

rm -f "$TEMP_AUDIO"

if [ -z "$TEXT" ]; then
    echo "No speech detected."
    exit 0
fi

echo "$TEXT"

if $COPY_MODE; then
    echo -n "$TEXT" | xclip -selection clipboard
    echo "(copied to clipboard)"
else
    # Type into active window
    if command -v xdotool &>/dev/null; then
        sleep 0.2
        xdotool type --delay 10 "$TEXT"
    elif command -v wtype &>/dev/null; then
        wtype "$TEXT"
    else
        echo -n "$TEXT" | xclip -selection clipboard
        echo "(xdotool/wtype not found - copied to clipboard instead)"
    fi
fi
