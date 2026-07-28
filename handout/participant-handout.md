# Build Your Own Clinical AI Agent

**CME: Artificial Intelligence in Healthcare — From Theory to Clinical Mastery**<br>
SIMS&RH Tumkur · Dept. of Anatomy · 12 August 2026<br>
Dr. Siddalingaiah H S · Professor, Dept. of Community Medicine

---

## What an agent is

An **agent** is not a chatbot. A chatbot answers what you ask. An agent pursues a goal you set — deciding its own next step, using tools, and looping until it is done or you stop it.

The clinical parallel is an intern: knowledge, standing orders, access to the ward, memory of the patient — and the judgement to escalate.

### Every agent has exactly four parts

| Part | What it is | Clinical parallel |
|---|---|---|
| **1 · The model** | The reasoning engine — GPT, Gemini, Claude | An intern's medical knowledge: broad, but knows nothing about *your* hospital |
| **2 · Instructions** | What it must and must not do — **in plain English** | Your department's standing orders. **This is where safety lives.** |
| **3 · Tools** | What it can reach: documents, calculators, systems | Access to the chart. An intern without it is useless. |
| **4 · Memory** | What it carries across the conversation | The case file |

**Part 2 is written in plain English, not code.** That is why a clinician can build one of these — and why a programmer alone cannot.

---

## Build one in 30 minutes — the recipe

You need: a laptop, a browser, and a free account. No installation. No cost.

**1 · Pick your builder** — any of: Google AI Studio (Gems), ChatGPT (Custom GPT), or Claude (Projects). All have a free tier.

**2 · Create a new agent and name it.**

**3 · Write the instructions.** This is the clinical work — take your time:

```
You are a clinical guideline assistant for [YOUR DEPARTMENT].

Rules:
1. Answer ONLY from the documents provided. They are your only source of truth.
2. Cite the section after every factual claim.
3. If the documents do not cover it, say exactly:
   "This is not covered in the guidelines I have been given."
   Do not use outside knowledge to fill the gap.
4. Never give individualised treatment advice for a named patient.
5. Be brief. Three to five sentences.
```

**4 · Upload your documents.** Guidelines, protocols, SOPs. These become its tools.

**5 · Test it** — with the three tests below.

**6 · Share it** when it passes. Not before.

> **Rule 3 is the whole game.** Without it you have a confident guesser. With it you have a tool you can defend.

---

## The three tests — run these on ANY AI tool

| | Test | What good looks like |
|---|---|---|
| **1** | Ask something it should know | Answers **and cites a source you can open** |
| **2** | Ask something outside its documents | **It refuses** |
| **3** | Ask it to treat a named patient | **It declines** |

**If it fails test 2, it is not safe for clinical use.**

That is also the single best question to put to a vendor: *"Show me it refusing to answer."* The pause before the reply tells you most of what you need to know.

---

## Four capabilities — not one trick

| Capability | What it does | Where it pays off |
|---|---|---|
| **Grounding** | Answers only from documents you trust, with citations | Guideline queries at the point of care |
| **Structured output** | Free text in, fixed format out | Discharge summaries, referrals, records |
| **The loop** | Multi-step reasoning that knows when to stop | Triage support, adaptive checklists |
| **Scale** | The same judgement across hundreds of records | Systematic reviews, chart audits |

All four were demonstrated live. All four are on the link below, running.

---

## Before you deploy anything — the non-negotiables

- **No identifiable patient data** into a public AI service. Ever. Not names, contact details, hospital numbers, addresses, or full dates of birth.
- **A named clinician owns the output.** Not a committee.
- **A human decides.** Nothing here diagnoses or prescribes.
- **DPDP Act 2023 duties apply** to you as a data fiduciary. "The vendor handles it" is not a defence.
- **Write down what it is NOT for**, before anyone uses it.
- **Log everything** from day one — it cannot be added later.

The full 10-point safety checklist is in your takeaway pack.

---

## What it costs

| Scenario | Volume | Cheap model | Frontier model |
|---|---|---|---|
| Prototyping | Under the free tier | **₹0** | **₹0** |
| One department, guideline Q&A | 2,000/month | **₹36** | **₹446** |
| Whole hospital, guideline Q&A | 20,000/month | **₹356** | **₹4,455** |
| Hospital-wide discharge summaries | 10,000/month | **₹297** | **₹3,712** |
| Screening a systematic review | 5,000 abstracts, once | **₹30** | **₹379** |

There is no single price for "AI" — the same job costs roughly **twelve times more** on a frontier model. Picking the cheapest model that passes the three tests is a real decision with real money attached.

**Model costs only.** Staff time to build, validate and govern it is the real cost, and it is not zero. Recalculate with current prices using `tools/cost_calculator.py` in your takeaway pack.

> ⚠️ **"It fits in the free tier" is about volume, not suitability.** Free tiers have rate limits, no uptime guarantee, no data-processing agreement, and terms that often allow the provider to train on your inputs. Prototype free; pay the moment real users depend on it.

---

## Three things to do on Monday

**1 · Build one** — 30 minutes. Take one guideline you look up often. Follow the recipe above.

**2 · Break one** — 15 minutes. Run the three tests on an AI tool you already use. If it never refuses, stop trusting it with clinical questions.

**3 · Ask one question** — 5 minutes. Next time a vendor pitches AI to this hospital: *"Show me it refusing to answer."*

---

## Your takeaway pack

Scan the QR code from the session, or use the link below. It contains:

- **The four prototypes**, live — open them, break them, copy them
- **The prompt pack** — 12 clinical agent prompts, ready to paste
- **The safety checklist** — 10 questions to ask before any AI tool sees a patient
- **The full source code** — including the safety logic shown on stage

🔗 ______________________________________________

---

*Educational prototypes only. Not medical devices. No real patient data was used in this session.*
