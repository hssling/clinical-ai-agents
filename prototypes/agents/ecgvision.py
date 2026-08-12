"""ECGVision -- 12-Lead Electrocardiogram Diagnostic & Emergency Safeguard Agent.

Capability: 12-Lead ECG Waveform Analysis & Ischemic / Arrhythmic Risk Stratification.

Demonstrates: Analyzing ECG telemetry images while enforcing deterministic red-flag
overrides for Acute STEMI, Ventricular Tachycardia, Severe Hyperkalemia, and QTc Prolongation.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
import re

from agents import provider

TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

ECG_SAMPLES = [
    {
        "label": "❤️ Baseline: Normal Sinus Rhythm (12-Lead)",
        "lead_view": "12-Lead ECG",
        "file_name": "ecg_normal_sinus.png",
        "context": "42-year-old asymptomatic adult presenting for routine executive health checkup. Heart rate 72 bpm, BP 118/76 mmHg. No chest pain or dyspnea.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "🚨 Emergency: Acute Anterior STEMI (Leads V1-V4)",
        "lead_view": "12-Lead ECG",
        "file_name": "ecg_stemi_elevation.png",
        "context": "58-year-old male presenting with 45 minutes of crushing substernal chest pain radiating to left arm, diaphoresis, and nausea. BP 90/60 mmHg, HR 105 bpm.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "⚡ Critical: Hyperkalemia Peaked T-Waves (K+ 7.2)",
        "lead_view": "12-Lead ECG",
        "file_name": "ecg_hyperkalemia.png",
        "context": "65-year-old end-stage renal disease patient who missed hemodialysis. Presents with muscle weakness, serum Potassium 7.2 mEq/L, and tall narrow peaked T-waves.",
        "image_b64": TINY_PNG_B64,
    },
]


@dataclass
class ECGResult:
    lead_view: str
    quality_ok: bool
    has_critical_cardiac_flag: bool
    alerts: list[str] = field(default_factory=list)
    report: str = ""


ECG_RED_FLAGS = [
    (r"stemi|st[- ]elevation|tombstone", "🚨 EMERGENCY CARDIAC ALERT: Suspected Acute ST-Elevation Myocardial Infarction (STEMI) — STAT Cath Lab Activation (<90 min Door-to-Balloon target) & Dual Antiplatelet Therapy required."),
    (r"vtach|ventricular tachycardia|vfib|fibrillation|torsades", "🚨 LETHAL ARRHYTHMIA ALERT: Sustained Ventricular Tachycardia / VFib Pattern Identified — Immediate Defibrillation & ACLS Protocol activation required."),
    (r"hyperkalemia|peaked t|tented t|sine wave", "🚨 CRITICAL METABOLIC ALERT: Hyperkalemic Cardiac Toxicity ECG Changes — Immediate IV Calcium Gluconate, Insulin/Dextrose, and STAT Hemodialysis consult required."),
    (r"qtc prolong|long qt|> 500|500ms", "⚠️ HIGH RISK DRUG SAFETY ALERT: Severe QTc Prolongation (>500 ms) — High risk of Torsades de Pointes; immediately discontinue QTc-prolonging medications."),
]


def analyze_ecg_image(
    image_bytes: bytes,
    file_name: str = "ecg_strip.png",
    clinical_context: str = "",
    lead_view: str = "12-Lead ECG",
) -> ECGResult:
    """Analyze 12-lead ECG or rhythm strip image and clinical presentation."""
    is_valid = len(image_bytes) >= 50
    alerts: list[str] = []
    combined_text = f"{file_name} {clinical_context}".lower()

    for pattern, alert_msg in ECG_RED_FLAGS:
        if re.search(pattern, combined_text):
            alerts.append(alert_msg)

    has_critical = len(alerts) > 0
    image_b64 = base64.b64encode(image_bytes).decode("utf-8") if image_bytes else TINY_PNG_B64

    prompt = f"""Clinical ECG Vision Diagnostic Assessment:

Lead View / Format: {lead_view}
Patient Presentation & Clinical Context:
{clinical_context or 'No context provided.'}

Deterministic Safety Overrides Active:
{chr(10).join(alerts) if alerts else 'None'}

Please provide a structured electrocardiology evaluation:
1. **Rhythm, Rate & Axis Analysis** (Heart Rate, P-wave morphology, PR interval, QRS duration, QTc)
2. **Ischemic & Morphological Assessment** (ST segments, T waves, Q waves by anatomical territory)
3. **Primary Cardiology Diagnosis / Differential**
4. **Emergency Cardiac Management Plan** (Interventions, pharmacotherapy, monitoring)
"""

    mock_report = f"""### Electrocardiogram (ECG) Diagnostic Assessment ({lead_view})

1. **Rhythm, Rate & Axis Analysis**:
   - **Rate & Rhythm**: Sinus rhythm at 74 bpm with regular R-R intervals.
   - **Intervals**: PR interval 158 ms, QRS duration 86 ms, QTc interval 412 ms (normal <450 ms).
   - **Axis**: Normal cardiac axis (~ +45 degrees).

2. **Ischemic & Morphological Assessment**:
   - **Leads V1-V4**: Concave ST segments with normal T-wave inversion/upright transition.
   - **Leads II, III, aVF**: No ST elevations or pathological Q waves.
   - **Leads I, aVL**: Intact R-wave progression; no reciprocal depression.

3. **Primary Diagnosis**:
   - **Normal 12-Lead Electrocardiogram** — No acute ischemic ST-T changes or conduction delay.

4. **Recommended Clinical Strategy**:
   - Reassure patient; no immediate emergency catheterization required based on baseline trace.
   - Correlate with serial troponin T/I levels if presenting with acute atypical chest pain.
"""

    report = provider.complete_multimodal(
        prompt,
        image_b64=image_b64,
        mime_type="image/png",
        system="You are an expert board-certified cardiologist and electrophysiology consultant.",
        mock=mock_report,
    )

    return ECGResult(
        lead_view=lead_view,
        quality_ok=is_valid,
        has_critical_cardiac_flag=has_critical,
        alerts=alerts,
        report=report,
    )
