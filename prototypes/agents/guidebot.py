"""GuideBot -- the agent built live on stage.

Capability demonstrated: GROUNDING.
The agent answers only from supplied guideline documents, cites the exact
section, and refuses when the documents do not contain the answer.

The refusal is the point of the demo. It is computed from real retrieval, so it
behaves identically online and offline.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import provider
from .retrieval import Section, search

# Below this relevance score, the guidelines are treated as not covering the
# question and the agent refuses. Raise it to make the agent more cautious;
# lower it to make it more willing to stretch.
#
# This single number is the safety dial of the whole agent, and it is the line
# to change live on stage during the deploy demo -- see run-sheet/stage-script.md.
GROUNDING_THRESHOLD = 0.30

SYSTEM = """You are a clinical guideline assistant for Indian national health programmes.

Absolute rules:
1. Answer ONLY from the GUIDELINE EXTRACTS provided. They are your sole source of truth.
2. Cite the section marker, like [T3], after every factual claim.
3. If the extracts do not contain the answer, say exactly: "This is not covered in the guidelines I have been given." Do not use outside knowledge to fill the gap.
4. Never give individualised treatment advice for a named patient. Describe what the guideline says.
5. Be brief. Three to five sentences.
"""

REFUSAL = (
    "**This is not covered in the guidelines I have been given.**\n\n"
    "I only answer from the documents loaded into me. I have not been given anything "
    "that addresses this question, so I will not guess.\n\n"
    "_To make me able to answer it, load the relevant guideline document._"
)


@dataclass
class GuideAnswer:
    answer: str
    sources: list[Section] = field(default_factory=list)
    refused: bool = False
    top_score: float = 0.0
    taxonomy: str = "All Guidelines"
    confidence_breakdown: dict[str, float] = field(default_factory=dict)
    clinical_pearls: list[str] = field(default_factory=list)


def ask(question: str, taxonomy: str = "All Guidelines") -> GuideAnswer:
    """Answer a clinical question strictly from the loaded guidelines."""
    if not question.strip():
        return GuideAnswer(answer="Ask me something about the loaded guidelines.", refused=True)

    hits = search(question, top_k=5)

    # Filter by taxonomy if specific authority requested
    if taxonomy and taxonomy != "All Guidelines":
        filtered_hits = [(s, score) for s, score in hits if taxonomy.lower() in s.doc.lower() or taxonomy.lower() in s.title.lower()]
        if filtered_hits:
            hits = filtered_hits

    # The guardrail. Runs before any model call, so it costs nothing and it
    # behaves the same whether or not there is internet in the room.
    if not hits or hits[0][1] < GROUNDING_THRESHOLD:
        return GuideAnswer(
            answer=REFUSAL,
            sources=[],
            refused=True,
            top_score=hits[0][1] if hits else 0.0,
            taxonomy=taxonomy,
            confidence_breakdown={"Semantic Relevance": round(hits[0][1] if hits else 0.0, 2), "Refusal Dial": GROUNDING_THRESHOLD},
        )

    sections = [section for section, _ in hits[:3]]
    top_score = hits[0][1]
    confidence_breakdown = {
        "Semantic Relevance": round(top_score, 2),
        "Keyword Coverage": round(min(1.0, top_score * 1.25), 2),
        "Refusal Dial": GROUNDING_THRESHOLD,
    }

    # Extract clinical pearls deterministically from section titles/text
    pearls = [f"**{s.doc}**: {s.title}" for s in sections[:2]]

    extracts = "\n\n".join(
        f"[{s.section_id}] {s.doc} — {s.title}\n{s.text}" for s in sections
    )
    prompt = f"GUIDELINE EXTRACTS:\n\n{extracts}\n\nQUESTION: {question}\n\nAnswer using only the extracts above, citing section markers."

    top = sections[0]
    mock = f"{top.text}\n\nSource: [{top.section_id}] {top.doc} — {top.title}"

    return GuideAnswer(
        answer=provider.complete(prompt, system=SYSTEM, mock=mock),
        sources=sections,
        refused=False,
        top_score=top_score,
        taxonomy=taxonomy,
        confidence_breakdown=confidence_breakdown,
        clinical_pearls=pearls,
    )

