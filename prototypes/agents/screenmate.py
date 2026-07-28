"""ScreenMate -- prototype 4.

Capability demonstrated: TOOL USE AT SCALE.
The same decision applied to many records, returning machine-readable output
that feeds the next step of a workflow instead of a human re-reading it.

This is the prototype that reframes AI agents from "chat" to "throughput", which
is the point worth making to a research audience.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from . import provider

VERDICTS = ("INCLUDE", "EXCLUDE", "UNCLEAR")

SYSTEM = """You screen research abstracts for a systematic review.

For each abstract, decide INCLUDE, EXCLUDE, or UNCLEAR against the criteria given.

Return ONLY a JSON array. One object per abstract, in the same order:
[{"id": "<id>", "verdict": "INCLUDE|EXCLUDE|UNCLEAR", "reason": "<max 15 words>"}]

Use UNCLEAR when the abstract does not contain enough information to decide.
Never guess a verdict you cannot justify from the abstract text. No prose outside the JSON.
"""

MOCK = """[
{"id": "A1", "verdict": "INCLUDE", "reason": "Cluster RCT, adults 30+, BP outcome, Indian primary care setting"},
{"id": "A2", "verdict": "EXCLUDE", "reason": "Paediatric population, outside the age criterion"},
{"id": "A3", "verdict": "UNCLEAR", "reason": "Study design not stated in abstract"},
{"id": "A4", "verdict": "EXCLUDE", "reason": "Narrative review, not a primary study"},
{"id": "A5", "verdict": "INCLUDE", "reason": "Randomised, adult, reports systolic BP at 6 months"}
]"""


@dataclass
class Abstract:
    id: str
    text: str


@dataclass
class ScreenVerdict:
    id: str
    verdict: str
    reason: str


@dataclass
class ScreenResult:
    verdicts: list[ScreenVerdict] = field(default_factory=list)
    parse_error: str = ""

    @property
    def counts(self) -> dict[str, int]:
        return {v: sum(1 for x in self.verdicts if x.verdict == v) for v in VERDICTS}


def parse_abstracts(blob: str) -> list[Abstract]:
    """Split a pasted block into abstracts. One per paragraph, or 'ID: text' lines."""
    chunks = [c.strip() for c in re.split(r"\n\s*\n", blob) if c.strip()]
    abstracts = []
    for i, chunk in enumerate(chunks, start=1):
        match = re.match(r"^([A-Za-z0-9_-]{1,12})\s*[::.]\s*(.+)$", chunk, re.S)
        if match:
            abstracts.append(Abstract(id=match.group(1), text=match.group(2).strip()))
        else:
            abstracts.append(Abstract(id=f"A{i}", text=chunk))
    return abstracts


def _extract_json(text: str) -> list[dict]:
    """Models wrap JSON in prose and code fences. Dig it out rather than trusting them."""
    fenced = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    candidate = fenced.group(1) if fenced else text
    start, end = candidate.find("["), candidate.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("no JSON array found in model output")
    return json.loads(candidate[start:end + 1])


def screen(abstracts: list[Abstract], criteria: str) -> ScreenResult:
    """Apply inclusion/exclusion criteria across a batch of abstracts."""
    if not abstracts:
        return ScreenResult()

    listing = "\n\n".join(f"ID {a.id}:\n{a.text}" for a in abstracts)
    prompt = f"CRITERIA:\n{criteria}\n\nABSTRACTS:\n\n{listing}\n\nReturn the JSON array now."

    raw = provider.complete(prompt, system=SYSTEM, mock=MOCK, temperature=0.0)

    try:
        rows = _extract_json(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        return ScreenResult(parse_error=f"Could not parse model output as JSON: {exc}")

    known = {a.id for a in abstracts}
    verdicts = []
    for row in rows:
        verdict = str(row.get("verdict", "")).upper()
        verdicts.append(
            ScreenVerdict(
                id=str(row.get("id", "?")),
                # An unrecognised verdict becomes UNCLEAR, never a silent INCLUDE.
                verdict=verdict if verdict in VERDICTS else "UNCLEAR",
                reason=str(row.get("reason", ""))[:200],
            )
        )

    # Anything the model skipped is surfaced, not quietly dropped.
    seen = {v.id for v in verdicts}
    verdicts += [
        ScreenVerdict(id=aid, verdict="UNCLEAR", reason="Model returned no verdict for this abstract")
        for aid in known - seen
    ]

    return ScreenResult(verdicts=verdicts)
