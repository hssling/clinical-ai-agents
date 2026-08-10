"""TriageAssist -- prototype 3.

Capability demonstrated: THE AGENTIC LOOP.
Unlike the other three, this agent does not answer once. It decides whether it
has enough information, asks a follow-up if not, and stops when it either hits a
red flag or exhausts its question budget.

Two teaching points are built into the design on purpose:

1. THE LOOP MUST TERMINATE. MAX_QUESTIONS is a hard budget. An agent that can
   decide to keep going must also be forced to stop.
2. SAFETY LOGIC IS LOCAL AND DETERMINISTIC. Red-flag detection is plain Python,
   not a model call. It cannot be talked out of escalating, it cannot hallucinate,
   and it behaves identically with the wifi unplugged.

EDUCATIONAL DEMONSTRATION ONLY. NOT FOR CLINICAL USE.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import provider

MAX_QUESTIONS = 3

# ---------------------------------------------------------------------------
# THE CLINICAL SAFETY LAYER
#
# Dr. Siddalingaiah: this table is yours. It encodes which presentations must
# escalate immediately regardless of anything else the agent thinks. Edit it to
# match your own practice and local referral pathways -- adding or removing a
# line here is the single most useful live edit you can make on stage, because
# it shows the room that the clinician, not the model, owns the safety rules.
#
# Format: regex pattern -> (why it escalates, where it goes)
# ---------------------------------------------------------------------------
RED_FLAGS: dict[str, tuple[str, str]] = {
    r"\bchest pain\b|\bcrushing\b|\bpain.{0,20}(left arm|jaw)\b":
        ("Possible acute coronary syndrome", "Immediate ECG and emergency referral"),
    r"\bbreathless|short(ness)? of breath|unable to (speak|complete)\b":
        ("Respiratory distress", "Assess saturation now; emergency referral if low"),
    r"\bunconscious|drowsy|confus|altered sensorium|not responding\b":
        ("Altered consciousness", "Emergency referral, check glucose immediately"),
    r"\bconvuls|seizure|fits?\b":
        ("Seizure activity", "Emergency referral"),
    r"\bbleeding|haemorrhag|hemorrhag|blood in vomit|black stool\b":
        ("Active or significant bleeding", "Emergency referral"),
    r"\bstiff neck|neck rigidity|photophobia\b":
        ("Possible meningism", "Emergency referral"),
    r"\bweakness.{0,20}(one side|face)|slurred speech|facial droop\b":
        ("Possible stroke", "Stroke pathway, emergency referral within window"),
    r"\bsevere abdominal pain|rigid abdomen|guarding\b":
        ("Possible acute abdomen", "Surgical opinion urgently"),
    r"\bpregnan.{0,30}(bleed|pain|reduced (fetal|foetal) move)":
        ("Obstetric emergency", "Immediate obstetric referral"),
    r"\binfant|newborn|neonate\b.{0,40}\b(fever|not feeding|lethargic)\b":
        ("Sick young infant", "Immediate paediatric referral"),
    r"\bsuicid|self harm|end my life\b":
        ("Risk of self-harm", "Immediate mental health assessment, do not leave alone"),
}

SYSTEM = """You are a triage assistant supporting a health worker at a primary care facility in India.

You do NOT diagnose and you do NOT prescribe. Your only job is to ask the single
most useful next question that would change how urgently this person is seen.

Reply with ONE short question and nothing else. No preamble, no explanation.
"""

FALLBACK_QUESTIONS = [
    "How long has this been going on, and is it getting worse?",
    "Is there any fever, breathlessness, or bleeding along with this?",
    "Does the person have diabetes, high blood pressure, is pregnant, or is under five years old?",
]


# Cues that flip a red-flag match into a negative finding. Without these, a
# patient answering "no bleeding" escalates for bleeding.
NEGATION_CUES = (
    "no ", "not ", "never ", "denie", "denies ", "without ", "absent",
    "nil ", "none ", "negative for ", "ruled out", "no h/o", "n/o ",
)
NEGATION_WINDOW = 30  # characters to look back before a match


@dataclass
class TriageState:
    complaint: str
    answers: list[tuple[str, str]] = field(default_factory=list)

    @property
    def transcript(self) -> str:
        """Full conversation -- for display and for the model."""
        lines = [f"Presenting complaint: {self.complaint}"]
        lines += [f"Q: {q}\nA: {a}" for q, a in self.answers]
        return "\n".join(lines)

    @property
    def patient_text(self) -> str:
        """Only what the PATIENT said -- the complaint and the answers.

        Red flags must never be scanned over the agent's own questions. Asking
        "any bleeding?" and hearing "no" would otherwise escalate for bleeding:
        the agent would be reacting to its own words.
        """
        return "\n".join([self.complaint, *(a for _, a in self.answers)])


@dataclass
class TriageStep:
    done: bool
    question: str = ""
    escalate: bool = False
    reasons: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    summary: str = ""
    esi_level: int = 4
    heart_score: int | None = None
    qsofa_score: int | None = None



def _is_negated(text: str, match_start: int) -> bool:
    """Was this finding explicitly denied just before it was mentioned?

    Deliberately crude. Clinical negation detection is a research problem; this
    catches the common "no chest pain" / "denies bleeding" phrasing and nothing
    more. It errs towards escalating -- an unhandled phrasing raises the flag
    rather than suppressing it.
    """
    window = text[max(0, match_start - NEGATION_WINDOW):match_start]
    return any(cue in window for cue in NEGATION_CUES)


def check_red_flags(text: str) -> tuple[list[str], list[str]]:
    """Deterministic, local, offline. The model never gets a vote on this."""
    reasons, actions = [], []
    lowered = text.lower()
    for pattern, (reason, action) in RED_FLAGS.items():
        for match in re.finditer(pattern, lowered):
            if not _is_negated(lowered, match.start()):
                reasons.append(reason)
                actions.append(action)
                break
    return reasons, actions


def calculate_esi_level(reasons: list[str], text: str) -> int:
    """Calculate Emergency Severity Index (ESI) triage level (1 to 5)."""
    text_lower = text.lower()
    if any(r in text_lower for r in ["unconscious", "respiratory distress", "cardiac arrest", "seizure"]):
        return 1  # Resuscitation (Immediate)
    if reasons:
        return 2  # Emergent (High Risk)
    if "fever" in text_lower or "vomiting" in text_lower or "pain" in text_lower:
        return 3  # Urgent (Multiple resources)
    return 4  # Less Urgent


def calculate_clinical_scores(text: str) -> tuple[int | None, int | None]:
    """Calculate HEART score for chest pain & qSOFA score for sepsis deterministically."""
    text_lower = text.lower()
    heart_score = None
    qsofa_score = None

    if "chest pain" in text_lower or "angina" in text_lower:
        # HEART Score calculation heuristic (History, ECG, Age, Risk factors, Troponin)
        h = 2 if "crushing" in text_lower or "radiation" in text_lower else 1
        e = 0
        a = 2 if "60" in text_lower or "65" in text_lower or "70" in text_lower else 1
        r = 2 if "diabetes" in text_lower or "smok" in text_lower or "htn" in text_lower else 1
        t = 1
        heart_score = h + e + a + r + t

    if "fever" in text_lower or "infection" in text_lower or "sepsis" in text_lower:
        # qSOFA: RR >= 22 (1 pt), Altered Mentation (1 pt), SBP <= 100 (1 pt)
        qsofa_score = 0
        if any(w in text_lower for w in ["drowsy", "confused", "altered", "lethargic"]):
            qsofa_score += 1
        if any(w in text_lower for w in ["breathless", "rr 2", "rr 3", "tachypnea"]):
            qsofa_score += 1
        if any(w in text_lower for w in ["hypotension", "low bp", "sbp 90", "shock"]):
            qsofa_score += 1

    return heart_score, qsofa_score


def step(state: TriageState) -> TriageStep:
    """Advance the loop by one turn: escalate, ask, or conclude."""
    # Scans patient_text, never transcript -- see TriageState.patient_text.
    reasons, actions = check_red_flags(state.patient_text)
    esi_level = calculate_esi_level(reasons, state.patient_text)
    heart_score, qsofa_score = calculate_clinical_scores(state.patient_text)

    # Escalation short-circuits the loop. Nothing overrides a red flag.
    if reasons:
        return TriageStep(
            done=True,
            escalate=True,
            reasons=reasons,
            actions=sorted(set(actions)),
            summary="Red flag identified. Escalate now — do not continue questioning.",
            esi_level=esi_level,
            heart_score=heart_score,
            qsofa_score=qsofa_score,
        )

    # Budget exhausted: stop and hand over. An agent that never stops is a bug.
    if len(state.answers) >= MAX_QUESTIONS:
        return TriageStep(
            done=True,
            escalate=False,
            summary=(
                "No red flags identified in the information given. "
                "Proceed with routine assessment by the medical officer. "
                "Re-triage immediately if the person deteriorates."
            ),
            esi_level=esi_level,
            heart_score=heart_score,
            qsofa_score=qsofa_score,
        )

    asked = [q for q, _ in state.answers]
    prompt = (
        f"{state.transcript}\n\n"
        f"Questions already asked: {asked or 'none'}\n\n"
        "What is the single most useful next question?"
    )
    mock = FALLBACK_QUESTIONS[len(state.answers) % len(FALLBACK_QUESTIONS)]
    question = provider.complete(prompt, system=SYSTEM, mock=mock, temperature=0.3).strip()

    return TriageStep(
        done=False,
        question=question.split("\n")[0][:200],
        esi_level=esi_level,
        heart_score=heart_score,
        qsofa_score=qsofa_score,
    )
