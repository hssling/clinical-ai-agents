"""OtoscopeAI -- ENT Otoscopic Visual Diagnostic Agent.

Capability: Tympanic Membrane & External Auditory Canal Visual Diagnostic Assessment.

Demonstrates: Analyzing otoscopic imagery for otitis media & effusion while enforcing
deterministic red-flag checks for Acute Mastoiditis, TM Perforation, and Necrotizing Otitis Externa.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
import re

from agents import provider

TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

OTOSCOPE_SAMPLES = [
    {
        "label": "👂 Otoscopy: Acute Otitis Media (Bulging TM)",
        "ear_side": "Right Ear (AD)",
        "file_name": "otoscopy_acute_otitis_media.jpg",
        "context": "3-year-old child with 2 days of high fever (102°F), severe ear otalgia, and irritability. Bulging erythematous tympanic membrane with loss of cone of light.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "🚨 Otoscopy: Acute Mastoiditis (Retroauricular Swelling)",
        "ear_side": "Left Ear (AS)",
        "file_name": "otoscopy_acute_mastoiditis.jpg",
        "context": "6-year-old child with persistent untreated otitis media presenting with post-auricular tenderness, erythema, and outward displacement of the pinna.",
        "image_b64": TINY_PNG_B64,
    },
]


@dataclass
class OtoscopeResult:
    ear_side: str
    quality_ok: bool
    has_critical_ent_flag: bool
    alerts: list[str] = field(default_factory=list)
    report: str = ""


OTOSCOPE_RED_FLAGS = [
    (r"mastoiditis|retroauricular|post[- ]auricular", "EMERGENCY ENT ALERT: Suspected Acute Mastoiditis — High risk of intracranial spread; urgent ENT consult & STAT Temporal Bone CT required."),
    (r"perforation|perforated\s+tm", "CRITICAL ENT ALERT: Tympanic Membrane Perforation Identified — Avoid ototoxic drops (Aminoglycosides); urgent ENT evaluation."),
    (r"necrotizing\s+otitis|malignant\s+otitis", "HIGH RISK ALERT: Suspected Necrotizing (Malignant) Otitis Externa — urgent IV anti-Pseudomonal therapy required."),
]


def analyze_otoscopy_image(
    image_bytes: bytes,
    file_name: str = "otoscopy_photo.jpg",
    clinical_context: str = "",
    ear_side: str = "Right Ear (AD)",
) -> OtoscopeResult:
    """Analyze otoscopic image of tympanic membrane and ear canal."""
    is_valid = len(image_bytes) >= 50
    alerts: list[str] = []
    combined_text = f"{file_name} {clinical_context}".lower()

    for pattern, alert_msg in OTOSCOPE_RED_FLAGS:
        if re.search(pattern, combined_text):
            alerts.append(alert_msg)

    has_critical = len(alerts) > 0
    image_b64 = base64.b64encode(image_bytes).decode("utf-8") if image_bytes else TINY_PNG_B64

    prompt = f"""Otoscopic Visual Diagnostic Assessment:

Ear Examined: {ear_side}
Patient Clinical Symptoms & Duration:
{clinical_context or 'No context provided.'}

Deterministic Safety Alerts:
{chr(10).join(alerts) if alerts else 'None'}

Please provide a structured otoscopic report:
1. **Tympanic Membrane Characteristics** (Color, Translucency, Position, Bony Landmarks)
2. **External Auditory Canal (EAC) & Malleus Assessment**
3. **Primary Otolaryngological Impression / Differential**
4. **Recommended Antimicrobial & ENT Management Strategy**
"""

    mock_report = f"""### Otoscopic Examination Assessment ({ear_side})

1. **Tympanic Membrane Characteristics**:
   - **Color**: Intensely erythematous and opaque.
   - **Position**: Marked outward bulging with opacification.
   - **Landmarks**: Loss of normal bony landmarks (handle of malleus) and absent light reflex (cone of light).

2. **External Auditory Canal (EAC)**:
   - Mild concentric canal wall edema; no otorrhea or visible fungal hyphae.

3. **Primary Diagnosis**:
   - **Acute Otitis Media (AOM)** — Suppurative Stage (Right Ear).

4. **Recommended Clinical Action Plan**:
   - Initiate High-Dose Amoxicillin (80-90 mg/kg/day) for 10 days according to AAP guidelines.
   - Prescribe weight-appropriate analgesia (Ibuprofen / Paracetamol).
   - Re-evaluate in 48-72 hours if fever or otalgia persists.
"""

    report = provider.complete_multimodal(
        prompt,
        image_b64=image_b64,
        mime_type="image/jpeg",
        system="You are an expert board-certified otolaryngologist (ENT Specialist) and pediatric AI consultant.",
        mock=mock_report,
    )

    return OtoscopeResult(
        ear_side=ear_side,
        quality_ok=is_valid,
        has_critical_ent_flag=has_critical,
        alerts=alerts,
        report=report,
    )
