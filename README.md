# yap

*Talk is cheap.*

Voice dictation for the terminal. Records audio, transcribes locally with [Whisper](https://github.com/SYSTRAN/faster-whisper), and types the result into the active window.

## Install

```bash
git clone https://github.com/xuefei-wang/yap.git
cd yap
./install.sh
```

Then add yap to your PATH:

```bash
echo 'export PATH="$HOME/yap:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

```bash
yap        # Record -> transcribe -> type into active window
yap -c     # Record -> transcribe -> copy to clipboard
```

1. Run `yap`
2. Speak
3. Press Enter to stop recording
4. Text is typed into the active window (or copied with `-c`)

### Whisper models

Set `WHISPER_MODEL` to control speed vs accuracy:

| Model | Speed | Accuracy |
|-------|-------|----------|
| `tiny.en` | ~1s | Good |
| `base.en` | ~2s | Better (default) |
| `small.en` | ~4s | Great |
| `medium.en` | ~8s | Best |

```bash
export WHISPER_MODEL=small.en
yap
```

## Dependencies

- **ffmpeg** - audio recording
- **faster-whisper** - speech-to-text (or openai-whisper)
- **xdotool** - typing into active window (X11)
- **wtype** - typing into active window (Wayland, optional)
- **xclip** - clipboard support

All installed automatically by `./install.sh` (Ubuntu/Debian).

## License

MIT
