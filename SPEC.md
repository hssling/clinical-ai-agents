# Build Your Own Clinical AI Agent — Session Design Spec

**Speaker:** Dr. Siddalingaiah H S, Professor, Dept. of Community Medicine, SIMS&RH
**Event:** CME — *Artificial Intelligence in Healthcare: From Theory to Clinical Mastery*
**Host:** Dept. of Anatomy, Shridevi Institute of Medical Sciences & Research Hospital, Tumkur
**Date:** 12 August 2026 · **Slot:** 12:30 – 13:15 (45 min, hard stop — lunch follows)
**Accreditation:** Applied for KMC credit hours

---

## 1. Constraints that drive every decision

| Constraint | Consequence for the design |
|---|---|
| Hard 13:15 stop, lunch immediately after | Live build front-loaded; Q&A is the compressible block, not the demo |
| Pre-lunch attention trough | Cold open with a *working* agent before any definition |
| Audience = clinicians & medical educators, not developers | No terminal work until minute 24; no `pip install` on stage |
| Auditorium wifi unreliable at scale | Every component must run fully offline via `MOCK_MODE` |
| Morning sessions already cover ethics (09:30) and multimodal GenAI (10:45) | Reference, don't re-teach; callback to governance during the failure demo |

## 2. Session arc

| Clock | Block | Min | Medium |
|---|---|---|---|
| 12:30 | Cold open — audience question answered live with citation | 3 | Live agent |
| 12:33 | What IS an agent — vs chatbot, the 4 parts, the loop | 5 | Slides |
| 12:38 | Utility — where it pays off in a clinician's week | 4 | Slides |
| 12:42 | **LIVE BUILD** — guideline agent, no code | 8 | Browser |
| 12:50 | **LIVE TEST** — including a deliberate refusal | 4 | Browser |
| 12:54 | **LIVE DEPLOY** — coded version, edit one line, push, refresh | 5 | Terminal + URL |
| 12:59 | Gallery — 3 remaining prototypes, 90s each | 5 | Deployed app |
| 13:04 | Requirements — technical, data, governance, cost | 4 | Slides |
| 13:08 | Future prospects + Monday-morning actions | 3 | Slides |
| 13:11 | QR takeaway + Q&A | 4 | Slides |
| 13:15 | **HARD STOP** | | |

### Two load-bearing choices

**Cold open precedes all definition.** A real question from the floor, answered in ~10 seconds with a guideline page citation, then: *"I built that in six minutes; by 1:15 you'll have the link."* Pre-lunch audiences do not grant patience — it must be bought.

**The agent is made to fail on purpose.** During LIVE TEST, an out-of-scope question is asked and the agent *refuses* rather than fabricates. This is the highest-value minute of the session: it separates the talk from AI hype, discharges the hallucination objection before Q&A, and calls back to the 09:30 governance session.

## 3. The eight clinical prototypes

One core capability each — the progression *is* the argument of the talk.

| # | Name | Clinical job | Capability taught |
|---|---|---|---|
| 1 | **GuideBot** ⭐ | Answers from national guidelines with citations; refuses when unsupported | Grounding — retrieval, citation, refusal |
| 2 | **DischargeDraft** | Case notes → structured discharge summary | Structured generation — schema-constrained output |
| 3 | **TriageAssist** | Complaint → follow-ups → red-flag detection → escalation | The agentic loop — multi-turn, decides when to stop |
| 4 | **ScreenMate** | Screens abstracts against inclusion/exclusion criteria | Tool use at scale — batch, machine-readable output |
| 5 | **PharmGuard** | Prescriptions → interactions, allergy alerts & renal dose checks | Safety overrides — local deterministic validation |
| 6 | **LabAlert** | Lab panels → panic value detection & critical alerts | Boundary checks — numerical range validation |
| 7 | **TrialMatch** | Patient summary vs protocol criteria → matrix breakdown | Reasoning matrix — multi-attribute evaluation |
| 8 | **DiffCheck** | Symptoms → differential matrix & red-teaming safety checklist | Cognitive debiasing — red-teaming anchoring bias |

**TriageAssist ships with a permanent, non-dismissible on-screen banner: "EDUCATIONAL DEMONSTRATION — NOT FOR CLINICAL USE."** Non-negotiable in an accredited session.

## 4. Architecture

```
Streamlit app ──► agents/ ──► provider layer ──► Gemini (free tier)
  8 pages         8 modules    swappable        └─ MOCK_MODE ──► canned replies
```

- **One app, eight pages, one URL.** Eight browser tabs is an unaffordable risk on stage.
- **Gemini free tier default.** Free key, no credit card, available in India. Provider layer is swappable to OpenAI/Anthropic in one line.
- **`MOCK_MODE=1` is the fallback kit, not a toy.** Realistic pre-written responses, zero internet, zero API key. If wifi fails at 12:42, one environment variable keeps the entire demo live. The audience cannot tell.
- **Hugging Face Spaces for deploy.** Free, public URL, `git push` rebuilds in 60–90s. The rebuild window is covered by the Requirements slide — dead air becomes stagecraft.

## 5. Deliverables

```
clinical-ai-agent-session/
├─ README.md          start here, in order
├─ SPEC.md            this file
├─ slides/            45-min PPTX, speaker notes + running clock
├─ prototypes/        4 agents, Streamlit, MOCK_MODE, sample data
├─ run-sheet/         stage script, pre-flight checklist, Plan B
├─ handout/           participant PDF, prompt pack, safety checklist, MCQs
├─ tools/             cost calculator, agent-anatomy page
└─ deploy/            HF Space setup, live-edit rehearsal
```

Slides are **PPTX**, not HTML: editable by the speaker, opens on any auditorium machine, survives no internet.

### Extras included

| | Tool | Purpose |
|---|---|---|
| A | Prompt Pack — 12 copy-paste clinical agent prompts | Highest-value non-coder takeaway |
| B | 10-point Clinical AI Safety Checklist, printable | The artefact an accredited CME should leave behind |
| C | 5 MCQs + feedback form | KMC credit-hours paper trail; clean close |
| D | Interactive "Agent Anatomy" web page, QR-linked | Post-lunch exploration |
| E | Cost-of-running calculator | Kills the "we can't afford AI" objection with rupee figures |

## 6. Assumptions

1. Presentation from the speaker's own Windows laptop, projector-connected.
2. Free Google AI Studio API key and free Hugging Face account created before the day.
3. Sample data = condensed extracts of Indian national-programme guidelines, clearly labelled as such; speaker may substitute their own PDFs.
4. Every component degrades gracefully to fully offline.

## 7. Explicitly out of scope (YAGNI)

- Audience build-along on their own devices — wifi risk outweighs engagement gain; QR takeaway serves the same goal.
- Real patient data of any kind, at any point.
- Fine-tuning, model training, vector databases — named in "future prospects", not built.
- Any claim of clinical validation or regulatory clearance for the prototypes.
