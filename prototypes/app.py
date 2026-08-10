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
from agents import diffcheck, discharge, guidebot, labalert, pharmguard, provider, screenmate, triage, trialmatch  # noqa: E402
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
    st.caption("**Capability: structured generation.** Messy ward notes in, "
               "a fixed-schema discharge summary out — with the schema checked by us, not the model.")

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
        banner("warn", "⚠️ Identifier check failed — do not send this text to any AI service")
        for warning in live_warnings:
            st.write(f"- {warning}")

    if st.button("Draft discharge summary", type="primary"):
        result = discharge.draft(notes)

        if result.missing_sections:
            banner("warn", f"Schema check: missing {', '.join(result.missing_sections)}")
        else:
            banner("ok", "✅ Schema check passed — all 8 required sections present")

        st.markdown(result.summary)

    with st.expander("What just happened?"):
        st.markdown("""
The identifier scan runs **on this machine, before anything is sent anywhere**.
That ordering is the whole point: a privacy check that runs after the network
call has already protected nothing.

The eight headings are then verified in the output by the application. The model
is asked for structure; the code confirms it. Never trust a model to be the last
line of validation on its own output.
""")


# ---------------------------------------------------------------- 3. TriageAssist
elif page == "triage":
    st.title("TriageAssist")
    banner("danger", "⚠️ EDUCATIONAL DEMONSTRATION — NOT FOR CLINICAL USE")
    st.caption("**Capability: the agentic loop.** It decides whether it has enough "
               "information, asks a follow-up if not, and stops when it must.")

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
one of three moves: escalate, ask one more question, or stop.

Two things are deliberately not left to the model:

- **Red flags are plain Python** — {len(triage.RED_FLAGS)} patterns checked locally.
  The model cannot talk the agent out of escalating, and the rules work offline.
- **The loop is budgeted** at {triage.MAX_QUESTIONS} questions. An agent that can
  decide to continue must also be forced to stop.
""")


# ---------------------------------------------------------------- 4. ScreenMate
else:
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
Output is **JSON, not prose** — so it flows into the next step of a workflow
instead of being re-read by a person. That is the difference between a chatbot
and an agent doing real work.

Three safeguards worth copying:

- An unrecognised verdict becomes **UNCLEAR**, never a silent INCLUDE. Failures
  must fall towards more human review, not less.
- Any abstract the model skipped is **surfaced**, not quietly dropped.
- UNCLEAR exists at all, so the agent can say *"I cannot tell from this."*
""")


# ---------------------------------------------------------------- 5. PharmGuard
elif page == "pharm":
    st.title("PharmGuard")
    st.caption("**Capability: deterministic safety overrides.** Hardcoded medical safety tables "
               "run locally *before* calling the LLM. High-risk contraindications override model output.")

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
The interaction table and allergy check run **locally in Python before the prompt is constructed**.
If a life-threatening contraindication (e.g. Warfarin + NSAID, or Metformin in eGFR < 30) is present,
it generates a high-severity alert banner regardless of what the LLM generates.
Safety guardrails must be deterministic, not prompt-dependent.
""")


# ---------------------------------------------------------------- 6. LabAlert
elif page == "lab":
    st.title("LabAlert")
    st.caption("**Capability: numerical boundary check.** Parses numeric lab metrics locally and "
               "triggers immediate emergency banners for critical 'Panic Values'.")

    if st.button("📋 Load critical lab panel sample", use_container_width=True):
        st.session_state.lab_text = samples.LAB_PANEL_CRITICAL

    lab_input = st.text_area("Laboratory Panel Report",
                             value=st.session_state.get("lab_text", samples.LAB_PANEL_CRITICAL),
                             height=220)

    if st.button("Analyze Lab Panel", type="primary"):
        result = labalert.analyze_labs(lab_input)

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
else:
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

