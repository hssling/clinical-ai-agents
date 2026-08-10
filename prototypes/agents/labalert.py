"""LabAlert -- Clinical Lab Interpreter & Panic Value Escalator.

Capability: Numerical Range Boundary Check & Critical Value Escalation.

Demonstrates: Combining deterministic numerical range validation with LLM clinical interpretation.
Laboratory "Panic Values" (life-threatening abnormalities) are detected locally via numeric thresholds
before generating the clinical summary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re

from agents import provider

# Deterministic Panic Value thresholds
PANIC_THRESHOLDS = {
    "potassium": {"low_panic": 2.8, "high_panic": 6.0, "unit": "mEq/L"},
    "sodium": {"low_panic": 120, "high_panic": 158, "unit": "mEq/L"},
    "troponin": {"high_panic": 0.04, "unit": "ng/mL"},
    "platelets": {"low_panic": 20000, "high_panic": 1000000, "unit": "/µL"},
    "hemoglobin": {"low_panic": 6.5, "high_panic": 20.0, "unit": "g/dL"},
    "glucose": {"low_panic": 40, "high_panic": 400, "unit": "mg/dL"},
    "ph": {"low_panic": 7.20, "high_panic": 7.60, "unit": ""},
}


@dataclass
class LabValue:
    test_name: str
    val: float
    unit: str
    status: str  # NORMAL, ABNORMAL, PANIC_LOW, PANIC_HIGH


@dataclass
class LabAlertResult:
    has_panic: bool
    panic_alerts: list[str] = field(default_factory=list)
    lab_values: list[LabValue] = field(default_factory=list)
    summary: str = ""


def check_lab_thresholds(lab_text: str) -> tuple[bool, list[str], list[LabValue]]:
    """Parse laboratory metrics and evaluate numeric panic limits deterministically."""
    panic_alerts: list[str] = []
    parsed_values: list[LabValue] = []
    has_panic = False

    text_lower = lab_text.lower()

    # Pattern matches test name followed by colon/equals and numeric value
    patterns = [
        ("potassium", r"(?:potassium|k\+?)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("sodium", r"(?:sodium|na\+?)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("troponin", r"(?:troponin[ -]?[it]?)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("platelets", r"(?:platelets?|plt)\s*[:=]?\s*([0-9,]+)"),
        ("hemoglobin", r"(?:hemoglobin|hb|hgb)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("glucose", r"(?:glucose|blood sugar)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("ph", r"(?:ph)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
    ]

    for test_key, pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            raw_val = match.group(1).replace(",", "")
            try:
                val = float(raw_val)
            except ValueError:
                continue

            limits = PANIC_THRESHOLDS[test_key]
            unit = limits["unit"]
            status = "NORMAL"

            if "low_panic" in limits and val <= limits["low_panic"]:
                status = "PANIC_LOW"
                has_panic = True
                panic_alerts.append(
                    f"CRITICAL CRITICAL PANIC: {test_key.title()} level {val} {unit} is dangerously low (<= {limits['low_panic']} {unit}). Immediate clinical intervention required."
                )
            elif "high_panic" in limits and val >= limits["high_panic"]:
                status = "PANIC_HIGH"
                has_panic = True
                panic_alerts.append(
                    f"CRITICAL PANIC VALUE: {test_key.title()} level {val} {unit} is dangerously elevated (>= {limits['high_panic']} {unit}). High cardiac / metabolic risk."
                )

            parsed_values.append(LabValue(test_name=test_key.title(), val=val, unit=unit, status=status))

    return has_panic, panic_alerts, parsed_values


def analyze_labs(lab_text: str, patient_context: str = "") -> LabAlertResult:
    """Perform deterministic lab panic scan and generate expert clinical lab interpretation."""
    has_panic, panic_alerts, parsed_values = check_lab_thresholds(lab_text)

    prompt = f"""Clinical Laboratory Panel Interpretation:

Patient Clinical Context: {patient_context or 'Not specified'}
Laboratory Report Data:
{lab_text}

Panic Alert Triggered: {'YES' if has_panic else 'NO'}
Identified Panic Alerts:
{chr(10).join(panic_alerts) if panic_alerts else 'None'}

Provide a structured clinical interpretation including:
1. Critical Findings & Immediate Risk Assessment
2. Likely Etiologies & Differential Diagnoses
3. Recommended Immediate Diagnostic & Therapeutic Actions
"""

    mock_summary = """### Clinical Laboratory Panel Summary

1. **CRITICAL PANIC ALERT**:
   - **Potassium 6.4 mEq/L (PANIC HIGH)**: Severe hyperkalemia posing immediate risk of lethal cardiac arrhythmias, heart block, or cardiac arrest.
   - **Troponin I 0.12 ng/mL (ELEVATED)**: Indicates active myocardial injury.

2. **Clinical Interpretation**:
   - Acute hyperkalemic emergency in setting of suspected myocardial injury or acute kidney injury.

3. **Immediate Clinical Action Plan**:
   - Obtain immediate 12-lead ECG to check for peak T waves, QRS widening, or sine waves.
   - Administer 10% Calcium Gluconate IV for cardiac membrane stabilization.
   - Administer Insulin 10 units IV with 50mL D50W to drive potassium intracellularly.
   - Stat Cardiology & ICU consult.
"""

    summary = provider.complete(
        prompt,
        system="You are an expert clinical pathologist and emergency medicine consultant AI.",
        mock=mock_summary,
    )

    return LabAlertResult(
        has_panic=has_panic,
        panic_alerts=panic_alerts,
        lab_values=parsed_values,
        summary=summary,
    )
