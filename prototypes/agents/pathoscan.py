"""PathoScan -- Digital Pathology & Histology Multimodal Agent.

Capability: Photomicrograph & Biopsy Slide Analysis with Diagnostic Safety Checks.

Demonstrates: Combining histology image metadata validation, deterministic malignancy red-flag
triggers (vascular invasion, high mitotic index), and multimodal vision reasoning to assess
biopsy specimens and IHC requirements.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
import os
import re

from agents import provider

TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

PATHOLOGY_SAMPLES = [
    {
        "label": "🔬 Breast Biopsy: Invasive Ductal Carcinoma",
        "tissue_type": "Breast Tissue Biopsy",
        "file_name": "breast_biopsy_he_stain.jpg",
        "context": "Core needle biopsy of 2.5cm firm breast mass in a 52-year-old female. H&E stain, high power field. High mitotic count and lymphovascular invasion noted.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "🧫 Lymph Node: Granulomatous Lymphadenitis",
        "tissue_type": "Lymph Node Biopsy",
        "file_name": "lymph_node_granuloma_tb.jpg",
        "context": "Excisional cervical lymph node biopsy in a 34-year-old male with chronic fever and night sweats. Caseating necrotizing granulomas with Langhans giant cells.",
        "image_b64": TINY_PNG_B64,
    },
]


@dataclass
class PathoScanResult:
    tissue_type: str
    quality_ok: bool
    has_critical_malignancy: bool
    alerts: list[str] = field(default_factory=list)
    report: str = ""


MALIGNANCY_RED_FLAGS = [
    (r"lymphovascular\s+invasion|lvi\s+positive", "CRITICAL PATHOLOGY ALERT: Lymphovascular Invasion Identified — High risk of nodal metastasis; urgent staging required."),
    (r"high\s+mitotic\s+(?:count|rate|index)", "HIGH-GRADE ALERT: Elevated Mitotic Index (>20 HPF) — aggressive proliferation pattern."),
    (r"poorly\s+differentiated|anaplastic", "HIGH RISK ALERT: Poorly Differentiated / Anaplastic Cytology — urgent multidisciplinary oncology consult."),
]


def analyze_pathology_slide(
    image_bytes: bytes,
    file_name: str = "biopsy_slide.jpg",
    clinical_context: str = "",
    tissue_type: str = "Breast Tissue Biopsy",
) -> PathoScanResult:
    """Analyze biopsy slide image and generate structured histopathology assessment."""
    is_valid = len(image_bytes) >= 50
    alerts: list[str] = []
    combined_text = f"{file_name} {clinical_context}".lower()

    for pattern, alert_msg in MALIGNANCY_RED_FLAGS:
        if re.search(pattern, combined_text):
            alerts.append(alert_msg)

    has_critical = len(alerts) > 0
    image_b64 = base64.b64encode(image_bytes).decode("utf-8") if image_bytes else TINY_PNG_B64

    prompt = f"""Digital Pathology Histology Assessment:

Specimen / Tissue Type: {tissue_type}
Clinical & Histological History:
{clinical_context or 'No context provided.'}

Deterministic Malignancy Alerts Triggered:
{chr(10).join(alerts) if alerts else 'None'}

Please provide a structured pathology interpretation:
1. **Architectural & Cytological Pattern Assessment**
2. **Nuclear Grade & Mitotic Activity**
3. **Primary Histopathological Diagnosis / Differential**
4. **Recommended Ancillary & Immunohistochemistry (IHC) Panels**
"""

    mock_report = f"""### Digital Pathology Assessment ({tissue_type})

1. **Architectural & Cytological Assessment**:
   - Infiltrative nests and cords of atypical epithelial cells disturbing normal parenchymal architecture.
   - Marked pleomorphism, hyperchromatic nuclei, and prominent nucleoli present.

2. **Nuclear Grade & Mitotic Activity**:
   - **Histological Grade**: Grade 3 (Poorly Differentiated).
   - **Mitotic Activity**: Elevated (>18 mitotic figures per 10 HPF).

3. **Primary Diagnosis**:
   - **Invasive Ductal Carcinoma (NOS)** of the breast.
   - Focal lymphovascular invasion noted.

4. **Recommended IHC Panel**:
   - Estrogen Receptor (ER), Progesterone Receptor (PR), HER2/neu protein expression, and Ki-67 proliferation index.
"""

    report = provider.complete_multimodal(
        prompt,
        image_b64=image_b64,
        mime_type="image/jpeg",
        system="You are an expert board-certified surgical pathologist and dermatopathologist AI consultant.",
        mock=mock_report,
    )

    return PathoScanResult(
        tissue_type=tissue_type,
        quality_ok=is_valid,
        has_critical_malignancy=has_critical,
        alerts=alerts,
        report=report,
    )
