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
    "lactate": {"high_panic": 4.0, "unit": "mmol/L"},
    "calcium": {"low_panic": 6.5, "high_panic": 13.0, "unit": "mg/dL"},
}


@dataclass
class LabValue:
    test_name: str
    val: float
    unit: str
    status: str  # NORMAL, ABNORMAL, PANIC_LOW, PANIC_HIGH


@dataclass
class ABGInterpretation:
    disorder: str
    anion_gap: float | None = None
    compensation: str = ""


@dataclass
class LabAlertResult:
    has_panic: bool
    panic_alerts: list[str] = field(default_factory=list)
    lab_values: list[LabValue] = field(default_factory=list)
    abg_analysis: ABGInterpretation | None = None
    summary: str = ""


def calculate_abg(ph: float | None, pco2: float | None, hco3: float | None, na: float | None = None, cl: float | None = None) -> ABGInterpretation | None:
    """Interpret Arterial Blood Gas (ABG) & calculate Serum Anion Gap."""
    if ph is None or pco2 is None or hco3 is None:
        return None

    disorder = "Normal Acid-Base Balance"
    if ph < 7.35:
        if pco2 > 45:
            disorder = "Respiratory Acidosis"
        elif hco3 < 22:
            disorder = "Metabolic Acidosis"
        else:
            disorder = "Mixed Acidosis"
    elif ph > 7.45:
        if pco2 < 35:
            disorder = "Respiratory Alkalosis"
        elif hco3 > 26:
            disorder = "Metabolic Alkalosis"
        else:
            disorder = "Mixed Alkalosis"

    anion_gap = None
    if na is not None and cl is not None:
        anion_gap = round(na - (cl + hco3), 1)
        if "Metabolic Acidosis" in disorder and anion_gap > 12:
            disorder += f" (High Anion Gap = {anion_gap} mEq/L)"

    return ABGInterpretation(disorder=disorder, anion_gap=anion_gap)


def check_lab_thresholds(lab_text: str) -> tuple[bool, list[str], list[LabValue]]:
    """Parse laboratory metrics and evaluate numeric panic limits deterministically."""
    panic_alerts: list[str] = []
    parsed_values: list[LabValue] = []
    has_panic = False

    text_lower = lab_text.lower()

    patterns = [
        ("potassium", r"(?:potassium|k\+?)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("sodium", r"(?:sodium|na\+?)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("troponin", r"(?:troponin[ -]?[it]?)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("platelets", r"(?:platelets?|plt)\s*[:=]?\s*([0-9,]+)"),
        ("hemoglobin", r"(?:hemoglobin|hb|hgb)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("glucose", r"(?:glucose|blood sugar)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("ph", r"(?:ph)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("lactate", r"(?:lactate|lactic acid)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
        ("calcium", r"(?:calcium|ca\+?)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)"),
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

    # Check for ABG parameters in text
    ph_match = re.search(r"\bph\s*[:=]?\s*([0-9]+\.[0-9]+)", lab_text, re.I)
    pco2_match = re.search(r"\bpco2\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)", lab_text, re.I)
    hco3_match = re.search(r"\bhco3|bicarb\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)", lab_text, re.I)
    na_match = re.search(r"\bna\+?|sodium\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)", lab_text, re.I)
    cl_match = re.search(r"\bcl-?|chloride\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)", lab_text, re.I)

    abg = None
    if ph_match and pco2_match and hco3_match:
        try:
            ph = float(ph_match.group(1))
            pco2 = float(pco2_match.group(1))
            hco3 = float(hco3_match.group(1))
            na = float(na_match.group(1)) if na_match else None
            cl = float(cl_match.group(1)) if cl_match else None
            abg = calculate_abg(ph, pco2, hco3, na, cl)
        except ValueError:
            abg = None

    prompt = f"""Clinical Laboratory Panel Interpretation:

Patient Clinical Context: {patient_context or 'Not specified'}
Laboratory Report Data:
{lab_text}

Panic Alert Triggered: {'YES' if has_panic else 'NO'}
Identified Panic Alerts:
{chr(10).join(panic_alerts) if panic_alerts else 'None'}
ABG Interpretation: {abg.disorder if abg else 'N/A'}

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
        abg_analysis=abg,
        summary=summary,
    )

