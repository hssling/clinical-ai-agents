"""LLM provider layer.

One job: turn a prompt into text, and never let the demo die.

MOCK_MODE=1 returns pre-written responses instantly with no network and no API
key. This is the on-stage fallback: if auditorium wifi fails, set the flag and
every prototype keeps working. The audience cannot tell the difference.

Swapping providers is a one-line change in _live_complete().
"""

from __future__ import annotations

import os
import textwrap

MODEL = os.environ.get("AGENT_MODEL", "gemini-2.0-flash")


class ProviderError(RuntimeError):
    """Raised when a live call fails and no mock is available to fall back to."""


def is_mock_mode() -> bool:
    """Mock mode is on if explicitly set, or if no API key exists to call with."""
    if os.environ.get("MOCK_MODE", "").strip() in {"1", "true", "True"}:
        return True
    return not os.environ.get("GOOGLE_API_KEY", "").strip()


def mode_label() -> str:
    """Human-readable mode, shown in the app sidebar so you always know which you're in."""
    return "OFFLINE DEMO (mock)" if is_mock_mode() else f"LIVE ({MODEL})"


def complete(prompt: str, *, system: str = "", mock: str = "", temperature: float = 0.2) -> str:
    """Return model output for `prompt`.

    `mock` is the response used when offline. Every caller must supply one --
    an agent without a mock is an agent that can break on stage.
    """
    if is_mock_mode():
        if not mock:
            raise ProviderError(
                "MOCK_MODE is on but this call has no mock response. "
                "Every agent must ship a mock so the demo survives without wifi."
            )
        return textwrap.dedent(mock).strip()

    try:
        return _live_complete(prompt, system=system, temperature=temperature)
    except Exception as exc:  # noqa: BLE001 - on stage, degrading beats crashing
        if mock:
            return (
                textwrap.dedent(mock).strip()
                + f"\n\n---\n_(Live call failed, showed offline response instead: {type(exc).__name__})_"
            )
        raise ProviderError(f"Live call failed and no mock available: {exc}") from exc


def _live_complete(prompt: str, *, system: str, temperature: float) -> str:
    """The only provider-specific code in the project.

    To use OpenAI or Anthropic instead, replace this function body. Nothing
    else in the codebase knows which model is answering.
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system or None,
            temperature=temperature,
        ),
    )
    return (response.text or "").strip()
