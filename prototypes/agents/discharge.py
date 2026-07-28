"""DischargeDraft -- prototype 2.

Capability demonstrated: STRUCTURED GENERATION.
Free-text ward notes in, a fixed-schema discharge summary out. The schema is
enforced by the application, not hoped for from the model.

Also demonstrates the identifier check every clinical AI tool needs: text is
scanned locally for things that look like patient identifiers BEFORE anything
leaves the machine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import provider

SECTIONS = [
    "Diagnosis",
    "Course in Hospital",
    "Investigations",
    "Treatment Given",
    "Condition at Discharge",
    "Discharge Medications",
    "Follow-up Advice",
    "Danger Signs — Return Immediately If",
]

# Local patterns for things that must never be sent to an external model.
IDENTIFIER_PATTERNS = {
    "phone number": re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b"),
    "Aadhaar-like number": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "email address": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
    "hospital/MRN number": re.compile(r"\b(?:MRN|UHID|IP|OP)[\s:/-]*\d{3,}\b", re.I),
    "full date of birth": re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-](?:19|20)\d{2}\b"),
}

SYSTEM = f"""You are a discharge summary assistant for an Indian teaching hospital.

Convert the ward notes into a discharge summary with EXACTLY these headings, in
this order, each on its own line prefixed with '## ':
{chr(10).join('- ' + s for s in SECTIONS)}

Rules:
- Use only information present in the notes. Write "Not documented" where the notes are silent.
- Never invent doses, dates, or investigation results.
- Write danger signs in plain language a patient's family can act on.
- Keep it factual. No commentary.
"""

MOCK = """
## Diagnosis
Community-acquired pneumonia, right lower lobe. Type 2 diabetes mellitus, previously diagnosed.

## Course in Hospital
Admitted with four days of fever, productive cough and breathlessness. Started on intravenous
antibiotics and oxygen by nasal prongs. Fever settled by day 3. Oxygen requirement weaned off
by day 4. Ambulant and maintaining saturation on room air at discharge.

## Investigations
Chest X-ray: right lower zone consolidation. Total leucocyte count raised on admission,
normalising by day 4. Random blood glucose elevated on admission. HbA1c 8.2 percent.

## Treatment Given
Intravenous antibiotics for 4 days, changed to oral. Oxygen supplementation. Nebulisation.
Antipyretics. Insulin sliding scale during admission, transitioned to oral hypoglycaemic agent.

## Condition at Discharge
Afebrile. Saturation 97 percent on room air. Tolerating oral feeds. Ambulant independently.

## Discharge Medications
Oral antibiotic to complete the course as prescribed. Oral hypoglycaemic agent as charted.
Paracetamol as needed for fever.

## Follow-up Advice
Review in the outpatient department after 7 days with a repeat chest X-ray.
Diabetes clinic review in 2 weeks. Continue home blood glucose monitoring.

## Danger Signs — Return Immediately If
Fever returns or does not settle. Breathing becomes difficult or faster than usual.
Lips or fingertips look blue. Unable to eat or drink. Becomes drowsy or confused.
Blood sugar readings stay very high or very low.
"""


@dataclass
class DischargeResult:
    summary: str
    identifier_warnings: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)


def find_identifiers(text: str) -> list[str]:
    """Scan locally for probable patient identifiers. Runs before any network call."""
    return [
        f"Possible {label} found — remove before sending to any AI service"
        for label, pattern in IDENTIFIER_PATTERNS.items()
        if pattern.search(text)
    ]


def draft(notes: str) -> DischargeResult:
    """Turn ward notes into a schema-checked discharge summary."""
    if not notes.strip():
        return DischargeResult(summary="Paste some ward notes to draft a summary.")

    warnings = find_identifiers(notes)
    summary = provider.complete(
        f"WARD NOTES:\n\n{notes}\n\nProduce the discharge summary now.",
        system=SYSTEM,
        mock=MOCK,
        temperature=0.1,
    )

    # The schema is verified by us, not trusted from the model. This check is
    # what makes it 'structured generation' rather than 'hoping for structure'.
    missing = [s for s in SECTIONS if f"## {s}" not in summary]

    return DischargeResult(summary=summary, identifier_warnings=warnings, missing_sections=missing)
