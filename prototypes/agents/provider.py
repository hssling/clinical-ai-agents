"""LLM provider layer.

One job: turn a prompt into text, and never let the demo die.

Four backends, chosen automatically from whichever key is present, in this order:

    OPENAI_API_KEY      ->  OpenAI      (paid, most reliable -- wins if set)
    OPENROUTER_API_KEY  ->  OpenRouter  (many models, free tier, throttles)
    GOOGLE_API_KEY      ->  Gemini      (Google AI Studio)
    none of the above   ->  MOCK        (offline, pre-written responses)

The order is deliberate: dropping in a paid OpenAI key on the day takes over
automatically, with no code or config change, and removes the free-tier
throttling risk from the live demo.

MOCK_MODE=1 forces the last one regardless. That is the on-stage fallback: if
auditorium wifi fails, set the flag and every prototype keeps working with no
network and no key. The audience cannot tell the difference.

All provider-specific code lives at the bottom of this file. Nothing else in
the codebase knows or cares which model is answering.
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

# OpenAI. Paid, so throttling is not the concern here -- the chain exists
# because model availability varies between accounts and tiers, and a 404 on
# the first choice should not end the demo.
OPENAI_FALLBACKS = [
    "gpt-4.1-mini",   # cheap, fast, easily good enough for these prompts
    "gpt-4o-mini",
    "gpt-4.1",
]
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "").strip()

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
    """Which backend will answer: 'openai', 'openrouter', 'gemini', or 'mock'."""
    if _env("MOCK_MODE") in {"1", "true", "True"}:
        return "mock"
    # Paid first. Adding an OpenAI key on the day should silently take over.
    if _env("OPENAI_API_KEY"):
        return "openai"
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
    if provider == "openai":
        return f"LIVE · OpenAI · {last_model_used or OPENAI_MODEL or OPENAI_FALLBACKS[0]}"
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
        if provider == "openai":
            return _openai(prompt, system=system, temperature=temperature)
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


def _chat_completions(label: str, url: str, models: list[str], headers: dict,
                      prompt: str, system: str, temperature: float) -> str:
    """The OpenAI /chat/completions shape, which OpenRouter also speaks.

    Walks the model list and returns the first real answer. For OpenRouter a
    throttled model is the normal case rather than an exception, so moving on
    is expected behaviour, not error handling; for OpenAI the same mechanism
    covers models an account cannot access.

    Stdlib only -- no provider SDK is needed to run this app.
    """
    global last_model_used

    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
    failures = []

    for model in models:
        try:
            data = _post(url, {"model": model, "messages": messages,
                               "temperature": temperature}, headers)
            answer = (data["choices"][0]["message"]["content"] or "").strip()
            if answer:
                last_model_used = model
                return answer
            failures.append(f"{model}: empty response")
        except ProviderError as exc:
            failures.append(f"{model}: {exc}"[:160])

    raise ProviderError(f"All {label} models failed — " + " | ".join(failures))


def _openai(prompt: str, *, system: str, temperature: float) -> str:
    return _chat_completions(
        "OpenAI",
        "https://api.openai.com/v1/chat/completions",
        [OPENAI_MODEL] if OPENAI_MODEL else OPENAI_FALLBACKS,
        {"Authorization": f"Bearer {_env('OPENAI_API_KEY')}"},
        prompt, system, temperature,
    )


def _openrouter(prompt: str, *, system: str, temperature: float) -> str:
    return _chat_completions(
        "OpenRouter",
        "https://openrouter.ai/api/v1/chat/completions",
        [OPENROUTER_MODEL] if OPENROUTER_MODEL else OPENROUTER_FALLBACKS,
        {
            "Authorization": f"Bearer {_env('OPENROUTER_API_KEY')}",
            # Attribution headers OpenRouter uses for its dashboards.
            "HTTP-Referer": "https://clinical-ai-agents.streamlit.app",
            "X-Title": "Clinical AI Agents (CME demo)",
        },
        prompt, system, temperature,
    )


def self_test() -> int:
    """Report which backend is active and prove it can actually answer.

        python agents/provider.py

    Run this after setting a key, and again on the morning of the session. A key
    that authenticates is not the same as a key that works -- an account with no
    credit lists models happily and then returns 429 on every completion.
    """
    provider = active_provider()
    print(f"Active provider : {provider}")
    print(f"Label           : {mode_label()}")
    print("Keys present    : " + ", ".join(
        name for name in ("OPENAI_API_KEY", "OPENROUTER_API_KEY", "GOOGLE_API_KEY")
        if _env(name)) or "Keys present    : none")

    if provider == "mock":
        print("\nRunning OFFLINE. This is fine for the demo -- every agent works,")
        print("only the prose is pre-written. Set a key to go live.")
        return 0

    print("\nSending a real request...")
    try:
        answer = complete("Reply with the single word: ok", system="Be terse.")
        print(f"OK — {last_model_used or 'model'} answered: {answer[:60]!r}")
        return 0
    except ProviderError as exc:
        print(f"FAILED — {exc}")
        text = str(exc)
        if "429" in text and "quota" in text.lower():
            print("\n>> The key is valid but the account has no usable credit.")
            print("   OpenAI: add billing at platform.openai.com/settings/organization/billing")
            print("   Until then the app silently falls back to mock responses.")
        elif "401" in text:
            print("\n>> The key was rejected. Check it was copied whole.")
        elif "429" in text:
            print("\n>> Rate limited. For OpenRouter free models this is routine —")
            print("   run tools/probe_models.py to find one that is currently up.")
        return 1


def complete_multimodal(
    prompt: str,
    *,
    image_b64: str = "",
    mime_type: str = "image/png",
    system: str = "",
    mock: str = "",
    temperature: float = 0.2,
) -> str:
    """Return model output for `prompt` and optional base64 `image_b64`.

    `mock` is used in offline mode or as a fallback if the live call fails.
    """
    provider = active_provider()

    if provider == "mock" or not image_b64:
        if provider == "mock":
            if not mock:
                raise ProviderError(
                    "MOCK_MODE is on but this call has no mock response. "
                    "Every agent must ship a mock so the demo survives without wifi."
                )
            return textwrap.dedent(mock).strip()
        return complete(prompt, system=system, mock=mock, temperature=temperature)

    try:
        if provider == "openai":
            return _chat_completions_multimodal(
                "OpenAI",
                "https://api.openai.com/v1/chat/completions",
                [OPENAI_MODEL] if OPENAI_MODEL else OPENAI_FALLBACKS,
                {"Authorization": f"Bearer {_env('OPENAI_API_KEY')}"},
                prompt, image_b64, mime_type, system, temperature,
            )
        if provider == "openrouter":
            return _chat_completions_multimodal(
                "OpenRouter",
                "https://openrouter.ai/api/v1/chat/completions",
                [OPENROUTER_MODEL] if OPENROUTER_MODEL else OPENROUTER_FALLBACKS,
                {
                    "Authorization": f"Bearer {_env('OPENROUTER_API_KEY')}",
                    "HTTP-Referer": "https://clinical-ai-agents.streamlit.app",
                    "X-Title": "Clinical AI Agents (CME demo)",
                },
                prompt, image_b64, mime_type, system, temperature,
            )
        return _gemini_multimodal(prompt, image_b64=image_b64, mime_type=mime_type, system=system, temperature=temperature)
    except Exception as exc:  # noqa: BLE001 - on stage, degrading beats crashing
        if mock:
            return (
                textwrap.dedent(mock).strip()
                + f"\n\n---\n_(Live multimodal call failed, showed offline response instead: "
                  f"{type(exc).__name__})_"
            )
        raise ProviderError(f"Live multimodal call failed and no mock available: {exc}") from exc


def _chat_completions_multimodal(
    label: str, url: str, models: list[str], headers: dict,
    prompt: str, image_b64: str, mime_type: str, system: str, temperature: float
) -> str:
    global last_model_used

    user_content: list[dict] = [{"type": "text", "text": prompt}]
    if image_b64:
        user_content.append({"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}})

    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": user_content}]
    failures = []

    for model in models:
        try:
            data = _post(url, {"model": model, "messages": messages, "temperature": temperature}, headers)
            answer = (data["choices"][0]["message"]["content"] or "").strip()
            if answer:
                last_model_used = model
                return answer
            failures.append(f"{model}: empty response")
        except ProviderError as exc:
            failures.append(f"{model}: {exc}"[:160])

    raise ProviderError(f"All {label} multimodal models failed — " + " | ".join(failures))


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


def _gemini_multimodal(
    prompt: str, *, image_b64: str, mime_type: str, system: str, temperature: float
) -> str:
    parts: list[dict] = [{"text": prompt}]
    if image_b64:
        parts.insert(0, {
            "inlineData": {
                "mimeType": mime_type,
                "data": image_b64,
            }
        })
    payload: dict = {
        "contents": [{"parts": parts}],
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


if __name__ == "__main__":
    raise SystemExit(self_test())

