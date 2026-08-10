"""FundusVision -- Retinal Screening & Ophthalmology Multimodal Agent.

Capability: Fundus Photomicrograph Screening for Retinopathy & Neurological Optic Disc Emergencies.

Demonstrates: Screening retinal imagery for Diabetic/Hypertensive Retinopathy while enforcing
deterministic red-flag checks for Papilledema (elevated ICP) and neovascularization.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
import re

from agents import provider

TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

FUNDUS_SAMPLES = [
    {
        "label": "👁️ Retinal Fundus: Severe NPDR (Diabetic Retinopathy)",
        "eye_side": "Right Eye (OD)",
        "file_name": "fundus_diabetic_retinopathy_npdr.jpg",
        "context": "56-year-old male with 14-year history of Type 2 DM (HbA1c 9.2%). Multiple hard exudates, microaneurysms, and macular edema.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "🚨 Optic Disc: Bilateral Papilledema (Elevated ICP)",
        "eye_side": "Bilateral Fundus (OU)",
        "file_name": "fundus_papilledema_elevated_icp.jpg",
        "context": "28-year-old female presenting with severe morning headaches, pulsatile tinnitus, and transient visual obscurations. Optic disc margin blurring and hyperemia.",
        "image_b64": TINY_PNG_B64,
    },
]


@dataclass
class FundusVisionResult:
    eye_side: str
    quality_ok: bool
    has_papilledema_alert: bool
    alerts: list[str] = field(default_factory=list)
    report: str = ""


FUNDUS_RED_FLAGS = [
    (r"papilledema|disc\s+swelling|blurred\s+disc\s+margin", "EMERGENCY NEUROLOGICAL ALERT: Bilateral Papilledema / Optic Disc Swelling — Risk of elevated Intracranial Pressure (ICP); urgent Neuro-imaging (STAT Brain MRI/CT) required."),
    (r"neovascularization|preretinal\s+hemorrhage", "URGENT OPHTHALMOLOGY ALERT: Proliferative Retinopathy with Neovascularization — high risk of vitreous hemorrhage & tractional retinal detachment; urgent panretinal photocoagulation consult."),
]


def analyze_fundus_image(
    image_bytes: bytes,
    file_name: str = "fundus_photo.jpg",
    clinical_context: str = "",
    eye_side: str = "Right Eye (OD)",
) -> FundusVisionResult:
    """Analyze retinal fundus photograph and grade retinopathy / optic disc abnormalities."""
    is_valid = len(image_bytes) >= 50
    alerts: list[str] = []
    combined_text = f"{file_name} {clinical_context}".lower()

    for pattern, alert_msg in FUNDUS_RED_FLAGS:
        if re.search(pattern, combined_text):
            alerts.append(alert_msg)

    has_papilledema = len(alerts) > 0
    image_b64 = base64.b64encode(image_bytes).decode("utf-8") if image_bytes else TINY_PNG_B64

    prompt = f"""Retinal Fundus Screening & Optic Disc Assessment:

Eye Examined: {eye_side}
Patient Clinical Context & Ocular History:
{clinical_context or 'No context provided.'}

Deterministic Safety Alerts:
{chr(10).join(alerts) if alerts else 'None'}

Please provide a structured ophthalmic screening report:
1. **Optic Disc & Cup-to-Disc Ratio (CDR) Assessment**
2. **Retinal Vascular & Macular Findings** (Microaneurysms, Hard Exudates, Hemorrhages)
3. **ETDRS Diabetic Retinopathy Severity Grading**
4. **Recommended Ophthalmic / Neurological Management & Referral Window**
"""

    mock_report = f"""### Retinal Fundus Screening Report ({eye_side})

1. **Optic Disc Assessment**:
   - **Disc Margins**: Sharp, distinct borders with no hyperemia or elevation.
   - **Cup-to-Disc Ratio**: 0.3 (Symmetrical, within normal limits).

2. **Vascular & Macular Findings**:
   - Multiple cotton-wool spots, hard exudates arranged in circinate pattern near the fovea.
   - Numerous intraretinal dot-and-blot hemorrhages across 4 quadrants.

3. **Retinopathy Severity Grade**:
   - **Severe Non-Proliferative Diabetic Retinopathy (NPDR)** with clinically significant macular edema (CSME).

4. **Referral & Clinical Action Plan**:
   - Refer to Retina Specialist within **1 to 2 weeks** for OCT macular scan & intravitreal anti-VEGF evaluation.
   - Optimize systemic HbA1c (< 7.0%) and blood pressure (< 130/80 mmHg).
"""

    report = provider.complete_multimodal(
        prompt,
        image_b64=image_b64,
        mime_type="image/jpeg",
        system="You are an expert board-certified ophthalmologist and retina specialist AI consultant.",
        mock=mock_report,
    )

    return FundusVisionResult(
        eye_side=eye_side,
        quality_ok=is_valid,
        has_papilledema_alert=has_papilledema,
        alerts=alerts,
        report=report,
    )
