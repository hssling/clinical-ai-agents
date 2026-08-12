"""Build Your Own Clinical AI Agent -- four working prototypes.

CME: Artificial Intelligence in Healthcare, SIMS&RH Tumkur, 12 Aug 2026.

Run locally:   streamlit run app.py
Offline mode:  set MOCK_MODE=1  (no internet, no API key, full demo)

One app, four pages, one URL. Four browser tabs is not a risk worth taking on stage.
"""

from __future__ import annotations

import os

import streamlit as st


def _bridge_secrets() -> None:
    """Copy Streamlit secrets into the environment.

    Streamlit Cloud supplies configuration through st.secrets, but the agents
    are plain Python and read os.environ so they can also be used from scripts
    and tests. This bridges the two, and must run BEFORE the agents are
    imported -- provider.py decides mock-vs-live from the environment at import
    time. Existing environment variables win, so a local shell export still
    overrides a deployed secret.
    """
    try:
        secrets = st.secrets
    except Exception:  # noqa: BLE001 - no secrets file locally is normal
        return
    for key in ("GOOGLE_API_KEY", "MOCK_MODE", "AGENT_MODEL"):
        try:
            value = secrets[key]
        except Exception:  # noqa: BLE001 - key simply absent
            continue
        if value and not os.environ.get(key):
            os.environ[key] = str(value)


_bridge_secrets()

import samples  # noqa: E402 - must follow the secrets bridge
from agents import (  # noqa: E402
    chartvision,
    diffcheck,
    discharge,
    ecgvision,
    fundusvision,
    guidebot,
    labalert,
    multimodal,
    otoscope,
    pathoscan,
    pharmguard,
    provider,
    screenmate,
    triage,
    trialmatch,
    woundtrack,
)
from agents.retrieval import load_sections  # noqa: E402

st.set_page_config(page_title="Clinical AI Agents — Live Demo", page_icon="🩺", layout="wide")

# Projector styling: an auditorium back row cannot read Streamlit's defaults.
st.markdown("""
<style>
  html, body, [class*="css"] { font-size: 18px; }
  .main .block-container { padding-top: 2rem; max-width: 1150px; }
  h1 { font-size: 2.4rem !important; }
  h2 { font-size: 1.7rem !important; }
  .stButton button { font-size: 1.05rem; padding: 0.5rem 1rem; }
  .banner { padding: 0.85rem 1.1rem; border-radius: 8px; font-weight: 600;
            margin-bottom: 1rem; border-left: 6px solid; }
  .danger  { background:#fdecea; color:#7f1d1d; border-color:#dc2626; }
  .warn    { background:#fff7e6; color:#7c4a03; border-color:#f59e0b; }
  .ok      { background:#eaf7ee; color:#14532d; border-color:#16a34a; }
  .cite    { background:#f1f5f9; border-left:4px solid #64748b; padding:0.6rem 0.9rem;
             margin:0.4rem 0; border-radius:6px; font-size:0.95rem; }
</style>
""", unsafe_allow_html=True)


def banner(kind: str, text: str) -> None:
    st.markdown(f'<div class="banner {kind}">{text}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- sidebar
PAGES = {
    "1 · GuideBot — grounding": "guide",
    "2 · DischargeDraft — structure": "discharge",
    "3 · TriageAssist — the loop": "triage",
    "4 · ScreenMate — scale": "screen",
    "5 · PharmGuard — safety overrides": "pharm",
    "6 · LabAlert — panic values": "lab",
    "7 · TrialMatch — criteria matrix": "trial",
    "8 · DiffCheck — debiasing": "diff",
    "9 · RadVision — multimodal vision": "vision",
    "10 · PathoScan — digital pathology": "pathology",
    "11 · WoundTrack — wound staging": "wound",
    "12 · ChartVision — prescription OCR": "chart",
    "13 · FundusVision — retinal screening": "fundus",
    "14 · OtoscopeAI — ENT diagnostic vision": "otoscope",
    "15 · ECGVision — cardiac ECG diagnostics": "ecg",
}



with st.sidebar:
    st.title("🩺 Clinical AI Agents")
    st.caption("CME · SIMS&RH Tumkur · 12 Aug 2026")
    choice = st.radio("Prototype", list(PAGES), label_visibility="collapsed")
    page = PAGES[choice]

    st.divider()
    mock = provider.is_mock_mode()
    st.metric("Mode", "OFFLINE" if mock else "LIVE")
    st.caption(provider.mode_label())
    if mock:
        st.info("Running on pre-written responses. No internet or API key needed.")
    st.caption(f"{len(load_sections())} guideline sections loaded")

    st.divider()
    st.caption("Educational prototypes. Not medical devices. "
               "No real patient data has been used.")


# ---------------------------------------------------------------- 1. GuideBot
if page == "guide":
    st.title("GuideBot")
    st.caption("**Capability: grounding.** Answers only from the loaded guidelines, "
               "cites the section, and refuses when the answer is not there.")

    if "guide_q" not in st.session_state:
        st.session_state.guide_q = samples.GUIDE_QUESTIONS[0]

    st.write("**Try one:**")
    cols = st.columns(len(samples.GUIDE_QUESTIONS))
    for col, question in zip(cols, samples.GUIDE_QUESTIONS):
        label = "❌ Out of scope" if question == samples.GUIDE_QUESTIONS[-1] else question[:26] + "…"
        if col.button(label, key=f"gq_{question[:18]}", use_container_width=True):
            st.session_state.guide_q = question

    question = st.text_input("Clinical question", key="guide_q")

    if st.button("Ask GuideBot", type="primary") or question:
        result = guidebot.ask(question)

        if result.refused:
            banner("danger", "🛑 REFUSED — the agent declined rather than guessed")
            st.markdown(result.answer)
        else:
            banner("ok", f"✅ Answered from the guidelines · relevance {result.top_score:.0%}")
            st.markdown(result.answer)

        if result.sources:
            st.subheader("Sources it used")
            for source in result.sources:
                st.markdown(f'<div class="cite"><b>{source.citation}</b><br>{source.text}</div>',
                            unsafe_allow_html=True)

        with st.expander("What just happened?"):
            st.markdown(f"""
1. Your question was matched against **{len(load_sections())} guideline sections** locally.
2. Best relevance score: **{result.top_score:.2f}** · refusal threshold: **{guidebot.GROUNDING_THRESHOLD}**.
3. {"Below threshold, so the agent refused **before ever calling the model**."
   if result.refused else
   "Above threshold, so the matched sections were passed to the model as its only source."}

The guardrail is plain Python, not a request to the model to behave. That is why
it costs nothing, cannot be argued with, and works with the wifi unplugged.
""")


# ---------------------------------------------------------------- 2. DischargeDraft
elif page == "discharge":
    st.title("DischargeDraft")
    st.caption("**Capability: structured generation & PHI auto-redaction.** Messy ward notes in, "
               "a fixed-schema discharge summary out with local PHI auto-scrubbing and ICD-10 coding suggestions.")

    if "notes" not in st.session_state:
        st.session_state.notes = samples.WARD_NOTES

    col_a, col_b = st.columns(2)
    if col_a.button("📋 Load sample ward notes", use_container_width=True):
        st.session_state.notes = samples.WARD_NOTES
    if col_b.button("⚠️ Load notes containing identifiers", use_container_width=True):
        st.session_state.notes = samples.WARD_NOTES_WITH_IDENTIFIERS

    notes = st.text_area("Ward notes", key="notes", height=240)

    live_warnings = discharge.find_identifiers(notes)
    if live_warnings:
        banner("warn", "⚠️ Identifier check fired — PHI will be automatically scrubbed locally before model submission")
        for warning in live_warnings:
            st.write(f"- {warning}")

    if st.button("Draft discharge summary", type="primary"):
        result = discharge.draft(notes)

        if result.missing_sections:
            banner("warn", f"Schema check: missing {', '.join(result.missing_sections)}")
        else:
            banner("ok", "✅ Schema check passed — all 8 required sections present")

        if result.identifier_warnings:
            st.info(f"🔒 **PHI Auto-Redaction Active**: {len(result.identifier_warnings)} identifiers scrubbed locally.")
            with st.expander("View Sanitized Notes Sent to Model"):
                st.code(result.redacted_text)

        if result.icd10_suggestions:
            st.write("**Suggested ICD-10 Diagnostic Codes:**")
            st.table(result.icd10_suggestions)

        st.markdown(result.summary)

    with st.expander("What just happened?"):
        st.markdown("""
The identifier scan and **auto-redaction engine** run **on this machine, before anything is sent anywhere**.
That ordering is the whole point: a privacy check that runs after the network
call has already protected nothing.

The eight headings are then verified in the output by the application, and ICD-10 codes are suggested automatically.
""")


# ---------------------------------------------------------------- 3. TriageAssist
elif page == "triage":
    st.title("TriageAssist")
    banner("danger", "⚠️ EDUCATIONAL DEMONSTRATION — NOT FOR CLINICAL USE")
    st.caption("**Capability: the agentic loop & ESI score.** It decides whether it has enough "
               "information, asks a follow-up if not, and calculates standardized ESI/HEART/qSOFA risk ratings.")

    if "tstate" not in st.session_state:
        st.session_state.tstate = None
        st.session_state.tstep = None

    st.write("**Start a case:**")
    cols = st.columns(2)
    for i, complaint in enumerate(samples.TRIAGE_COMPLAINTS):
        if cols[i % 2].button(complaint, key=f"tc_{i}", use_container_width=True):
            st.session_state.tstate = triage.TriageState(complaint=complaint)
            st.session_state.tstep = triage.step(st.session_state.tstate)

    typed = st.text_input("…or type a presenting complaint")
    if st.button("Start triage", type="primary") and typed.strip():
        st.session_state.tstate = triage.TriageState(complaint=typed.strip())
        st.session_state.tstep = triage.step(st.session_state.tstate)

    state, current = st.session_state.tstate, st.session_state.tstep

    if state:
        st.divider()
        st.markdown(f"**Presenting complaint:** {state.complaint}")
        for q, a in state.answers:
            st.markdown(f"- **{q}** → _{a}_")

        if current and not current.done:
            st.markdown(f"### ❓ {current.question}")
            st.caption(f"Question {len(state.answers) + 1} of a maximum {triage.MAX_QUESTIONS}")
            answer = st.text_input("Answer", key=f"ans_{len(state.answers)}")
            if st.button("Submit answer") and answer.strip():
                state.answers.append((current.question, answer.strip()))
                st.session_state.tstep = triage.step(state)
                st.rerun()

        elif current and current.done:
            c1, c2, c3 = st.columns(3)
            c1.metric("ESI Triage Rating", f"Level {current.esi_level}", f"{'Immediate/Emergent' if current.esi_level <= 2 else 'Urgent/Routine'}")
            if current.heart_score is not None:
                c2.metric("HEART Score", f"{current.heart_score} / 10", "Chest Pain Risk")
            if current.qsofa_score is not None:
                c3.metric("qSOFA Score", f"{current.qsofa_score} / 3", "Sepsis Risk")

            if current.escalate:
                banner("danger", "🚨 ESCALATE NOW")
                st.markdown("**Red flags identified:**")
                for reason in current.reasons:
                    st.markdown(f"- {reason}")
                st.markdown("**Action:**")
                for action in current.actions:
                    st.markdown(f"- {action}")
            else:
                banner("ok", "✅ No red flags in the information given")
            st.info(current.summary)

    with st.expander("What just happened?"):
        st.markdown(f"""
This agent **loops**. Every turn it re-reads the whole conversation and chooses
one of three moves: escalate, ask one more question, or stop. ESI, HEART, and qSOFA scores are computed deterministically.
""")


# ---------------------------------------------------------------- 4. ScreenMate
elif page == "screen":
    st.title("ScreenMate")
    st.caption("**Capability: tool use at scale.** The same judgement applied across "
               "many records, returning machine-readable output — not chat.")

    col_a, col_b = st.columns(2)
    criteria = col_a.text_area("Inclusion / exclusion criteria",
                               value=samples.SCREEN_CRITERIA, height=280)
    blob = col_b.text_area("Abstracts (blank line between each)",
                           value=samples.SCREEN_ABSTRACTS, height=280)

    if st.button("Screen all abstracts", type="primary"):
        abstracts = screenmate.parse_abstracts(blob)
        result = screenmate.screen(abstracts, criteria)

        if result.parse_error:
            banner("warn", f"⚠️ {result.parse_error}")
        else:
            counts = result.counts
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Screened", len(result.verdicts))
            c2.metric("Include", counts["INCLUDE"])
            c3.metric("Exclude", counts["EXCLUDE"])
            c4.metric("Unclear", counts["UNCLEAR"])

            icons = {"INCLUDE": "✅", "EXCLUDE": "❌", "UNCLEAR": "❓"}
            st.table([
                {"ID": v.id, "": icons.get(v.verdict, "❓"),
                 "Verdict": v.verdict, "Reason": v.reason}
                for v in result.verdicts
            ])
            banner("warn", "⚠️ UNCLEAR and EXCLUDE rows must still be checked by a human. "
                           "This narrows the pile; it does not replace the screener.")

    with st.expander("What just happened?"):
        st.markdown("""
Output is **JSON, not prose** — so it flows into the next step of a workflow.
""")


# ---------------------------------------------------------------- 5. PharmGuard
elif page == "pharm":
    st.title("PharmGuard")
    st.caption("**Capability: deterministic safety overrides.** Hardcoded medical safety tables "
               "and Cockcroft-Gault CrCl & QTc risk calculators run locally *before* calling the LLM.")

    if st.button("📋 Load high-risk sample prescription", use_container_width=True):
        st.session_state.p_meds = "\n".join(samples.PHARM_MEDICATIONS)
        st.session_state.p_allergies = ", ".join(samples.PHARM_ALLERGIES)
        st.session_state.p_egfr = str(samples.PHARM_EGFR)
        st.session_state.p_dx = samples.PHARM_DIAGNOSIS

    col_a, col_b = st.columns(2)
    p_meds_raw = col_a.text_area("Prescribed Medications (one per line)",
                                 value=st.session_state.get("p_meds", "\n".join(samples.PHARM_MEDICATIONS)),
                                 height=180)
    p_dx = col_b.text_area("Clinical Indication / Diagnosis",
                           value=st.session_state.get("p_dx", samples.PHARM_DIAGNOSIS),
                           height=180)

    c1, c2 = st.columns(2)
    p_allergies_raw = c1.text_input("Documented Allergies (comma-separated)",
                                    value=st.session_state.get("p_allergies", ", ".join(samples.PHARM_ALLERGIES)))
    p_egfr_str = c2.text_input("Renal Function eGFR (mL/min/1.73m²)",
                               value=st.session_state.get("p_egfr", str(samples.PHARM_EGFR)))

    if st.button("Run PharmGuard Safety Scan", type="primary"):
        meds = [m.strip() for m in p_meds_raw.splitlines() if m.strip()]
        allergies = [a.strip() for a in p_allergies_raw.split(",") if a.strip()]
        try:
            egfr_val = float(p_egfr_str) if p_egfr_str.strip() else None
        except ValueError:
            egfr_val = None

        result = pharmguard.analyze_prescriptions(meds, allergies, egfr_val, p_dx)

        if result.crcl:
            st.metric("Cockcroft-Gault CrCl", f"{result.crcl} mL/min", "Renal Clearance")
        if result.qtc_warning:
            banner("danger", "🚨 QTc PROLONGATION & TORSADES DE POINTES RISK DETECTED")

        if result.has_contraindication:
            banner("danger", "🚨 HIGH-RISK CONTRAINDICATION DETECTED — LOCAL GUARDRAIL OVERRIDE")
        elif result.alerts:
            banner("warn", "⚠️ MEDICATION SAFETY WARNINGS IDENTIFIED")
        else:
            banner("ok", "✅ No high-risk deterministic contraindications found")

        if result.alerts:
            st.markdown("**Deterministic Local Safety Flags:**")
            for alert in result.alerts:
                st.markdown(f"- **{alert}**")

        st.divider()
        st.markdown(result.analysis)

    with st.expander("What just happened?"):
        st.markdown("""
The interaction table, CrCl calculation, and QTc risk scanner run **locally in Python before the prompt is constructed**.
""")


# ---------------------------------------------------------------- 6. LabAlert
elif page == "lab":
    st.title("LabAlert")
    st.caption("**Capability: numerical boundary check.** Parses numeric lab metrics locally, calculates ABG acid-base status, and "
               "triggers immediate emergency banners for critical 'Panic Values'.")

    if st.button("📋 Load critical lab panel sample", use_container_width=True):
        st.session_state.lab_text = samples.LAB_PANEL_CRITICAL

    lab_input = st.text_area("Laboratory Panel Report",
                             value=st.session_state.get("lab_text", samples.LAB_PANEL_CRITICAL),
                             height=220)

    if st.button("Analyze Lab Panel", type="primary"):
        result = labalert.analyze_labs(lab_input)

        if result.abg_analysis:
            st.info(f"🧪 **ABG Acid-Base Interpretation**: **{result.abg_analysis.disorder}**" +
                    (f" (Anion Gap: {result.abg_analysis.anion_gap} mEq/L)" if result.abg_analysis.anion_gap else ""))


        if result.has_panic:
            banner("danger", "🚨 CRITICAL LAB PANIC VALUES IDENTIFIED — IMMEDIATE ACTION REQUIRED")
            for alert in result.panic_alerts:
                st.markdown(f"- **{alert}**")
        else:
            banner("ok", "✅ No critical panic values detected")

        if result.lab_values:
            st.write("**Parsed Laboratory Metrics:**")
            st.table([
                {"Test": lv.test_name, "Value": f"{lv.val} {lv.unit}", "Status": lv.status}
                for lv in result.lab_values
            ])

        st.markdown(result.summary)

    with st.expander("What just happened?"):
        st.markdown("""
Numeric regex parsing checks panic limits (e.g. Potassium > 6.0, Troponin > 0.04) **locally in code**.
This guarantees panic value recognition even if the LLM fails to highlight the numeric anomaly.
""")


# ---------------------------------------------------------------- 7. TrialMatch
elif page == "trial":
    st.title("TrialMatch")
    st.caption("**Capability: multi-criteria matrix.** Compares patient profiles against protocol "
               "inclusion/exclusion criteria and outputs structured criteria matrices.")

    col_a, col_b = st.columns(2)
    patient_text = col_a.text_area("Patient Profile", value=samples.TRIAL_PATIENT_PROFILE, height=260)
    criteria_text = col_b.text_area("Protocol Criteria", value=samples.TRIAL_CRITERIA, height=260)

    if st.button("Evaluate Trial Eligibility", type="primary"):
        result = trialmatch.screen_trial(patient_text, criteria_text)

        if result.verdict == "ELIGIBLE":
            banner("ok", "✅ PATIENT IS ELIGIBLE FOR CLINICAL TRIAL RECRUITMENT")
        elif result.verdict == "INELIGIBLE":
            banner("danger", "❌ PATIENT IS INELIGIBLE — CRITERIA UNMET OR EXCLUSION MET")
        else:
            banner("warn", "❓ ELIGIBILITY UNCERTAIN — ADDITIONAL CLINICAL DATA REQUIRED")

        st.markdown(f"**Executive Summary:** {result.summary}")

        if result.criteria_matches:
            st.write("**Criteria Breakdown Matrix:**")
            icons = {"MET": "✅", "UNMET": "❌", "UNKNOWN": "❓"}
            st.table([
                {"Criterion": c.criterion, "": icons.get(c.status, "❓"), "Status": c.status, "Rationale": c.explanation}
                for c in result.criteria_matches
            ])

    with st.expander("What just happened?"):
        st.markdown("""
The output is forced into a **structured multi-attribute matrix (JSON)**.
Instead of an ambiguous paragraph, the agent evaluates each criterion individually,
making protocol audit and human review fast and accountable.
""")


# ---------------------------------------------------------------- 8. DiffCheck
elif page == "diff":
    st.title("DiffCheck")
    st.caption("**Capability: red-teaming & cognitive debiasing.** Generates differential diagnoses while "
               "actively challenging anchoring bias with mandatory 'Must-Not-Miss' safety checklists.")

    if st.button("📋 Load pleuritic chest pain case (anchoring risk)", use_container_width=True):
        st.session_state.diff_symptoms = samples.DIFF_SYMPTOMS
        st.session_state.diff_working = samples.DIFF_WORKING_DIAGNOSIS

    symptoms_in = st.text_area("Presenting Symptoms & History",
                               value=st.session_state.get("diff_symptoms", samples.DIFF_SYMPTOMS),
                               height=160)
    working_in = st.text_input("Initial Working Diagnosis (Subject to Anchoring Check)",
                               value=st.session_state.get("diff_working", samples.DIFF_WORKING_DIAGNOSIS))

    if st.button("Run Diagnostic Safety Check", type="primary"):
        result = diffcheck.evaluate_differential(symptoms_in, working_in)

        if result.must_not_miss_checklist:
            banner("warn", "⚠️ MANDATORY SAFETY CHECKLIST: HIGH-RISK EMERGENCIES TO RULE OUT")
            st.markdown("**Must-Not-Miss Emergencies for this Presentation:**")
            for item in result.must_not_miss_checklist:
                st.markdown(f"- 🔴 **{item}**")

        st.divider()
        st.markdown(result.debiasing_critique)

        if result.differentials:
            st.write("**Differential Diagnosis Matrix:**")
            st.table([
                {"Diagnosis": d.diagnosis, "Category": d.category, "Supporting": d.supporting_evidence, "Key Rule-Out Test": d.key_test_to_rule_out}
                for d in result.differentials
            ])

    with st.expander("What just happened?"):
        st.markdown("""
Cognitive bias (like premature closure and anchoring) is a leading cause of diagnostic error.
DiffCheck acts as a **red-teaming agent**: it injects a deterministic organ-system emergency checklist
and explicitly critiques the initial impression before accepting a benign diagnosis.
""")


# ---------------------------------------------------------------- 9. RadVision
elif page == "vision":
    st.title("RadVision")

    st.caption("**Capability: multimodal clinical vision.** Combines medical imaging (Chest X-Ray, Derm, ECG) "
               "with clinical history, applying deterministic image quality validation and critical red-flag safety triggers.")

    multimodal_samples = getattr(samples, "MULTIMODAL_SAMPLES", getattr(multimodal, "MULTIMODAL_SAMPLES", []))
    tiny_png_b64 = getattr(samples, "TINY_PNG_B64", getattr(multimodal, "TINY_PNG_B64", ""))

    st.write("**Try a sample clinical vision case:**")
    cols = st.columns(len(multimodal_samples))
    for col, sample_case in zip(cols, multimodal_samples):
        if col.button(sample_case["label"], key=f"ms_{sample_case['modality']}", use_container_width=True):
            st.session_state.rad_context = sample_case["context"]
            st.session_state.rad_modality = sample_case["modality"]
            st.session_state.rad_filename = sample_case["file_name"]
            st.session_state.rad_b64 = sample_case["image_b64"]

    default_context = multimodal_samples[0]["context"] if multimodal_samples else "54-year-old male presenting with high fever and cough."
    context_in = st.text_area("Patient Clinical History & Context",
                              value=st.session_state.get("rad_context", default_context),
                              height=120)

    col_m1, col_m2 = st.columns(2)
    modality_in = col_m1.selectbox("Image Modality", ["Chest X-Ray", "Dermatology", "ECG", "Clinical Photo"],
                                   index=0 if "rad_modality" not in st.session_state else
                                   ["Chest X-Ray", "Dermatology", "ECG", "Clinical Photo"].index(st.session_state.rad_modality) if st.session_state.rad_modality in ["Chest X-Ray", "Dermatology", "ECG", "Clinical Photo"] else 0)

    uploaded_file = col_m2.file_uploader("Upload Medical Image (PNG, JPG, WEBP)", type=["png", "jpg", "jpeg", "webp"])

    image_bytes = None
    file_name = st.session_state.get("rad_filename", "cxr_sample.jpg")

    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        file_name = uploaded_file.name
        st.image(image_bytes, caption=f"Uploaded Image: {file_name}", use_column_width=True)
    elif "rad_b64" in st.session_state:
        import base64
        image_bytes = base64.b64decode(st.session_state.rad_b64)
        st.info(f"Loaded sample image metadata: {file_name}")
    else:
        import base64
        image_bytes = base64.b64decode(tiny_png_b64) if tiny_png_b64 else b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="


    if st.button("Run Multimodal Vision Analysis", type="primary"):
        if image_bytes:
            result = multimodal.analyze_clinical_image(
                image_bytes=image_bytes,
                file_name=file_name,
                clinical_context=context_in,
                modality=modality_in,
            )

            if result.has_critical_red_flag:
                banner("danger", "🚨 CRITICAL RED-FLAG SAFETY ALERT TRIGGERED")
                for flag in result.red_flags:
                    st.write(f"- {flag}")

            if result.quality_check.is_valid:
                banner("ok", f"✅ Image Validation Passed · {result.quality_check.mime_type} ({result.quality_check.file_size_kb} KB)")
            else:
                banner("warn", "⚠️ Image Quality / Format Warning")

            st.markdown(result.report)

    with st.expander("What just happened?"):
        st.markdown("""
1. The image payload undergoes **deterministic size & format validation** before reaching the vision model.
2. Clinical context is scanned locally for **life-threatening emergencies** (Pneumothorax, Acute STEMI, Melanoma risk).
3. Image bytes and clinical history are packaged into a **multimodal vision request** sent to the LLM (Gemini 2.0 Flash / GPT-4o / OpenRouter).
4. If running offline (`MOCK_MODE=1`), pre-audited diagnostic vision reports are served instantly without network latency.
""")


# ---------------------------------------------------------------- 10. PathoScan
elif page == "pathology":
    st.title("PathoScan")
    st.caption("**Capability: digital pathology & histology analysis.** Evaluates biopsy photomicrographs, "
               "incorporating deterministic malignancy safety triggers (vascular invasion, high mitotic index) and IHC recommendations.")

    patho_samples = getattr(samples, "PATHOLOGY_SAMPLES", getattr(pathoscan, "PATHOLOGY_SAMPLES", []))
    st.write("**Try a sample histology case:**")
    cols = st.columns(len(patho_samples))
    for col, sample_case in zip(cols, patho_samples):
        if col.button(sample_case["label"], key=f"ps_{sample_case['tissue_type']}", use_container_width=True):
            st.session_state.patho_context = sample_case["context"]
            st.session_state.patho_tissue = sample_case["tissue_type"]

    tissue_in = st.text_input("Specimen / Tissue Type",
                              value=st.session_state.get("patho_tissue", "Breast Tissue Biopsy"))
    context_in = st.text_area("Clinical History & Histological Details",
                              value=st.session_state.get("patho_context", patho_samples[0]["context"] if patho_samples else ""),
                              height=120)

    uploaded_file = st.file_uploader("Upload Biopsy Photomicrograph (PNG, JPG)", type=["png", "jpg", "jpeg"])
    import base64
    image_bytes = uploaded_file.read() if uploaded_file else base64.b64decode(pathoscan.TINY_PNG_B64)

    if st.button("Run Digital Pathology Assessment", type="primary"):
        result = pathoscan.analyze_pathology_slide(
            image_bytes=image_bytes,
            file_name=uploaded_file.name if uploaded_file else "biopsy_sample.jpg",
            clinical_context=context_in,
            tissue_type=tissue_in,
        )

        if result.has_critical_malignancy:
            banner("danger", "🚨 HIGH-GRADE MALIGNANCY RED-FLAG TRIGGERED")
            for alert in result.alerts:
                st.write(f"- {alert}")

        st.markdown(result.report)

    with st.expander("What just happened?"):
        st.markdown("""
Biopsy slides undergo local keyword scanning for aggressive features (lymphovascular invasion, high mitotic rate)
before the vision model outlines nuclear grading and recommends specific immunoperoxidase panels (ER/PR/HER2/Ki-67).
""")


# ---------------------------------------------------------------- 11. WoundTrack
elif page == "wound":
    st.title("WoundTrack")
    st.caption("**Capability: visual wound staging & tissue composition.** Evaluates diabetic foot ulcers & pressure injuries, "
               "calculating tissue composition percentages (granulation vs slough vs eschar) and infection safety risks.")

    wound_samples = getattr(samples, "WOUND_SAMPLES", getattr(woundtrack, "WOUND_SAMPLES", []))
    st.write("**Try a sample wound case:**")
    cols = st.columns(len(wound_samples))
    for col, sample_case in zip(cols, wound_samples):
        if col.button(sample_case["label"], key=f"ws_{sample_case['location']}", use_container_width=True):
            st.session_state.wound_context = sample_case["context"]
            st.session_state.wound_location = sample_case["location"]

    loc_in = st.text_input("Anatomical Wound Location",
                           value=st.session_state.get("wound_location", "Plantar Surface 1st MTP Joint"))
    context_in = st.text_area("Patient History & Clinical Features",
                              value=st.session_state.get("wound_context", wound_samples[0]["context"] if wound_samples else ""),
                              height=120)

    uploaded_file = st.file_uploader("Upload Wound Photograph (PNG, JPG)", type=["png", "jpg", "jpeg"])
    import base64
    image_bytes = uploaded_file.read() if uploaded_file else base64.b64decode(woundtrack.TINY_PNG_B64)

    if st.button("Run Wound Staging & Infection Assessment", type="primary"):
        result = woundtrack.analyze_wound_image(
            image_bytes=image_bytes,
            file_name=uploaded_file.name if uploaded_file else "wound_sample.jpg",
            clinical_context=context_in,
            location=loc_in,
        )

        if result.has_critical_infection:
            banner("danger", "🚨 CRITICAL WOUND INFECTION ALERT TRIGGERED")
            for alert in result.alerts:
                st.write(f"- {alert}")

        st.markdown(result.report)

    with st.expander("What just happened?"):
        st.markdown("""
Exposed bone (probe-to-bone positive) and spreading erythema trigger immediate osteomyelitis/necrotizing infection alerts
prior to generating Wagner/NPUAP staging and tissue breakdown percentages.
""")


# ---------------------------------------------------------------- 12. ChartVision
elif page == "chart":
    st.title("ChartVision")
    st.caption("**Capability: prescription OCR & high-alert drug double-check.** Transcribes handwritten doctor orders, "
               "detecting high-alert medications (Insulin, Heparin, Digoxin) and dosing unit ambiguities.")

    chart_samples = getattr(samples, "CHART_SAMPLES", getattr(chartvision, "CHART_SAMPLES", []))
    st.write("**Try a sample handwritten order case:**")
    cols = st.columns(len(chart_samples))
    for col, sample_case in zip(cols, chart_samples):
        if col.button(sample_case["label"], key=f"cs_{sample_case['document_type']}", use_container_width=True):
            st.session_state.chart_context = sample_case["context"]
            st.session_state.chart_type = sample_case["document_type"]

    type_in = st.selectbox("Document Category", ["Handwritten Prescription", "ICU Flowsheet Note", "Outpatient Consultation Card"],
                           index=0)
    context_in = st.text_area("Order Context / Notes",
                              value=st.session_state.get("chart_context", chart_samples[0]["context"] if chart_samples else ""),
                              height=120)

    uploaded_file = st.file_uploader("Upload Prescription / Chart Image (PNG, JPG)", type=["png", "jpg", "jpeg"])
    import base64
    image_bytes = uploaded_file.read() if uploaded_file else base64.b64decode(chartvision.TINY_PNG_B64)

    if st.button("Digitize Order & Run Medication Safety Audit", type="primary"):
        result = chartvision.digitize_clinical_chart(
            image_bytes=image_bytes,
            file_name=uploaded_file.name if uploaded_file else "chart_sample.jpg",
            context_notes=context_in,
            document_type=type_in,
        )

        if result.has_high_alert_drug:
            banner("warn", "⚠️ HIGH-ALERT MEDICATION VERIFICATION TRIGGERED")
            for alert in result.alerts:
                st.write(f"- {alert}")

        st.markdown(result.report)

    with st.expander("What just happened?"):
        st.markdown("""
High-risk drugs (Insulin, Anticoagulants, Methotrexate) trigger automatic double-check protocols, and dangerous abbreviations
(like 'U' for units) are flagged to prevent medication transcription errors.
""")


# ---------------------------------------------------------------- 13. FundusVision
elif page == "fundus":
    st.title("FundusVision")
    st.caption("**Capability: retinal fundus screening & papilledema alert.** Grades Diabetic & Hypertensive Retinopathy "
               "while enforcing deterministic safety triggers for Bilateral Papilledema (elevated ICP).")

    fundus_samples = getattr(samples, "FUNDUS_SAMPLES", getattr(fundusvision, "FUNDUS_SAMPLES", []))
    st.write("**Try a sample fundus screening case:**")
    cols = st.columns(len(fundus_samples))
    for col, sample_case in zip(cols, fundus_samples):
        if col.button(sample_case["label"], key=f"fs_{sample_case['eye_side']}", use_container_width=True):
            st.session_state.fundus_context = sample_case["context"]
            st.session_state.fundus_side = sample_case["eye_side"]

    side_in = st.selectbox("Eye Examined", ["Right Eye (OD)", "Left Eye (OS)", "Bilateral Fundus (OU)"], index=0)
    context_in = st.text_area("Patient History & Symptoms",
                              value=st.session_state.get("fundus_context", fundus_samples[0]["context"] if fundus_samples else ""),
                              height=120)

    uploaded_file = st.file_uploader("Upload Fundus Photograph (PNG, JPG)", type=["png", "jpg", "jpeg"])
    import base64
    image_bytes = uploaded_file.read() if uploaded_file else base64.b64decode(fundusvision.TINY_PNG_B64)

    if st.button("Run Retinal Vision Assessment", type="primary"):
        result = fundusvision.analyze_fundus_image(
            image_bytes=image_bytes,
            file_name=uploaded_file.name if uploaded_file else "fundus_sample.jpg",
            clinical_context=context_in,
            eye_side=side_in,
        )

        if result.has_papilledema_alert:
            banner("danger", "🚨 EMERGENCY NEUROLOGICAL ALERT TRIGGERED")
            for alert in result.alerts:
                st.write(f"- {alert}")

        st.markdown(result.report)

    with st.expander("What just happened?"):
        st.markdown("""
Optic disc margin blurring and papilledema trigger immediate emergency neuro-imaging warnings (Brain MRI/CT)
to rule out intracranial mass lesions before providing ETDRS retinopathy staging.
""")


# ---------------------------------------------------------------- 14. OtoscopeAI
elif page == "otoscope":
    st.title("OtoscopeAI")
    st.caption("**Capability: ENT otoscopic visual diagnostics.** Evaluates tympanic membrane opacity & mobility, "
               "enforcing deterministic red flags for Acute Mastoiditis, TM Perforation, and Necrotizing Otitis Externa.")

    oto_samples = getattr(samples, "OTOSCOPE_SAMPLES", getattr(otoscope, "OTOSCOPE_SAMPLES", []))
    st.write("**Try a sample otoscopic case:**")
    cols = st.columns(len(oto_samples))
    for col, sample_case in zip(cols, oto_samples):
        if col.button(sample_case["label"], key=f"os_{sample_case['ear_side']}", use_container_width=True):
            st.session_state.oto_context = sample_case["context"]
            st.session_state.oto_side = sample_case["ear_side"]

    ear_in = st.selectbox("Ear Examined", ["Right Ear (AD)", "Left Ear (AS)", "Bilateral Ears"], index=0)
    context_in = st.text_area("Patient Otalgia & Clinical Symptoms",
                              value=st.session_state.get("oto_context", oto_samples[0]["context"] if oto_samples else ""),
                              height=120)

    uploaded_file = st.file_uploader("Upload Otoscopic Image (PNG, JPG)", type=["png", "jpg", "jpeg"])
    import base64
    image_bytes = uploaded_file.read() if uploaded_file else base64.b64decode(otoscope.TINY_PNG_B64)

    if st.button("Run Otoscopic Diagnostic Analysis", type="primary"):
        result = otoscope.analyze_otoscopy_image(
            image_bytes=image_bytes,
            file_name=uploaded_file.name if uploaded_file else "otoscopy_sample.jpg",
            clinical_context=context_in,
            ear_side=ear_in,
        )

        if result.has_critical_ent_flag:
            banner("danger", "🚨 CRITICAL ENT RED-FLAG TRIGGERED")
            for alert in result.alerts:
                st.write(f"- {alert}")

        st.markdown(result.report)

    with st.expander("What just happened?"):
        st.markdown("""
Retroauricular swelling or TM perforations trigger immediate emergency ENT referral alerts and ototoxic drop warnings
prior to analyzing tympanic membrane erythema and bulging for Acute Otitis Media.
""")


# ---------------------------------------------------------------- 15. ECGVision
else:
    st.title("ECGVision")
    st.caption("**Capability: 12-lead ECG telemetry & cardiac red-flag triggers.** Evaluates ischemic ST-T changes, "
               "rhythm disturbances, and interval prolongations while enforcing deterministic safeguards for Acute STEMI, "
               "Sustained Ventricular Tachycardia, Severe Hyperkalemia, and QTc Prolongation.")

    ecg_samples = getattr(samples, "ECG_SAMPLES", getattr(ecgvision, "ECG_SAMPLES", []))
    st.write("**Try a sample cardiology case:**")
    cols = st.columns(len(ecg_samples))
    for col, sample_case in zip(cols, ecg_samples):
        if col.button(sample_case["label"], key=f"es_{sample_case['file_name']}", use_container_width=True):
            st.session_state.ecg_context = sample_case["context"]
            st.session_state.ecg_lead = sample_case["lead_view"]

    lead_in = st.selectbox("ECG Format / Lead View", ["12-Lead ECG", "Rhythm Strip (Lead II)", "Bedside Telemetry Monitor"], index=0)
    context_in = st.text_area("Patient Presentation & Vitals",
                              value=st.session_state.get("ecg_context", ecg_samples[0]["context"] if ecg_samples else ""),
                              height=120)

    uploaded_file = st.file_uploader("Upload ECG Image / Telemetry Strip (PNG, JPG)", type=["png", "jpg", "jpeg"])
    import base64
    image_bytes = uploaded_file.read() if uploaded_file else base64.b64decode(ecgvision.TINY_PNG_B64)

    if st.button("Run ECG Diagnostic & Cardiac Safety Assessment", type="primary"):
        result = ecgvision.analyze_ecg_image(
            image_bytes=image_bytes,
            file_name=uploaded_file.name if uploaded_file else "ecg_sample.png",
            clinical_context=context_in,
            lead_view=lead_in,
        )

        if result.has_critical_cardiac_flag:
            banner("danger", "🚨 CRITICAL CARDIAC SAFETY RED-FLAG TRIGGERED")
            for alert in result.alerts:
                st.write(f"- {alert}")

        st.markdown(result.report)

    with st.expander("What just happened?"):
        st.markdown("""
ST-elevation patterns (V1-V4, II/III/aVF) or hyperkalemic T-waves trigger immediate STAT emergency protocols
(Cath Lab activation <90 min, IV Calcium Gluconate) locally before model output synthesis.
""")




