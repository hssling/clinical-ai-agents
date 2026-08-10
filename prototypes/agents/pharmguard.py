"""PharmGuard -- Drug Interaction & Dosing Guardrail Agent.

Capability: Deterministic Safety Overrides & Drug Safety Guardrails.

Demonstrates: Local safety rules run *before* calling the LLM. If a severe
drug-drug interaction, organ contraindication, or allergy alert is detected
deterministically, safety warnings are prepended and take precedence over model prose.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re

from agents import provider

# Deterministic safety rules table
INTERACTION_RULES = [
    {
        "drugs": [r"\bwarfarin\b", r"\b(ibuprofen|naproxen|aspirin|diclofenac|indomethacin|ketorolac|meloxicam)\b"],
        "severity": "CONTRAINDICATION",
        "message": "High risk of severe gastrointestinal hemorrhage and major bleeding with co-administration of Warfarin and NSAID.",
    },
    {
        "drugs": [r"\b(enalapril|ramipril|lisinopril|perindopril|captopril|losartan|telmisartan|valsartan)\b",
                  r"\b(spironolactone|eplerenone|amiloride|triamterene)\b"],
        "severity": "WARNING",
        "message": "Risk of severe hyperkalemia when combining ACE-I / ARB with Potassium-Sparing Diuretics. Monitor K+ closely.",
    },
    {
        "drugs": [r"\bsildenafil|tadalafil|vardenafil\b", r"\bnitroglycerin|isosorbide|nitrate\b"],
        "severity": "CONTRAINDICATION",
        "message": "Life-threatening hypotension risk with PDE-5 inhibitors combined with Nitrates.",
    },
    {
        "drugs": [r"\b(fluoxetine|sertraline|paroxetine|citalopram|escitalopram)\b", r"\b(phenelzine|tranylcypromine|selegiline|moclobemide)\b"],
        "severity": "CONTRAINDICATION",
        "message": "Risk of severe, potentially fatal Serotonin Syndrome with SSRI + MAOI co-prescription.",
    },
]

ALLERGY_RULES = [
    {
        "allergy": r"\bpenicillin|beta-lactam\b",
        "drug": r"\b(amoxicillin|ampicillin|piperacillin|augmentin|amoxiclav)\b",
        "severity": "ALLERGY CONTRAINDICATION",
        "message": "Patient has documented Penicillin allergy; prescribe alternative non-beta-lactam antibiotic.",
    },
    {
        "allergy": r"\bsulfa|sulfonamide\b",
        "drug": r"\b(co-trimoxazole|trimethoprim-sulfamethoxazole|bactrim|septra|sulfasalazine)\b",
        "severity": "ALLERGY CONTRAINDICATION",
        "message": "Patient has documented Sulfa allergy; risk of severe cutaneous reaction / anaphylaxis.",
    },
]


@dataclass
class PharmGuardResult:
    has_contraindication: bool
    alerts: list[str] = field(default_factory=list)
    analysis: str = ""


def check_deterministic_safety(
    medications: list[str],
    allergies: list[str] | None = None,
    egfr: float | None = None,
) -> tuple[bool, list[str]]:
    """Scan prescriptions against hardcoded safety tables locally before any LLM call."""
    alerts: list[str] = []
    has_contraindication = False
    med_text = " ".join(medications).lower()
    allergy_text = " ".join(allergies or []).lower()

    # 1. Drug-Drug Interactions
    for rule in INTERACTION_RULES:
        patterns = rule["drugs"]
        if all(re.search(pat, med_text) for pat in patterns):
            severity = rule["severity"]
            alerts.append(f"[{severity}] {rule['message']}")
            if "CONTRAINDICATION" in severity:
                has_contraindication = True

    # 2. Allergy Checks
    for a_rule in ALLERGY_RULES:
        if re.search(a_rule["allergy"], allergy_text) and re.search(a_rule["drug"], med_text):
            severity = a_rule["severity"]
            alerts.append(f"[{severity}] {a_rule['message']}")
            has_contraindication = True

    # 3. Renal Dosing Safeguard
    if egfr is not None:
        if egfr < 30 and re.search(r"\bmetformin\b", med_text):
            alerts.append(
                "[RENAL CONTRAINDICATION] Metformin contraindicated when eGFR < 30 mL/min/1.73m² (Risk of Lactic Acidosis)."
            )
            has_contraindication = True
        elif egfr < 30 and re.search(r"\b(gentamicin|amikacin|vancomycin)\b", med_text):
            alerts.append(
                "[RENAL DOSING WARNING] Severe renal impairment (eGFR < 30). Mandatory dose reduction and serum therapeutic drug monitoring required."
            )

    return has_contraindication, alerts


def analyze_prescriptions(
    medications: list[str],
    allergies: list[str] | None = None,
    egfr: float | None = None,
    diagnosis: str = "",
) -> PharmGuardResult:
    """Evaluate medication safety using local rules combined with LLM analysis."""
    has_contraindication, alerts = check_deterministic_safety(medications, allergies, egfr)

    prompt = f"""Clinical Medication Safety Evaluation:

Medications: {', '.join(medications)}
Allergies: {', '.join(allergies) if allergies else 'None documented'}
Renal Function (eGFR): {f'{egfr} mL/min/1.73m²' if egfr is not None else 'Not provided'}
Indication / Diagnosis: {diagnosis or 'Not provided'}

Deterministic Local Guardrail Findings:
{chr(10).join(alerts) if alerts else 'No deterministic high-risk contraindications triggered.'}

Provide a concise clinical pharmacotherapy safety review covering:
1. Interaction Analysis
2. Dosing & Renal adjustment recommendations
3. Monitoring parameters
"""

    mock_analysis = """### Clinical Pharmacotherapy Safety Summary

1. **Safety Alert Evaluation**:
   - **Warfarin + Ibuprofen**: Co-prescription raises major gastrointestinal bleeding risk by 3–4x. NSAID should be discontinued immediately. Substitute topical analgesics or Paracetamol if pain control is required.
   - **Renal Dosing**: eGFR 28 mL/min indicates Stage 4 CKD. Metformin is contraindicated due to risk of severe lactic acidosis. Switch to linagliptin or insulin.

2. **Actionable Recommendations**:
   - Stop Ibuprofen; initiate Paracetamol 500mg PRN.
   - Discontinue Metformin; consult nephrology/endocrinology for insulin titration.
   - Check baseline INR and stool occult blood.
"""

    analysis = provider.complete(
        prompt,
        system="You are a clinical pharmacology safety agent. Provide clear, direct, evidence-based medication safety reviews.",
        mock=mock_analysis,
    )

    return PharmGuardResult(
        has_contraindication=has_contraindication,
        alerts=alerts,
        analysis=analysis,
    )
