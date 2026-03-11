"""LLM-based transcription correction."""

import json
import os
import subprocess
import sys
from urllib.request import Request, urlopen

PROMPT = (
    "Clean up this speech-to-text transcription. "
    "Add proper punctuation (commas, periods, question marks). "
    "Fix capitalization (sentence starts, proper nouns). "
    "Fix obvious grammar mistakes (subject-verb agreement, tense). "
    "Fix misheard homophones based on context (their/there/they're, its/it's). "
    "Remove filler words (um, uh, like, you know). "
    "Keep the speaker's original wording and tone — do not rephrase, "
    "formalize, or rewrite. Return only the corrected text, nothing else."
)


def llm_correct(text, provider, model=None):
    if not provider:
        return text

    try:
        if provider == "claude-code":
            return _correct_claude_code(text, model=model or "haiku")
        elif provider == "claude":
            return _correct_claude_api(text, model=model or "claude-haiku-4-5-20251001")
        elif provider == "openai":
            return _correct_openai(text, model=model or "gpt-4o-mini")
        elif provider == "gemini":
            return _correct_gemini(text, model=model or "gemini-2.0-flash")
    except Exception as e:
        print(f"LLM correction failed ({provider}): {e}", file=sys.stderr)
        return text
    return text


def _correct_claude_code(text, model="haiku"):
    result = subprocess.run(
        [
            "claude",
            "-p",
            "--model",
            model,
            "--no-session-persistence",
            "--tools",
            "",
            "--system-prompt",
            PROMPT,
        ],
        input=text,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout.strip() or text


def _api_request(url, headers, payload):
    data = json.dumps(payload).encode()
    req = Request(url, data=data, headers=headers, method="POST")
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _correct_claude_api(text, model="claude-haiku-4-5-20251001"):
    r = _api_request(
        "https://api.anthropic.com/v1/messages",
        {
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        {
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": f"{PROMPT}\n\n{text}"}],
        },
    )
    return r["content"][0]["text"]


def _correct_openai(text, model="gpt-4o-mini"):
    r = _api_request(
        "https://api.openai.com/v1/chat/completions",
        {
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        },
        {
            "model": model,
            "messages": [{"role": "user", "content": f"{PROMPT}\n\n{text}"}],
        },
    )
    return r["choices"][0]["message"]["content"]


def _correct_gemini(text, model="gemini-2.0-flash"):
    key = os.environ["GEMINI_API_KEY"]
    r = _api_request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
        {"Content-Type": "application/json"},
        {"contents": [{"parts": [{"text": f"{PROMPT}\n\n{text}"}]}]},
    )
    return r["candidates"][0]["content"]["parts"][0]["text"]
