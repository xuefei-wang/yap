"""Speech-to-text via faster-whisper."""

import sys

from faster_whisper import WhisperModel

_model_cache = {}


def transcribe(audio_path, model_size="small.en", language=None, verbose=True):
    if model_size not in _model_cache:
        if verbose:
            print(f"⏳ Loading Whisper model '{model_size}'...", file=sys.stderr)
        _model_cache[model_size] = WhisperModel(
            model_size, device="auto", compute_type="auto"
        )
        if verbose:
            print(f"✅ Model '{model_size}' ready.", file=sys.stderr)
    model = _model_cache[model_size]

    kwargs = {"beam_size": 5}
    if language:
        kwargs["language"] = language

    segments, _ = model.transcribe(audio_path, **kwargs)
    return "".join(segment.text for segment in segments).strip()
