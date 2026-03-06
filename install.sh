#!/bin/bash
# Install yap dependencies
set -e

echo "Installing yap dependencies..."

# System packages
PKGS=""
command -v ffmpeg &>/dev/null || PKGS+=" ffmpeg"
command -v xdotool &>/dev/null || PKGS+=" xdotool"
command -v xclip &>/dev/null || PKGS+=" xclip"

if [ -n "$PKGS" ]; then
    echo "Installing system packages:$PKGS"
    sudo apt-get update -qq && sudo apt-get install -y -qq $PKGS
else
    echo "System packages already installed (ffmpeg, xdotool, xclip)"
fi

# Python package (faster-whisper)
if ! python3 -c "import faster_whisper" 2>/dev/null; then
    echo "Installing faster-whisper..."
    if command -v uv &>/dev/null; then
        uv pip install --system faster-whisper
    elif command -v pip3 &>/dev/null; then
        pip3 install --user faster-whisper
    else
        echo "Error: No pip or uv found. Install Python first."
        exit 1
    fi
else
    echo "faster-whisper already installed"
fi

echo ""
echo "Done! Run 'yap' to start dictating."
