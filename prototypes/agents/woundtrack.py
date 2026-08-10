"""WoundTrack -- Multimodal Diabetic Foot & Surgical Wound Staging Agent.

Capability: Visual Wound Staging, Tissue Composition Percentage, and Infection Risk Assessment.

Demonstrates: Combining wound image metadata validation, deterministic red-flag heuristics
(gas gangrene, exposed bone/tendon, spreading cellulitis), and vision model staging.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
import re

from agents import provider

TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

WOUND_SAMPLES = [
    {
        "label": "🦶 Diabetic Foot Ulcer: Plantar Surface (Wagner Grade 3)",
        "location": "Plantar Surface 1st MTP Joint",
        "file_name": "diabetic_foot_ulcer_exposed_bone.jpg",
        "context": "64-year-old diabetic male with deep chronic ulcer on plantar aspect of right foot. Probe-to-bone positive, purulent discharge, spreading erythema 3cm.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "🏥 Post-Op Surgical Wound: Sacral Pressure Injury",
        "location": "Sacral Area",
        "file_name": "sacral_pressure_ulcer_stage3.jpg",
        "context": "78-year-old bedbound female post-hip fracture repair. Sacral Stage 3 pressure injury with 40% slough and 60% red granulation tissue. No osteomyelitis.",
        "image_b64": TINY_PNG_B64,
    },
]


@dataclass
class WoundTrackResult:
    location: str
    quality_ok: bool
    has_critical_infection: bool
    alerts: list[str] = field(default_factory=list)
    report: str = ""


WOUND_RED_FLAGS = [
    (r"gas\s+gangrene|crepitus|necrotizing", "EMERGENCY ALERT: Suspected Necrotizing Soft Tissue Infection / Gas Gangrene — immediate surgical debridement consult required."),
    (r"probe[- ]to[- ]bone|exposed\s+bone", "CRITICAL INFECTION RISK: Exposed Bone / Probe-to-bone positive — high risk of Osteomyelitis; stat MRI & bone biopsy recommended."),
    (r"spreading\s+erythema\s*>|cellulitis", "HIGH RISK ALERT: Rapidly Spreading Cellulitis (> 2cm margin) — urgent IV antibiotic therapy required."),
]


def analyze_wound_image(
    image_bytes: bytes,
    file_name: str = "wound_photo.jpg",
    clinical_context: str = "",
    location: str = "Plantar Surface 1st MTP Joint",
) -> WoundTrackResult:
    """Analyze wound photo and calculate tissue breakdown & staging."""
    is_valid = len(image_bytes) >= 50
    alerts: list[str] = []
    combined_text = f"{file_name} {clinical_context}".lower()

    for pattern, alert_msg in WOUND_RED_FLAGS:
        if re.search(pattern, combined_text):
            alerts.append(alert_msg)

    has_critical = len(alerts) > 0
    image_b64 = base64.b64encode(image_bytes).decode("utf-8") if image_bytes else TINY_PNG_B64

    prompt = f"""Wound Staging & Infection Assessment:

Anatomical Wound Location: {location}
Patient Clinical Context & Duration:
{clinical_context or 'No context provided.'}

Deterministic Safety Alerts:
{chr(10).join(alerts) if alerts else 'None'}

Please provide a structured wound report:
1. **Wound Classification & Staging** (Wagner Grade / NPUAP Stage)
2. **Tissue Composition Percentage** (Granulation % vs Slough % vs Eschar / Necrotic %)
3. **Exudate & Infection Risk Assessment**
4. **Recommended Wound Dressing & Surgical Debridement Plan**
"""

    mock_report = f"""### Wound Breakdown & Staging Assessment ({location})

1. **Classification & Staging**:
   - **Wagner Classification**: Grade 3 (Deep ulcer with osteitis / abscess / bone involvement).
   - **NPUAP Stage**: Stage 3/4 full-thickness skin and tissue loss.

2. **Tissue Breakdown Ratio**:
   - **Granulation Tissue**: 50% (healthy vascularized pink bed).
   - **Fibrinous Slough**: 40% (yellow devitalized tissue).
   - **Necrotic Eschar**: 10%.

3. **Infection Risk**:
   - High risk for underlying **Osteomyelitis** given probe-to-bone finding and localized erythema.

4. **Clinical Action & Dressing Plan**:
   - Stat Plain Radiograph / MRI of the foot to evaluate cortical bone erosion.
   - Surgical sharp debridement of non-viable slough.
   - Apply non-adherent silver alginate moisture-retentive dressing.
   - Offloading footwear / total contact casting consult.
"""

    report = provider.complete_multimodal(
        prompt,
        image_b64=image_b64,
        mime_type="image/jpeg",
        system="You are an expert wound care specialist and vascular surgeon AI consultant.",
        mock=mock_report,
    )

    return WoundTrackResult(
        location=location,
        quality_ok=is_valid,
        has_critical_infection=has_critical,
        alerts=alerts,
        report=report,
    )
