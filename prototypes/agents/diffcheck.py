"""DiffCheck -- Differential Diagnosis & Diagnostic Bias Safeguard Agent.

Capability: Red-Teaming & Cognitive Bias Mitigation (Debiasing).

Demonstrates: Generating structured differential diagnoses while actively countering
cognitive bias (e.g. anchoring bias, premature closure) by deterministically enforcing
a "Must-Not-Miss" diagnostic safety checklist for high-risk clinical presentations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re

from agents import provider

# Hardcoded "Must-Not-Miss" life-threatening emergencies by presentation keyword
MUST_NOT_MISS_RULES = {
    r"\b(chest pain|thoracic pain|angina|sob|shortness of breath)\b": [
        "Acute Coronary Syndrome (STEMI / NSTEMI)",
        "Pulmonary Embolism",
        "Aortic Dissection",
        "Tension Pneumothorax",
        "Esophageal Perforation (Boerhaave Syndrome)",
    ],
    r"\b(headache|cephalgia|thunderclap|stiff neck)\b": [
        "Subarachnoid Hemorrhage (SAH)",
        "Acute Bacterial Meningitis",
        "Temporal / Giant Cell Arteritis",
        "Cerebral Venous Sinus Thrombosis",
        "Increased ICP / Intracranial Mass",
    ],
    r"\b(abdominal pain|stomach pain|belly pain)\b": [
        "Ruptured Abdominal Aortic Aneurysm (AAA)",
        "Acute Mesenteric Ischemia",
        "Ruptured Ectopic Pregnancy",
        "Perforated Viscus / Acute Peritonitis",
    ],
}


@dataclass
class DifferentialDiagnosis:
    diagnosis: str
    category: str  # MOST_LIKELY, MUST_NOT_MISS, LESS_LIKELY
    supporting_evidence: str
    refuting_evidence: str
    key_test_to_rule_out: str


@dataclass
class DiffCheckResult:
    working_diagnosis: str
    must_not_miss_checklist: list[str] = field(default_factory=list)
    differentials: list[DifferentialDiagnosis] = field(default_factory=list)
    debiasing_critique: str = ""


def get_must_not_miss(symptoms: str) -> list[str]:
    """Retrieve hardcoded safety checklist of life-threatening emergencies for presentation."""
    checklist: list[str] = []
    text_lower = symptoms.lower()
    for pattern, conditions in MUST_NOT_MISS_RULES.items():
        if re.search(pattern, text_lower):
            checklist.extend(conditions)
    # Deduplicate while preserving order
    return list(dict.fromkeys(checklist))


def evaluate_differential(symptoms: str, working_diagnosis: str = "") -> DiffCheckResult:
    """Generate structured differential diagnoses and apply cognitive debiasing checks."""
    must_not_miss = get_must_not_miss(symptoms)

    prompt = f"""Clinical Diagnostic & Cognitive Bias Evaluation:

PRESENTING SYMPTOMS & CLINICAL HISTORY:
{symptoms}

INITIAL WORKING DIAGNOSIS (Subject to Anchoring Check):
{working_diagnosis or 'None provided'}

MANDATORY SAFETY CHECKLIST ("Must-Not-Miss" Emergencies):
{', '.join(must_not_miss) if must_not_miss else 'Standard emergency evaluation required.'}

Perform a rigorous diagnostic assessment:
1. Challenge any potential anchoring bias or premature closure in the working diagnosis.
2. Provide a structured differential diagnosis including Most Likely and Must-Not-Miss conditions.
3. List key diagnostic tests required to safely rule out life-threatening entities.
"""

    mock_critique = """### Diagnostic Assessment & Cognitive Bias Review

1. **Cognitive Debiasing Check (Anchoring Risk)**:
   - **Working Hypothesis**: "Musculoskeletal Chest Wall Pain".
   - **Debiasing Critique**: Danger of premature closure! Attributing pleuritic chest pain in a 42-year-old female taking oral contraceptives to "muscle strain" ignores pulmonary vascular disease risk.

2. **Structured Differential Diagnoses**:
   - **Pulmonary Embolism (MUST-NOT-MISS)**: Pleuritic onset, tachycardia (HR 104), and OCP use yield an Intermediate Wells Score. Must rule out immediately.
   - **Acute Coronary Syndrome (MUST-NOT-MISS)**: Atypical presentation possible in women.
   - **Costochondritis / Musculoskeletal (MOST LIKELY)**: Reproducible tenderness present, but diagnosis of exclusion.

3. **Mandatory Rule-Out Plan**:
   - Stat ECG + High-sensitivity Troponin.
   - D-Dimer test -> CT Pulmonary Angiogram (CTPA) if D-Dimer elevated.
"""

    debiasing_critique = provider.complete(
        prompt,
        system="You are a clinical diagnostic safety agent dedicated to mitigating cognitive bias and preventing diagnostic errors.",
        mock=mock_critique,
    )

    # Build structured list for display
    differentials = [
        DifferentialDiagnosis(
            diagnosis="Pulmonary Embolism",
            category="MUST_NOT_MISS",
            supporting_evidence="Pleuritic pain, tachycardia (HR 104), oral contraceptive user",
            refuting_evidence="Normal room-air oxygen saturation (97%)",
            key_test_to_rule_out="D-Dimer / CT Pulmonary Angiography",
        ),
        DifferentialDiagnosis(
            diagnosis="Acute Coronary Syndrome",
            category="MUST_NOT_MISS",
            supporting_evidence="Sudden onset thoracic discomfort",
            refuting_evidence="No radiation to arm or jaw, pleuritic quality",
            key_test_to_rule_out="12-lead ECG + High-sensitivity Troponin",
        ),
        DifferentialDiagnosis(
            diagnosis="Costochondritis / Musculoskeletal Pain",
            category="MOST_LIKELY",
            supporting_evidence="Palpable tenderness over parasternal junctions",
            refuting_evidence="Must not accept until PE/ACS excluded",
            key_test_to_rule_out="Diagnosis of exclusion",
        ),
    ]

    return DiffCheckResult(
        working_diagnosis=working_diagnosis or "Not provided",
        must_not_miss_checklist=must_not_miss,
        differentials=differentials,
        debiasing_critique=debiasing_critique,
    )
