"""Headless smoke test for all four agents in offline mode.

No Streamlit, no network, no API key required.
Run before the session:  python test_agents.py
"""

import os

os.environ["MOCK_MODE"] = "1"

from agents import diffcheck, discharge, guidebot, labalert, multimodal, pharmguard, screenmate, triage, trialmatch  # noqa: E402
import samples  # noqa: E402

failures: list[str] = []



def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"{'PASS' if condition else 'FAIL'}  {name}{'  -- ' + detail if detail else ''}")
    if not condition:
        failures.append(name)


print("=== 1. GuideBot (grounding) ===")
answered = guidebot.ask("What is the treatment regimen for drug-sensitive TB?")
check("answers an in-scope question", not answered.refused, f"cite {answered.sources[0].section_id}")
check("returns citations", len(answered.sources) > 0, f"{len(answered.sources)} sources")
check("answer mentions the regimen", "isoniazid" in answered.answer.lower())

refused = guidebot.ask(samples.GUIDE_QUESTIONS[-1])
check("refuses an out-of-scope question", refused.refused, f"score {refused.top_score:.2f}")
check("refusal cites nothing", not refused.sources)


print("\n=== 2. DischargeDraft (structured generation) ===")
clean = discharge.draft(samples.WARD_NOTES)
check("all 8 sections present", not clean.missing_sections,
      f"missing: {clean.missing_sections or 'none'}")
check("clean notes raise no identifier warning", not clean.identifier_warnings)

dirty = discharge.draft(samples.WARD_NOTES_WITH_IDENTIFIERS)
check("identifiers are detected", len(dirty.identifier_warnings) >= 4,
      f"{len(dirty.identifier_warnings)} warnings")
for warning in dirty.identifier_warnings:
    print(f"        - {warning}")


print("\n=== 3. TriageAssist (agentic loop) ===")
chest = triage.TriageState(complaint="45 year old man, chest pain since 2 hours, sweating")
chest_step = triage.step(chest)
check("chest pain escalates immediately", chest_step.escalate and chest_step.done,
      "; ".join(chest_step.reasons))

stroke = triage.step(triage.TriageState(complaint="sudden slurred speech and facial droop"))
check("stroke signs escalate", stroke.escalate, "; ".join(stroke.reasons))

benign = triage.TriageState(complaint="mild ankle sprain after a fall yesterday")
first = triage.step(benign)
check("benign case asks a question instead", not first.done and bool(first.question),
      first.question)

# Regression: the agent must not react to red-flag words in its OWN questions.
state = triage.TriageState(complaint="mild ankle sprain after a fall yesterday")
turns = 0
while turns < 10:
    result = triage.step(state)
    if result.done:
        break
    state.answers.append((result.question, "no"))
    turns += 1
check("uses its full question budget on a benign case", turns == triage.MAX_QUESTIONS,
      f"asked {turns} of {triage.MAX_QUESTIONS}")
check("benign case does NOT escalate", result.done and not result.escalate,
      "; ".join(result.reasons) or "no escalation")

# Regression: an explicit denial must not trip the flag.
denied = triage.TriageState(complaint="fever for 3 days, no chest pain, denies bleeding")
check("explicit denials are not treated as red flags", not triage.step(denied).escalate,
      "; ".join(triage.step(denied).reasons) or "correctly ignored")

# ...but a genuine finding in an ANSWER still must.
late = triage.TriageState(complaint="fever for 3 days")
late.answers.append(("Any other symptoms?", "yes, she has become drowsy since morning"))
check("red flag appearing in a later answer still escalates", triage.step(late).escalate,
      "; ".join(triage.step(late).reasons))


print("\n=== 4. ScreenMate (scale) ===")
abstracts = screenmate.parse_abstracts(samples.SCREEN_ABSTRACTS)
check("abstracts parsed with their IDs", len(abstracts) == 6,
      f"{len(abstracts)} parsed: {[a.id for a in abstracts]}")

screened = screenmate.screen(abstracts, samples.SCREEN_CRITERIA)
check("no parse error", not screened.parse_error, screened.parse_error)
check("every abstract gets a verdict", len(screened.verdicts) == len(abstracts),
      str(screened.counts))
check("all verdicts are valid values",
      all(v.verdict in screenmate.VERDICTS for v in screened.verdicts))
check("abstracts the model skipped are surfaced as UNCLEAR",
      any(v.id == "A6" for v in screened.verdicts), "A6 was not in the mock output")


print("\n=== 5. PharmGuard (safety overrides) ===")
p_res = pharmguard.analyze_prescriptions(
    samples.PHARM_MEDICATIONS, samples.PHARM_ALLERGIES, samples.PHARM_EGFR, samples.PHARM_DIAGNOSIS
)
check("detects high-risk drug interaction & contraindication", p_res.has_contraindication,
      f"alerts: {p_res.alerts}")
check("alerts include Warfarin + NSAID warning", any("Warfarin" in a for a in p_res.alerts))
check("alerts include Metformin renal warning", any("Metformin" in a for a in p_res.alerts))
check("alerts include Penicillin allergy warning", any("Penicillin" in a for a in p_res.alerts))


print("\n=== 6. LabAlert (panic values) ===")
l_res = labalert.analyze_labs(samples.LAB_PANEL_CRITICAL)
check("detects critical panic value", l_res.has_panic, f"panic alerts: {l_res.panic_alerts}")
check("identifies potassium panic elevation", any("Potassium" in a for a in l_res.panic_alerts))
check("parses numeric lab values", len(l_res.lab_values) >= 5, f"{len(l_res.lab_values)} values parsed")


print("\n=== 7. TrialMatch (criteria matrix) ===")
t_res = trialmatch.screen_trial(samples.TRIAL_PATIENT_PROFILE, samples.TRIAL_CRITERIA)
check("evaluates trial eligibility verdict", t_res.verdict == "INELIGIBLE", f"verdict: {t_res.verdict}")
check("no json parse error", not t_res.parse_error, t_res.parse_error)
check("generates criteria match matrix", len(t_res.criteria_matches) >= 3,
      f"{len(t_res.criteria_matches)} criteria matched")


print("\n=== 8. DiffCheck (debiasing) ===")
d_res = diffcheck.evaluate_differential(samples.DIFF_SYMPTOMS, samples.DIFF_WORKING_DIAGNOSIS)
check("retrieves must-not-miss emergency checklist", len(d_res.must_not_miss_checklist) >= 3,
      f"checklist: {d_res.must_not_miss_checklist}")
check("includes Pulmonary Embolism emergency", any("Pulmonary Embolism" in item for item in d_res.must_not_miss_checklist))
check("generates structured differential diagnosis matrix", len(d_res.differentials) >= 2,
      f"{len(d_res.differentials)} differentials")


print("\n=== 9. RadVision (multimodal clinical vision) ===")
import base64
img_bytes = base64.b64decode(samples.TINY_PNG_B64)

# Normal image analysis test
m_res = multimodal.analyze_clinical_image(
    image_bytes=img_bytes,
    file_name="cxr_pneumonia.png",
    clinical_context="Right lower lobe consolidation on CXR",
    modality="Chest X-Ray",
)
check("image quality validation passes", m_res.quality_check.is_valid, f"issues: {m_res.quality_check.issues}")
check("generates clinical vision report", len(m_res.report) > 50, f"report length: {len(m_res.report)}")

# Red-flag trigger check
stemi_res = multimodal.analyze_clinical_image(
    image_bytes=img_bytes,
    file_name="ecg_acute_stemi.png",
    clinical_context="Patient with severe chest pain and acute ST elevation on ECG",
    modality="ECG",
)
check("detects critical red-flag alert (STEMI)", stemi_res.has_critical_red_flag, f"red flags: {stemi_res.red_flags}")

# Corrupted image payload rejection check
bad_res = multimodal.analyze_clinical_image(
    image_bytes=b"short",
    file_name="bad.png",
    clinical_context="test",
)
check("rejects corrupted/short image payloads", not bad_res.quality_check.is_valid, "correctly flagged invalid")


print(f"\n{'=' * 46}")
print("ALL PASS" if not failures else f"{len(failures)} FAILURE(S): {failures}")
raise SystemExit(1 if failures else 0)

