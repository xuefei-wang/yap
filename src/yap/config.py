"""Configuration management for yap."""

import json
import os
import platform
import shutil


def _get_config_dir():
    if platform.system() == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return os.path.join(base, "yap")


CONFIG_DIR = _get_config_dir()
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

PROVIDERS = [
    ("claude-code", "Claude Code CLI", "claude", None),
    ("claude", "Anthropic API", None, "ANTHROPIC_API_KEY"),
    ("openai", "OpenAI API", None, "OPENAI_API_KEY"),
    ("gemini", "Google Gemini API", None, "GEMINI_API_KEY"),
]

# Models per provider: list of (model_id, description), first is default
PROVIDER_MODELS = {
    "claude-code": [
        ("haiku", "Claude Haiku — fast, cheapest"),
        ("sonnet", "Claude Sonnet — balanced"),
        ("opus", "Claude Opus — most capable"),
    ],
    "claude": [
        ("claude-haiku-4-5-20251001", "Claude Haiku 4.5 — fast, cheapest"),
        ("claude-sonnet-4-5-20250514", "Claude Sonnet 4.5 — balanced"),
        ("claude-opus-4-0-20250514", "Claude Opus 4 — most capable"),
    ],
    "openai": [
        ("gpt-4o-mini", "GPT-4o Mini — fast, cheapest"),
        ("gpt-4o", "GPT-4o — balanced"),
        ("o3-mini", "o3-mini — reasoning"),
    ],
    "gemini": [
        ("gemini-2.0-flash", "Gemini 2.0 Flash — fast, cheapest"),
        ("gemini-2.5-pro-preview-05-06", "Gemini 2.5 Pro — most capable"),
    ],
}


def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")


def run_config_wizard():
    print("\n🔧 yap configuration\n")
    print("Choose an LLM provider for transcription correction:\n")
    for i, (key, label, cli_bin, env_var) in enumerate(PROVIDERS, 1):
        extra = ""
        if cli_bin:
            extra = " (no API key needed)"
        elif env_var:
            extra = f" (requires {env_var})"
        print(f"  {i}) {key:<14} — {label}{extra}")

    print()
    choice = _prompt_choice(len(PROVIDERS))
    key, label, cli_bin, env_var = PROVIDERS[choice - 1]

    # Validate prerequisites
    if cli_bin:
        if shutil.which(cli_bin):
            print(f"\nChecking for '{cli_bin}' CLI... ✅ found")
        else:
            print(
                f"\n⚠️  '{cli_bin}' CLI not found on PATH. Install it before using --llm."
            )
    elif env_var:
        if os.environ.get(env_var):
            print(f"\nChecking for {env_var}... ✅ found")
        else:
            print(f"\n⚠️  {env_var} not set. Export it before using --llm.")

    # Model selection
    models = PROVIDER_MODELS[key]
    default_model = models[0][0]
    print(f"\nDefault model: {default_model}")

    if len(models) > 1:
        print("\nAvailable models:\n")
        for i, (model_id, desc) in enumerate(models, 1):
            marker = " (default)" if i == 1 else ""
            print(f"  {i}) {model_id:<35} — {desc}{marker}")
        print()
        model_choice = _prompt_model_choice(len(models))
        chosen_model = models[model_choice - 1][0]
    else:
        chosen_model = default_model

    cfg = load_config()
    cfg["llm_provider"] = key
    cfg["llm_model"] = chosen_model
    save_config(cfg)
    print(f"\nSaved to {CONFIG_PATH}")


def _prompt_choice(max_val):
    while True:
        try:
            val = int(input(f"Enter choice [1-{max_val}]: "))
            if 1 <= val <= max_val:
                return val
        except (ValueError, EOFError):
            pass
        print(f"Please enter a number between 1 and {max_val}.")


def _prompt_model_choice(max_val):
    while True:
        raw = input(f"Enter choice [1-{max_val}] (Enter for default): ").strip()
        if raw == "":
            return 1
        try:
            val = int(raw)
            if 1 <= val <= max_val:
                return val
        except (ValueError, EOFError):
            pass
        print(f"Please enter a number between 1 and {max_val}, or Enter for default.")
