"""Measure which OpenRouter free models are actually usable right now.

    python probe_models.py            # test the configured fallback chain
    python probe_models.py --all      # discover and test every free model

Free models on OpenRouter are shared capacity. They throttle upstream without
warning, and availability changes week to week -- one model measured 0/3 while
four others measured 3/3 in the same minute. Re-run this before the session and
reorder OPENROUTER_FALLBACKS in prototypes/agents/provider.py if needed.

Two things are measured, and the second matters as much as the first:
  RELIABILITY -- does it answer, repeatedly?
  CLEANLINESS -- "reasoning" models leak their thinking into the answer, which
                 looks terrible projected and breaks the structured agents.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prototypes"))
from agents.provider import OPENROUTER_FALLBACKS  # noqa: E402

API = "https://openrouter.ai/api/v1"

PROMPT = (
    "GUIDELINE EXTRACT:\n[T3] Drug-sensitive TB: two months of isoniazid, rifampicin, "
    "pyrazinamide and ethambutol, then four months of isoniazid, rifampicin and "
    "ethambutol.\n\nQUESTION: What is the regimen?\n\n"
    "Answer from the extract only, citing the section marker. Two sentences maximum."
)

# Tell-tales that a model is emitting its own reasoning rather than an answer.
LEAK_RE = re.compile(r"(?i)the user (wants|is asking)|<think|okay,? (so|let)|let me think")


def _key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENROUTER_API_KEY first.")
    return key


def _get(path: str, key: str) -> dict:
    req = urllib.request.Request(API + path, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read())


def _ask(model: str, key: str) -> tuple[bool, str]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a clinical guideline assistant. Be terse."},
            {"role": "user", "content": PROMPT},
        ],
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        API + "/chat/completions", data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        return True, (data["choices"][0]["message"]["content"] or "").strip()
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return False, type(exc).__name__


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true",
                        help="discover every free model instead of testing the chain")
    parser.add_argument("--tries", type=int, default=3)
    args = parser.parse_args()

    key = _key()

    if args.all:
        models = [
            m["id"] for m in _get("/models", key)["data"]
            if float(m.get("pricing", {}).get("prompt") or 1) == 0
            and float(m.get("pricing", {}).get("completion") or 1) == 0
        ]
        print(f"Discovered {len(models)} free models\n")
    else:
        models = OPENROUTER_FALLBACKS
        print("Testing the configured fallback chain\n")

    results = []
    for model in models:
        ok, sample = 0, ""
        for _ in range(args.tries):
            good, text = _ask(model, key)
            if good and text:
                ok += 1
                sample = sample or text
            time.sleep(1.2)

        leaky = bool(LEAK_RE.search(sample))
        results.append((ok, not leaky, model))
        flag = "LEAKY" if leaky else "clean"
        print(f"  {ok}/{args.tries}  {flag:<5}  {model}")
        if sample:
            print(f"          {sample[:110].replace(chr(10), ' ')}")

    usable = [m for ok, clean, m in results if ok == args.tries and clean]
    print(f"\n{len(usable)} model(s) fully reliable and clean.")
    if usable:
        print("\nSuggested OPENROUTER_FALLBACKS order:")
        for m in usable:
            print(f'    "{m}",')
    else:
        print("\nNothing is reliable right now. Run the session in MOCK_MODE=1 —")
        print("it is designed for exactly this, and nobody can tell.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
