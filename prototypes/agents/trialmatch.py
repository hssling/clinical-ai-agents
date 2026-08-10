"""TrialMatch -- Clinical Trial Eligibility Screening Agent.

Capability: Multi-Criteria Protocol Matching & Reasoning Matrix.

Demonstrates: Structured evaluation of complex clinical patient summaries against protocol
inclusion/exclusion criteria. Returns structured verdicts (ELIGIBLE, INELIGIBLE, NEEDS_MORE_DATA)
with criterion-by-criterion breakdown.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re

from agents import provider


@dataclass
class CriterionMatch:
    criterion: str
    status: str  # MET, UNMET, UNKNOWN
    explanation: str


@dataclass
class TrialMatchResult:
    verdict: str  # ELIGIBLE, INELIGIBLE, NEEDS_MORE_DATA
    summary: str
    criteria_matches: list[CriterionMatch] = field(default_factory=list)
    parse_error: str = ""


def screen_trial(patient_profile: str, trial_criteria: str) -> TrialMatchResult:
    """Evaluate patient summary against trial inclusion/exclusion criteria."""
    prompt = f"""Clinical Trial Eligibility Evaluation:

PATIENT CLINICAL PROFILE:
{patient_profile}

TRIAL INCLUSION & EXCLUSION CRITERIA:
{trial_criteria}

Analyze the patient profile against EACH protocol criterion.
Return ONLY a valid JSON object formatted as follows:
{{
  "verdict": "ELIGIBLE" | "INELIGIBLE" | "NEEDS_MORE_DATA",
  "summary": "Concise executive summary of trial eligibility",
  "criteria_matches": [
    {{
      "criterion": "Criterion statement",
      "status": "MET" | "UNMET" | "UNKNOWN",
      "explanation": "Brief rationale referencing patient data"
    }}
  ]
}}
"""

    mock_json = """{
  "verdict": "INELIGIBLE",
  "summary": "Patient meets age, histologically confirmed Type 2 Diabetes, and HbA1c criteria, but is INELIGIBLE due to severe renal impairment (eGFR 24 < 30 mL/min threshold in Exclusion Criteria).",
  "criteria_matches": [
    {
      "criterion": "Adults aged 18 to 75 years",
      "status": "MET",
      "explanation": "Patient is 58 years old."
    },
    {
      "criterion": "Diagnosed with Type 2 Diabetes Mellitus with HbA1c 7.5% - 10.5%",
      "status": "MET",
      "explanation": "HbA1c is 8.6%."
    },
    {
      "criterion": "Exclusion: eGFR < 30 mL/min/1.73m2 or end-stage renal disease",
      "status": "UNMET",
      "explanation": "Patient's eGFR is 24 mL/min/1.73m2, violating exclusion threshold."
    },
    {
      "criterion": "Exclusion: Active acute coronary syndrome within past 6 months",
      "status": "MET",
      "explanation": "No history of cardiac events reported."
    }
  ]
}"""

    raw_response = provider.complete(
        prompt,
        system="You are a clinical trials eligibility screening agent. You output ONLY valid JSON.",
        mock=mock_json,
    )

    # Clean JSON output
    cleaned = raw_response.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(cleaned)
        verdict = data.get("verdict", "NEEDS_MORE_DATA").upper()
        if verdict not in {"ELIGIBLE", "INELIGIBLE", "NEEDS_MORE_DATA"}:
            verdict = "NEEDS_MORE_DATA"

        matches = [
            CriterionMatch(
                criterion=item.get("criterion", ""),
                status=item.get("status", "UNKNOWN").upper(),
                explanation=item.get("explanation", ""),
            )
            for item in data.get("criteria_matches", [])
        ]

        return TrialMatchResult(
            verdict=verdict,
            summary=data.get("summary", "Eligibility evaluation complete."),
            criteria_matches=matches,
        )
    except Exception as exc:  # noqa: BLE001
        return TrialMatchResult(
            verdict="NEEDS_MORE_DATA",
            summary=raw_response,
            parse_error=f"JSON parsing error: {exc}",
        )
