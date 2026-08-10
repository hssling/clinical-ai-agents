"""ChartVision -- Handwritten Prescription & Note Digitizer Agent.

Capability: Multimodal Clinical OCR, Handwriting Ambiguity Flagging, and High-Alert Medication Verification.

Demonstrates: Transcribing handwritten clinical prescriptions & ICU flowsheets while deterministically
scanning for high-alert drugs (Insulin, Digoxin, Methotrexate, Chemotherapy) and dosing ambiguities.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
import re

from agents import provider

TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

CHART_SAMPLES = [
    {
        "label": "✍️ Prescription: Ciprofloxacin & Insulin Order",
        "document_type": "Handwritten Prescription",
        "file_name": "handwritten_prescription_insulin.jpg",
        "context": "Rx: Ciprofloxacin 500mg BID x7d. Regular Insulin 10U SC AC TID. Metformin 1000mg BID. Dr. R. Sharma, MD.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "📋 ICU Flowsheet: Inotrope & Heparin Infusion",
        "document_type": "ICU Flowsheet Note",
        "file_name": "icu_flowsheet_heparin_dopamine.jpg",
        "context": "ICU Day 2: Noradrenaline 0.1 mcg/kg/min IV. Heparin IV infusion 1000 units/hr. Check APTT q6h.",
        "image_b64": TINY_PNG_B64,
    },
]


@dataclass
class ChartVisionResult:
    document_type: str
    quality_ok: bool
    has_high_alert_drug: bool
    alerts: list[str] = field(default_factory=list)
    report: str = ""


HIGH_ALERT_DRUGS = [
    (r"insulin", "HIGH-ALERT MEDICATION TRIGGER: Insulin Order Detected — Independent double-check required; verify blood glucose & dosing units."),
    (r"heparin|warfarin", "HIGH-ALERT MEDICATION TRIGGER: Anticoagulant Order — Verify baseline PTT/INR and bleeding risk prior to administration."),
    (r"methotrexate", "HIGH-ALERT MEDICATION TRIGGER: Methotrexate Order — Confirm weekly vs daily dosing schedule (fatal overdose risk if daily)."),
    (r"digoxin", "HIGH-ALERT MEDICATION TRIGGER: Digoxin Order — Check baseline serum potassium and renal function (eGFR)."),
]


def digitize_clinical_chart(
    image_bytes: bytes,
    file_name: str = "chart_prescription.jpg",
    context_notes: str = "",
    document_type: str = "Handwritten Prescription",
) -> ChartVisionResult:
    """Digitize handwritten medical orders and perform drug safety verification."""
    is_valid = len(image_bytes) >= 50
    alerts: list[str] = []
    combined_text = f"{file_name} {context_notes}".lower()

    for pattern, alert_msg in HIGH_ALERT_DRUGS:
        if re.search(pattern, combined_text):
            alerts.append(alert_msg)

    has_high_alert = len(alerts) > 0
    image_b64 = base64.b64encode(image_bytes).decode("utf-8") if image_bytes else TINY_PNG_B64

    prompt = f"""Clinical Chart / Handwritten Order OCR Transcription:

Document Category: {document_type}
Clinical Context / Notes:
{context_notes or 'No context provided.'}

Deterministic High-Alert Drug Triggers:
{chr(10).join(alerts) if alerts else 'None'}

Please provide a structured transcription report:
1. **Verbatim Text Transcription**
2. **Structured Medication Table** (Drug Name, Dosage, Route, Frequency, Duration)
3. **Handwriting Ambiguity & Unclear Abbreviation Flags**
4. **Safety & High-Alert Medication Double-Check Warnings**
"""

    mock_report = f"""### Clinical Chart Transcription & Verification ({document_type})

1. **Structured Medication Orders Table**:
   | Medication | Dosage | Route | Frequency | Duration | Safety Flag |
   |---|---|---|---|---|---|
   | **Ciprofloxacin** | 500 mg | Oral | BID | 7 days | Standard |
   | **Regular Insulin** | 10 Units | Subcutaneous | TID (Before meals) | Ongoing | ⚠️ **High-Alert** |
   | **Metformin** | 1000 mg | Oral | BID | Ongoing | Check eGFR |

2. **Handwriting & Abbreviation Audit**:
   - `AC` (Ante Cibum / before meals) is handwritten clearly.
   - `U` unit abbreviation flagged: Recommended to write out "Units" fully to prevent 10U being misread as 100.

3. **High-Alert Safety Recommendations**:
   - **Insulin Verification**: Perform independent nurse double-check of syringe volume before injection.
   - **Renal Monitor**: Verify recent serum creatinine prior to continuing 1000mg BID Metformin.
"""

    report = provider.complete_multimodal(
        prompt,
        image_b64=image_b64,
        mime_type="image/jpeg",
        system="You are an expert clinical pharmacist and hospital chart auditor AI consultant.",
        mock=mock_report,
    )

    return ChartVisionResult(
        document_type=document_type,
        quality_ok=is_valid,
        has_high_alert_drug=has_high_alert,
        alerts=alerts,
        report=report,
    )
