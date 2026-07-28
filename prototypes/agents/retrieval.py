"""Local keyword retrieval over guideline documents.

Deliberately has no external dependency and no network call. That is what makes
the on-stage refusal demo honest: even in MOCK_MODE, the agent's decision to
answer or refuse is computed for real from the actual documents. Only the prose
is canned offline -- never the judgement.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

GUIDELINE_DIR = Path(__file__).resolve().parent.parent / "data" / "guidelines"

SECTION_RE = re.compile(r"^##\s*\[([A-Z0-9]+)\]\s*(.+)$", re.MULTILINE)
WORD_RE = re.compile(r"[a-z0-9]+")

STOPWORDS = {
    "a", "an", "and", "any", "are", "as", "at", "be", "by", "can", "do", "does",
    "for", "from", "given", "has", "have", "how", "i", "if", "in", "is", "it",
    "may", "must", "of", "on", "or", "should", "than", "that", "the", "then",
    "there", "this", "to", "was", "we", "what", "when", "where", "which", "who",
    "why", "will", "with", "you", "your", "patient", "case", "please", "tell",
}


@dataclass
class Section:
    doc: str          # human-readable document name
    section_id: str   # e.g. "S3" -- what gets cited on screen
    title: str
    text: str

    @property
    def citation(self) -> str:
        return f"[{self.section_id}] {self.doc} — {self.title}"


def _singular(word: str) -> str:
    """Crude plural stripping so 'thresholds' matches 'threshold'.

    Not linguistics -- just enough that a doctor phrasing a question naturally
    still finds the right section.
    """
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _tokenise(text: str) -> list[str]:
    return [
        _singular(w)
        for w in WORD_RE.findall(text.lower())
        if w not in STOPWORDS and len(w) > 2
    ]


@lru_cache(maxsize=1)
def load_sections(directory: str | None = None) -> tuple[Section, ...]:
    """Parse every guideline file into ## [ID] Title sections."""
    base = Path(directory) if directory else GUIDELINE_DIR
    sections: list[Section] = []

    for path in sorted(base.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        doc_name = raw.splitlines()[0].lstrip("# ").split(" — ")[0].strip()
        matches = list(SECTION_RE.finditer(raw))
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
            body = raw[match.end():end].strip()
            if body:
                sections.append(
                    Section(doc=doc_name, section_id=match.group(1),
                            title=match.group(2).strip(), text=body)
                )
    return tuple(sections)


@lru_cache(maxsize=1)
def _idf() -> tuple[dict[str, float], float]:
    """Rare words are worth more. 'rifampicin' should outrank 'treatment'.

    Also returns the weight given to a query word that appears nowhere in the
    corpus. That weight is what makes out-of-scope questions score low: a word
    the guidelines have never seen is the rarest word of all, so it carries
    maximum weight -- and it can never be matched.
    """
    sections = load_sections()
    total = len(sections) or 1
    counts: dict[str, int] = {}
    for section in sections:
        for term in set(_tokenise(f"{section.title} {section.text}")):
            counts[term] = counts.get(term, 0) + 1
    idf = {term: math.log(1 + total / count) for term, count in counts.items()}
    return idf, math.log(1 + total)


def search(query: str, *, top_k: int = 3) -> list[tuple[Section, float]]:
    """Return the best-matching sections with a 0-1 relevance score.

    Score is the fraction of the question's *total meaning* the section covers,
    where meaning is measured in IDF weight. Unknown words count against the
    score rather than being ignored -- see the note in _idf().
    """
    query_terms = set(_tokenise(query))
    if not query_terms:
        return []

    idf, oov_weight = _idf()
    weights = {term: idf.get(term, oov_weight) for term in query_terms}
    total_weight = sum(weights.values()) or 1.0

    scored = []
    for section in load_sections():
        body_terms = set(_tokenise(section.text))
        title_terms = set(_tokenise(section.title))
        matched = {t for t in query_terms if t in body_terms or t in title_terms}
        if not matched:
            continue

        coverage = sum(weights[t] for t in matched) / total_weight
        # A title hit signals topic rather than passing mention -- a nudge, not
        # a doubling, so it can never rescue an otherwise unsupported question.
        boost = 1.0 + 0.25 * (len(matched & title_terms) / len(query_terms))
        scored.append((section, min(coverage * boost, 1.0)))

    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]
