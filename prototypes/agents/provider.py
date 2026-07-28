"""LLM provider layer.

One job: turn a prompt into text, and never let the demo die.

Three providers, chosen automatically from whichever key is present:

    OPENROUTER_API_KEY  ->  OpenRouter  (many models, generous free tier)
    GOOGLE_API_KEY      ->  Gemini      (Google AI Studio)
    neither             ->  MOCK        (offline, pre-written responses)

MOCK_MODE=1 forces the last one regardless. That is the on-stage fallback: if
auditorium wifi fails, set the flag and every prototype keeps working with no
network and no key. The audience cannot tell the difference.

Only OpenRouter and Gemini know anything provider-specific, and both live at the
bottom of this file. Nothing else in the codebase knows which model is answering.
"""

from __future__ import annotations

import json
import os
import textwrap
import urllib.error
import urllib.request

# OpenRouter free models are shared and throttle upstream without warning -- one
# was measured at 0/3 success while others were 3/3 in the same minute. A single
# model is therefore not safe to stand in front of an audience with, so we try a
# chain and take the first that answers.
#
# Chosen by measurement (tools/probe_models.py), on two criteria:
#   1. reliability under repeated calls
#   2. CLEAN output -- "reasoning" models leak their thinking into the answer,
#      which looks terrible projected and breaks the structured-output agents.
OPENROUTER_FALLBACKS = [
    "inclusionai/ling-3.0-flash:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
]

# Setting OPENROUTER_MODEL pins one model and disables the chain.
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "").strip()

GEMINI_MODEL = os.environ.get("AGENT_MODEL", "gemini-2.0-flash")

TIMEOUT = 60

# Which model actually answered last, for the sidebar. A demo where you cannot
# tell what just served you is a demo you cannot debug.
last_model_used: str = ""


class ProviderError(RuntimeError):
    """Raised when a live call fails and no mock is available to fall back to."""


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


def active_provider() -> str:
    """Which backend will actually answer: 'openrouter', 'gemini', or 'mock'."""
    if _env("MOCK_MODE") in {"1", "true", "True"}:
        return "mock"
    if _env("OPENROUTER_API_KEY"):
        return "openrouter"
    if _env("GOOGLE_API_KEY"):
        return "gemini"
    return "mock"


def is_mock_mode() -> bool:
    return active_provider() == "mock"


def mode_label() -> str:
    """Human-readable mode, shown in the app sidebar so you always know which you're in."""
    provider = active_provider()
    if provider == "openrouter":
        model = last_model_used or OPENROUTER_MODEL or OPENROUTER_FALLBACKS[0]
        return f"LIVE · OpenRouter · {model.split('/')[-1]}"
    if provider == "gemini":
        return f"LIVE · Gemini · {GEMINI_MODEL}"
    return "OFFLINE DEMO (mock)"


def complete(prompt: str, *, system: str = "", mock: str = "", temperature: float = 0.2) -> str:
    """Return model output for `prompt`.

    `mock` is the response used when offline. Every caller must supply one --
    an agent without a mock is an agent that can break on stage.
    """
    provider = active_provider()

    if provider == "mock":
        if not mock:
            raise ProviderError(
                "MOCK_MODE is on but this call has no mock response. "
                "Every agent must ship a mock so the demo survives without wifi."
            )
        return textwrap.dedent(mock).strip()

    try:
        if provider == "openrouter":
            return _openrouter(prompt, system=system, temperature=temperature)
        return _gemini(prompt, system=system, temperature=temperature)
    except Exception as exc:  # noqa: BLE001 - on stage, degrading beats crashing
        if mock:
            return (
                textwrap.dedent(mock).strip()
                + f"\n\n---\n_(Live call failed, showed offline response instead: "
                  f"{type(exc).__name__})_"
            )
        raise ProviderError(f"Live call failed and no mock available: {exc}") from exc


def _post(url: str, payload: dict, headers: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"Content-Type": "application/json", **headers},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:
        # Surface the provider's own message -- "quota exceeded" and "key leaked"
        # need very different responses from you, and a bare 4xx says neither.
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise ProviderError(f"HTTP {exc.code}: {detail}") from exc


def _openrouter(prompt: str, *, system: str, temperature: float) -> str:
    """OpenAI-compatible chat completions. Stdlib only -- no extra dependency.

    Walks the model chain and returns the first real answer. A rate-limited
    free model is the normal case here, not an exception, so moving on to the
    next one is the expected behaviour rather than error handling.
    """
    global last_model_used

    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
    headers = {
        "Authorization": f"Bearer {_env('OPENROUTER_API_KEY')}",
        # Attribution headers OpenRouter uses for its dashboards.
        "HTTP-Referer": "https://clinical-ai-agents.streamlit.app",
        "X-Title": "Clinical AI Agents (CME demo)",
    }

    models = [OPENROUTER_MODEL] if OPENROUTER_MODEL else OPENROUTER_FALLBACKS
    failures = []

    for model in models:
        try:
            data = _post(
                "https://openrouter.ai/api/v1/chat/completions",
                {"model": model, "messages": messages, "temperature": temperature},
                headers,
            )
            answer = (data["choices"][0]["message"]["content"] or "").strip()
            if answer:
                last_model_used = model
                return answer
            failures.append(f"{model}: empty response")
        except ProviderError as exc:
            failures.append(f"{model}: {exc}"[:160])

    raise ProviderError("All OpenRouter models failed — " + " | ".join(failures))


def _gemini(prompt: str, *, system: str, temperature: float) -> str:
    """Google AI Studio. Also stdlib, so google-genai is not required to run."""
    payload: dict = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}

    data = _post(
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={_env('GOOGLE_API_KEY')}",
        payload,
        {},
    )
    return (data["candidates"][0]["content"]["parts"][0]["text"] or "").strip()
