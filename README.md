# Build Your Own Clinical AI Agent

[![CI](https://github.com/hssling/clinical-ai-agents/actions/workflows/ci.yml/badge.svg)](https://github.com/hssling/clinical-ai-agents/actions/workflows/ci.yml)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://clinical-ai-agents.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-0E8F84.svg)](LICENSE)

**Four working clinical AI agents, and everything needed to teach how they are built.**

**CME: Artificial Intelligence in Healthcare — From Theory to Clinical Mastery**
Shridevi Institute of Medical Sciences & Research Hospital, Tumkur · Dept. of Anatomy
**12 August 2026 · 12:30–13:15 · Hospital Auditorium**
Dr. Siddalingaiah H S, Professor, Dept. of Community Medicine

> ⚠️ **Educational demonstrations. Not medical devices.** Not clinically validated, no regulatory clearance. Must not be used to diagnose, treat, or direct management of any patient. No real patient data was used. See [LICENSE](LICENSE).

**🔗 Live app:** https://clinical-ai-agents.streamlit.app
**🔗 Interactive companion:** https://claude.ai/code/artifact/547c7a43-b3e2-4a18-a3bc-9cd652f40a85

---

## The four agents

| # | Agent | Clinical job | Capability it demonstrates |
|---|---|---|---|
| 1 | **GuideBot** | Answers from national guidelines with citations — and **refuses** when they don't cover it | Grounding |
| 2 | **DischargeDraft** | Ward notes → structured discharge summary, with a local identifier scan | Structured generation |
| 3 | **TriageAssist** | Complaint → follow-ups → red flags → escalation | The agentic loop |
| 4 | **ScreenMate** | Screens abstracts against inclusion/exclusion criteria | Batch scale |

The progression is the argument: *"AI in medicine" is not one capability, it is at least four, and they carry different risks.*

---

## Start here

| When | Read this |
|---|---|
| **Right now** | `run-sheet/preflight-checklist.md` — the T-minus-1-week items take a while |
| **Rehearsing** | `run-sheet/stage-script.md` — minute-by-minute, with the words to say |
| **The night before** | `run-sheet/fallback-plan.md` — what to do when it breaks |
| **On the lectern** | `run-sheet/stage-script.md`, printed |

---

## What's in the box

```
clinical-ai-agents/
├─ README.md            you are here
├─ SPEC.md              the design, and why each choice was made
├─ streamlit_app.py     deploy entry point (hands over to prototypes/app.py)
├─ requirements.txt     runtime deps — Streamlit Cloud reads this
│
├─ .github/workflows/
│   ├─ ci.yml               tests + boot check + rebuilds deck & PDFs
│   └─ live-check.yml       daily: is the deployed app actually up?
│
├─ slides/
│   ├─ Build-Your-Own-Clinical-AI-Agent.pptx    28 slides, speaker notes, running clock
│   └─ build_deck.py                            edit + regenerate the deck
│
├─ prototypes/          FOUR WORKING AGENTS
│   ├─ app.py               Streamlit, 4 pages, one URL
│   ├─ agents/
│   │   ├─ provider.py         LLM layer + MOCK_MODE (the offline fallback)
│   │   ├─ retrieval.py        local keyword search — no network, ever
│   │   ├─ guidebot.py         1 · grounding, citation, refusal   ⭐ built live
│   │   ├─ discharge.py        2 · structured output + identifier check
│   │   ├─ triage.py           3 · the agentic loop + red flags
│   │   └─ screenmate.py       4 · batch screening, machine-readable
│   ├─ data/guidelines/     3 condensed national programme extracts
│   ├─ samples.py           one-click demo inputs (never type on stage)
│   ├─ test_grounding.py    12 checks on the refusal guardrail
│   └─ test_agents.py       17 checks across all four agents
│
├─ run-sheet/
│   ├─ stage-script.md          minute-by-minute, with the exact words
│   ├─ preflight-checklist.md   T-minus 1 week / 1 day / 1 hour / 5 min
│   └─ fallback-plan.md         the failure ladder
│
├─ handout/              .md sources + print-ready .pdf
│   ├─ participant-handout.md/.pdf    the main takeaway
│   ├─ prompt-pack.md/.pdf            12 clinical prompts
│   ├─ safety-checklist.md/.pdf       10 questions before any AI sees a patient
│   └─ mcqs-and-feedback.md/.pdf      5 MCQs + feedback (KMC paper trail)
│
├─ tools/
│   ├─ agent-anatomy.html    interactive companion page — the QR destination
│   ├─ cost_calculator.py    what it costs, in rupees, with assumptions shown
│   ├─ probe_models.py       which free models are usable RIGHT NOW
│   ├─ check_live_app.py     pre-flight check on the deployed app
│   └─ make_pdfs.py          regenerate the handout PDFs after editing
│
└─ deploy/
    ├─ streamlit-cloud-setup.md      ⭐ the primary deployment
    └─ huggingface-space-setup.md    alternative host
```

---

## CI/CD

```
   you edit code
        │
        ├──► git push ──┬──► GitHub Actions ── tests + boot check + rebuild materials
        │               │
        │               └──► Streamlit Cloud ── detects the push, redeploys (~90s)
        │
        └──► daily 12:00 IST ──► live-check ── is the deployed app still up?
```

| Workflow · job | Catches |
|---|---|
| `ci.yml` · **agents** | A broken guardrail — the refusal or the red flags stop working |
| `ci.yml` · **boot** | An import error or missing dependency, *before* Streamlit Cloud hits it |
| `ci.yml` · **materials** | A deck or PDF that no longer builds; uploads fresh copies as artifacts |
| `live-check.yml` · **reachable** | A deployment that is down, broken, or asleep |

**Streamlit Community Cloud has no deploy API or CLI** — the first app creation is a browser form, once. Everything after that is automatic: pushes redeploy on their own, and the workflows above verify each change before and after it lands. Setup: [`deploy/streamlit-cloud-setup.md`](deploy/streamlit-cloud-setup.md).

Download the latest built deck and PDFs from any green CI run — **Actions → the run → Artifacts → `session-materials`**. No Python needed.

---

## Run the prototypes

**Python 3.11.** Streamlit has no wheels for 3.14 — on the author's machine `python` is 3.14, so use `py -3.11` there.

```bash
git clone https://github.com/hssling/clinical-ai-agents
cd clinical-ai-agents
pip install -r requirements.txt

# Offline mode — no internet, no API key, everything works
MOCK_MODE=1 streamlit run streamlit_app.py
```

<details>
<summary>Windows PowerShell</summary>

```powershell
py -3.11 -m pip install -r requirements.txt
$env:MOCK_MODE="1"
py -3.11 -m streamlit run streamlit_app.py
```
</details>

For live mode, set **one** key — providers are checked in the order OpenRouter → Gemini → mock:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."   # openrouter.ai/keys  (recommended)
# or
export GOOGLE_API_KEY="AIza..."            # aistudio.google.com/apikey
```

Or copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill it in.

> **Why OpenRouter is the default:** its free models are shared capacity and throttle without warning — measured here, one model returned 0/3 while four others returned 3/3 in the same minute. So the provider walks a **fallback chain** and takes the first model that answers. Check the chain before you rely on it: `python tools/probe_models.py`.

**Verify — both must print `ALL PASS`** (this is what CI runs):

```bash
cd prototypes
MOCK_MODE=1 python test_grounding.py    # 12 checks on the refusal guardrail
MOCK_MODE=1 python test_agents.py       # 17 checks across all four agents
```

---

## The three things that make this survivable

**1 · `MOCK_MODE=1` is a complete offline fallback.**
Set one environment variable and every prototype runs with no internet and no API key. This is not a degraded demo. Retrieval, citations, the refusal decision, the identifier scan, the red flags and the loop budget are all **computed for real** — only the generated prose is pre-written. If the auditorium wifi dies at 12:42, you lose nothing.

**2 · The safety logic is ordinary code, not prompting.**
GuideBot's refusal is a scored threshold that runs *before* the model is called. TriageAssist's red flags are regular expressions. Neither can be argued with, neither costs anything, and both work with the wifi unplugged. This is the intellectual point of the session and it is true of the code, not just the slides.

**3 · You never type on stage.**
Every prototype has one-click sample buttons. `samples.py` holds the inputs, including a set of ward notes seeded with identifiers so the privacy check fires on demand.

---

## The live deploy demo, in one line

Change `GROUNDING_THRESHOLD` in `prototypes/agents/guidebot.py` from `0.30` to `0.75`, commit, push. Streamlit Cloud rebuilds in ~90 seconds; the agent now refuses things it used to answer.

One number, one line, a visible behaviour change. Full rehearsal steps in [`deploy/streamlit-cloud-setup.md`](deploy/streamlit-cloud-setup.md).

---

## Before the day — the three that take real time

1. **Deploy the app**, add the API key as a secret, and confirm the URL opens on your phone over mobile data — [`deploy/streamlit-cloud-setup.md`](deploy/streamlit-cloud-setup.md)
2. **Build GuideBot in the no-code builder once, timed.** Under 8 minutes, or cut a step.
3. **Record the four fallback videos** — `run-sheet/fallback-plan.md`

Everything else is recoverable on the day. These three are not.

---

## Things you should change

This package is built to be edited, not just used.

| File | Why you'd change it |
|---|---|
| `prototypes/agents/triage.py` → `RED_FLAGS` | **The clinical safety table is yours.** It encodes which presentations must escalate. Edit it to match your practice and local referral pathways — and consider editing it *live* on stage, since it shows the room that the clinician owns the safety rules, not the model. |
| `prototypes/data/guidelines/` | Swap in guidelines you actually use. The retrieval parses any `.md` with `## [ID] Title` section markers. |
| `prototypes/agents/guidebot.py` → `GROUNDING_THRESHOLD` | The caution dial. Raise it and the agent refuses more. |
| `slides/build_deck.py` | Regenerate the deck after any edit — the speaker notes live here too. |
| `tools/cost_calculator.py` | Re-run with current prices before the session. Model pricing moves. |

---

## Provenance and limits

- Guideline files are **condensed teaching extracts**, clearly labelled as such in each file. They are not authoritative. Verify against current MoHFW / Central TB Division / NP-NCD documents before any real use.
- **No real patient data** was used anywhere in this package. All clinical text is fictional.
- The prototypes are **educational demonstrations, not medical devices.** TriageAssist carries a permanent on-screen notice to that effect.
- Cost figures come from `tools/cost_calculator.py` with its stated assumptions. The slide, the handout and the calculator agree; if you change one, re-run the other two.
