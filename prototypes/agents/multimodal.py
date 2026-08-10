"""RadVision -- Multimodal Clinical AI Agent.

Capability: Multimodal Clinical Vision & Diagnostic Guardrails.

Demonstrates: Combining image metadata validation, deterministic clinical safety checks
(panic/red-flag alerts), and multimodal LLM vision reasoning to analyze medical imagery
(Chest X-Ray, Dermatology, ECG, Clinical Photos).
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
import os
import re

from agents import provider


@dataclass
class ImageQualityCheck:
    is_valid: bool
    mime_type: str
    file_size_kb: float
    issues: list[str] = field(default_factory=list)


@dataclass
class RadVisionResult:
    modality: str
    quality_check: ImageQualityCheck
    has_critical_red_flag: bool
    red_flags: list[str] = field(default_factory=list)
    report: str = ""


# Deterministic red-flag triggers for clinical vision safety
RED_FLAG_PATTERNS = [
    (r"(?:tension\s+)?pneumothorax", "CRITICAL ALERT: Suspected Pneumothorax — risk of tension collapse; urgent bedside evaluation & chest tube consultation required."),
    (r"st[- ]?elevation|stemi|acute\s+mi|inferior\s+mi", "CRITICAL ALERT: Suspected Acute ST-Elevation Myocardial Infarction (STEMI) — activate emergency cardiac cath lab protocol."),
    (r"melanoma|nodular\s+lesion|abcde\s+positive", "HIGH RISK ALERT: High dermatological concern for Malignant Melanoma — urgent punch/excisional biopsy required."),
    (r"large\s+pleural\s+effusion|mediastinal\s+shift", "URGENT ALERT: Severe Pleural Effusion with Mediastinal Shift — immediate drainage evaluation."),
]


def check_image_quality(image_bytes: bytes, file_name: str) -> ImageQualityCheck:
    """Validate image bytes and size deterministically before calling vision model."""
    issues: list[str] = []
    file_size_kb = len(image_bytes) / 1024.0

    ext = os.path.splitext(file_name.lower())[1]
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }
    mime_type = mime_map.get(ext, "image/jpeg")

    if len(image_bytes) < 50:
        issues.append("Image payload is too small or corrupted (< 50 bytes).")
    if file_size_kb > 15000:
        issues.append("Image file exceeds 15 MB threshold for real-time vision processing.")

    return ImageQualityCheck(
        is_valid=len(issues) == 0,
        mime_type=mime_type,
        file_size_kb=round(file_size_kb, 1),
        issues=issues,
    )


def scan_red_flags(clinical_context: str, file_name: str) -> tuple[bool, list[str]]:
    """Scan text context and file indicators deterministically for life-threatening visual conditions."""
    combined_text = f"{file_name} {clinical_context}".lower()
    alerts: list[str] = []

    for pattern, alert_msg in RED_FLAG_PATTERNS:
        if re.search(pattern, combined_text):
            alerts.append(alert_msg)

    return len(alerts) > 0, alerts


def analyze_clinical_image(
    image_bytes: bytes,
    file_name: str = "clinical_image.jpg",
    clinical_context: str = "",
    modality: str = "Chest X-Ray",
) -> RadVisionResult:
    """Perform deterministic image quality/red-flag checks and run multimodal vision interpretation."""
    quality_check = check_image_quality(image_bytes, file_name)
    if not quality_check.is_valid:
        return RadVisionResult(
            modality=modality,
            quality_check=quality_check,
            has_critical_red_flag=False,
            red_flags=[],
            report=f"**Processing Error**: Image validation failed.\n" + "\n".join(f"- {i}" for i in quality_check.issues),
        )

    has_red_flag, red_flags = scan_red_flags(clinical_context, file_name)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = f"""Multimodal Clinical Image Analysis Request:

Image Modality: {modality}
Patient Clinical Context / History:
{clinical_context or 'No additional context provided.'}

Deterministic Safety Flags Detected:
{chr(10).join(red_flags) if red_flags else 'None'}

Please provide a structured clinical image interpretation including:
1. **Visual Quality & Modality Verification**
2. **Key Radiological / Clinical Findings** (bullet points with anatomical descriptions)
3. **Differential Diagnosis & Primary Impression** (with estimated clinical probability)
4. **Recommended Immediate Action Plan & Follow-up Studies**
"""

    mock_report = f"""### Multimodal Clinical Vision Report ({modality})

1. **Visual Quality & Modality Verification**:
   - **Modality**: {modality} (Validated)
   - **Quality**: Diagnostic quality image, adequate positioning, and contrast.

2. **Key Clinical Findings**:
   - Dense focal consolidation noted in the right lower lung zone with air bronchograms.
   - Blunting of the right costophrenic angle suggesting mild reactive parapneumonic effusion.
   - Cardiac silhouette and mediastinal contours are within normal limits for age.

3. **Primary Differential Impression**:
   - **Community-Acquired Pneumonia (CAP)** — High Likelihood (Right Lower Lobe).
   - Parapneumonic pleural effusion.
   - Rule out localized atelectasis.

4. **Recommended Next Steps**:
   - Initiate targeted empirical antibiotic therapy according to local CAP guidelines.
   - Obtain Sputum Culture & Blood Cultures prior to second antibiotic dose.
   - Monitor pulse oximetry and serial inflammatory markers (CRP / Procalcitonin).
"""

    report = provider.complete_multimodal(
        prompt,
        image_b64=image_b64,
        mime_type=quality_check.mime_type,
        system="You are an expert board-certified clinical radiologist and dermatologist AI consultant.",
        mock=mock_report,
    )

    return RadVisionResult(
        modality=modality,
        quality_check=quality_check,
        has_critical_red_flag=has_red_flag,
        red_flags=red_flags,
        report=report,
    )
