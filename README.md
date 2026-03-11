<p align="center">
  <img src="https://raw.githubusercontent.com/xuefei-wang/yap/main/banner.png" alt="yap — talk is cheap.">
</p>

<p align="center">
  <strong>Speak → Whisper transcribes → text appears.</strong>
  <br>
  Linux · macOS · Windows
</p>

## Install

```bash
uv pip install yap-dictation
```

Or from source:

```bash
git clone https://github.com/xuefei-wang/yap.git
cd yap
uv pip install .
```

`pip install` also works if you don't use uv.

Windows users: `uv pip install yap-dictation[windows]`

You also need **ffmpeg** installed (`apt install ffmpeg` / `brew install ffmpeg` / `winget install ffmpeg`).

## Usage

```bash
yap           # Record -> transcribe -> type into active window
yap -c        # Copy to clipboard instead
yap --llm     # Also correct with an LLM
```

Speak, press **Enter** to stop. Text is typed into the active window.

If no typing tool is found, yap copies to clipboard as a fallback.

### Options

| Flag / Env Var | Description |
|------|-------------|
| `-c`, `--clipboard` | Copy to clipboard instead of typing |
| `-l`, `--llm` | Correct transcription with an LLM |
| `--model MODEL` | Whisper model (default: `small.en`, env: `WHISPER_MODEL`) |
| `--lang LANG` | Language code e.g. `en`, `zh`, `ja` (env: `YAP_LANG`) |
| `-s`, `--serve` | Start the web UI server |
| `--port PORT` | Port for web UI server (default: 8765) |

## Web UI

For a graphical interface, start the web server:

```bash
uv pip install yap-dictation[web]   # one-time setup
yap --serve
```

Opens a browser page with a record button, transcription display, and settings.

**Keyboard shortcuts:** Space to toggle recording, Ctrl+Shift+C to copy transcription.

Two transcription modes available in the web UI:
- **Browser Speech** — free, uses your browser's built-in speech recognition (Chrome, Edge, Safari)
- **Local Whisper** — private, uses the same local Whisper model as the CLI

Note: Browser Speech sends audio to your browser vendor's servers for processing.

## LLM correction (optional)

Use `--llm` to send transcription through an LLM for grammar, punctuation, and misheard word fixes.

### Setup

Run `yap config` to choose your provider:

```bash
yap config
```

Available providers:

| Provider | Requires |
|----------|----------|
| `claude-code` | [Claude Code](https://claude.com/claude-code) CLI installed |
| `claude` | `ANTHROPIC_API_KEY` env var |
| `openai` | `OPENAI_API_KEY` env var |
| `gemini` | `GEMINI_API_KEY` env var |

`yap config` also lets you choose which model to use per provider. Defaults: Claude Haiku 4.5, GPT-4o Mini, Gemini 2.0 Flash.

Configuration is saved to `~/.config/yap/config.json`.

## Whisper models

| Model | Speed | Accuracy |
|-------|-------|----------|
| `tiny.en` | ~1s | Good |
| `base.en` | ~2s | Better |
| `small.en` | ~4s | Great **(default)** |
| `medium.en` | ~8s | Best |

For non-English languages, use models without `.en` suffix (e.g. `small`, `medium`):

```bash
yap --model small --lang zh
```

## Requirements

- **Python 3.10+**
- **ffmpeg** — audio recording (`apt install ffmpeg` / `brew install ffmpeg` / `winget install ffmpeg`)
- **faster-whisper** — installed automatically
- **Linux:** PulseAudio or PipeWire (with pipewire-pulse) for audio capture
- **Linux:** xdotool or wtype (typing), xclip or wl-copy (clipboard)
- **macOS:** works out of the box (uses osascript + pbcopy)
- **Windows:** ffmpeg (`winget install ffmpeg` or `choco install ffmpeg`), install extras with `uv pip install yap-dictation[windows]`

## License

GPL-3.0
