# Stage Script — Build Your Own Clinical AI Agent

**12:30 – 13:15 · Hospital Auditorium, SIMS&RH Tumkur · 12 August 2026**

Print this. Keep it on the lectern. The **bold quoted lines** are worth saying close to verbatim — everything else is yours.

> **The one rule: you stop at 13:15.** Lunch is immediately after and the room will leave with or without you. If you are behind, cut from the Gallery block (12:59) first, then the Future block. Never cut the refusal demo.

---

## Before you start — 60 seconds while being introduced

| | |
|---|---|
| ☐ | Browser window 1: **the no-code builder**, logged in, blank agent ready |
| ☐ | Browser window 2: **the deployed app**, GuideBot page, already loaded |
| ☐ | Terminal open at `prototypes/`, on the right branch, `git status` clean |
| ☐ | Deck open in presenter view (speaker notes visible to you) |
| ☐ | Phone hotspot ON and laptop already connected to it — not the auditorium wifi |
| ☐ | Guideline PDFs on the desktop, ready to drag into the builder |

---

## 12:30 · COLD OPEN — 3 min

**Do not introduce yourself yet.** Walk on, go straight to the browser showing GuideBot.

> **"Before I tell you anything — give me a clinical question. Something from the national programmes. TB, immunisation, hypertension screening. Anyone."**

Take a question from the floor. Type it. Let them watch it answer.

Point at the citation on screen.

> **"Notice what it did there. It didn't just answer — it told you which section of which guideline that came from. You can go and check it."**

> **"I built that in about six minutes. By quarter past one you'll know exactly how, and you'll have the link on your phone."**

*Now* introduce yourself. 20 seconds. Move on.

**If nobody offers a question** (silence happens), use: *"What is the treatment regimen for drug-sensitive TB?"* and say **"Fine — I'll go first."**

**⏱ Leave by 12:33.**

---

## 12:33 · WHAT YOU'LL LEAVE WITH — 1 min

Slide 3. Read the four items fast.

> **"I'm not going to teach you to code today. I'm going to show you that you don't need to."**

**⏱ Leave by 12:34.**

---

## 12:34 · WHAT IS AN AGENT — 5 min

**Slide 5 — Chatbot vs Agent.** 90 seconds.

> **"A chatbot answers. An agent does."**

Work the last row — the intern parallel. This room supervises interns.

> **"Think about a good intern. They have knowledge. They have your standing orders. They can order tests and read the chart. They remember the patient. And crucially — they escalate when they're out of their depth. That is exactly what an agent is."**

**Slide 6 — the four parts.** 2 minutes. The most important conceptual slide.

Land this:

> **"Look at part two. The instructions. That's written in plain English, not code. That is the entire reason a clinician can build one of these — and the reason a programmer alone can't."**

> **"When I build one in a few minutes, watch where I spend my time. It'll be on part two. That's where your clinical expertise goes in."**

**Slide 7 — the loop.** 60 seconds. Don't over-teach — they'll see it in TriageAssist.

> **"Everything that's gone wrong with AI agents in the real world comes down to one of two things. Either it couldn't stop, or it couldn't say 'I don't know'."**

**⏱ Leave by 12:39.**

---

## 12:39 · UTILITY — 3 min

**Slide 9 — four capabilities.** 90 seconds.

> **"People ask 'is AI useful in medicine' as if it's one thing. It's at least four things, and they have completely different risk profiles. I've built you one of each — you'll see all four running today."**

**Slide 10 — where it does NOT belong.** 60 seconds. **Say every word.**

Nod to the morning:

> **"Dr. Sudha took you through the governance framework this morning. I'm going to show you where it actually bites."**

**⏱ Leave by 12:42. The build must start now.**

---

## 12:42 · LIVE BUILD — 8 min 🔴

Switch to the builder. **Narrate continuously — silence while you type loses the room.**

### Step 1 — Create and name it (1 min)

> **"New agent. I'll call it GuideBot. That's it — it exists. It's useless, but it exists."**

### Step 2 — Write the instructions (3 min)

> **"This is the part that matters. This is the clinical work."**

Type this. It is on slide 13 if you need it:

```
You are a clinical guideline assistant for Indian national health programmes.

Rules:
1. Answer ONLY from the documents provided. They are your only source of truth.
2. Cite the section after every factual claim.
3. If the documents do not cover it, say exactly:
   "This is not covered in the guidelines I have been given."
   Do not use outside knowledge to fill the gap.
4. Never give individualised treatment advice for a named patient.
5. Be brief. Three to five sentences.
```

**Stop after rule 3. Look at the room.**

> **"That one rule — rule three — is the difference between a tool you can use in a clinic and a tool that will embarrass you in front of a patient. Everything else here is convenience. That line is safety."**

### Step 3 — Give it documents (2 min)

Drag in the guideline PDFs.

> **"Now it has something to read. Before this, it knew a lot about medicine in general and nothing about our programmes. Now it's the other way round — and that's what we want."**

### Step 4 — Save and ask it something (2 min)

Ask: *"When is the measles-rubella second dose given?"*

> **"Six minutes. No code. No installation. No IT ticket."**

**⏱ Leave by 12:50.**

> 🚨 **IF ANYTHING BREAKS:** Do not debug on stage. Say **"and this is one I prepared earlier"**, switch to the deployed app, carry on. Nobody will mind and most won't notice. Debugging live is the only way to actually lose this room.

---

## 12:50 · LIVE TEST — 4 min 🔴

**This is the most important block of your session.**

### Test 1 — something it should know (45 sec)

Ask: *"Who counts as a presumptive TB case?"* Point at the citation.

### Test 2 — the refusal (2 min) ⭐

**Set it up before you press enter:**

> **"Now watch this. I'm going to ask it something I never gave it any documents about. A normal chatbot will answer this confidently — and it might even be right. But it will be guessing."**

Type: *"What is the dose of adrenaline in cardiac arrest?"*

Press enter. **Let the refusal sit on screen for a full beat before you speak.**

> **"It said no."**

Pause.

> **"That is the behaviour you should demand from any AI tool anyone tries to sell to this hospital. Ask them to show you it refusing to answer something. If they can't — or won't — walk away."**

### Test 3 — the named patient (45 sec)

Ask: *"My patient Ramesh has TB and diabetes, what should I prescribe him?"* It should decline to give individualised advice.

**Slide 16 — why it refused.** 60 seconds.

> **"If your safety rule is written inside the prompt, you're asking the model nicely. If it's written in the code around the model, it's a rule. Know which one you've got."**

**⏱ Leave by 12:54.**

---

## 12:54 · LIVE DEPLOY — 5 min 🔴

Switch to the terminal.

> **"That one lives in a browser tab. Let me show you the same agent written properly, and already live on the internet."**

Show the deployed URL in a browser. Then back to the terminal:

```bash
cd prototypes
# open agents/guidebot.py, find GROUNDING_THRESHOLD
```

Change `GROUNDING_THRESHOLD = 0.30` to `0.75`.

> **"One number. I've just made it far more cautious — it will now refuse things it used to answer. That's a clinical decision, and I just made it in one line. Not a meeting. Not a vendor request. One line."**

```bash
git add -A
git commit -m "Raise grounding threshold for stricter refusal"
git push
```

> **"It's rebuilding itself now. Takes about a minute — so let's use that minute."**

**⏱ Go straight to slide 18 (Deployment options). Do not watch the progress bar.**

Talk over the build (90 sec):

> **"Deployment isn't one thing. Most clinical pilots should stop at row one or two. You don't need a public web address to get value — you need one to get users. And row four is the honest one: the moment real patient data is involved, this stops being a weekend project and becomes an IT project. That's not a reason not to start. It's a reason to start at row one."**

Glance at the build. When green, switch back, **refresh**, re-run the question that used to work.

> **"Same agent. Stricter. Live on the internet. Three minutes."**

**⏱ Leave by 12:59.**

---

## 12:59 · GALLERY — 5 min 🔴

**90 seconds each. Watch the clock — this is where overruns happen.**

### DischargeDraft (90 sec)

Click **"Load notes containing identifiers"**. The privacy warning fires.

> **"It caught the phone number, the email, the hospital number and the date of birth — before sending anything anywhere. That check runs on my laptop. If your privacy check runs after the network call, it has protected nothing."**

Then draft the summary. Point at the schema-check banner.

### TriageAssist (90 sec)

Point at the red banner first.

> **"Note the banner. This is a teaching demonstration. It is not for clinical use, and I'd say the same to anyone showing you one."**

Click the chest pain case. It escalates immediately, with no questions.

> **"It didn't ask a single question. The red flag short-circuits the loop. And that rule is plain code — the AI doesn't get a vote on whether to escalate. That's deliberate."**

### ScreenMate (90 sec)

Run it. Show the verdict table.

> **"Six abstracts here. It works exactly the same on six hundred. That's the one that changes what a systematic review costs you in weekends."**

> ⏱ **IF BEHIND: cut ScreenMate.** One line — *"there's a fourth one for screening abstracts, it's on the link"* — and move on.

**⏱ Leave by 13:04.**

---

## 13:04 · REQUIREMENTS — 4 min

**Slide 21 — what you need.** 2 minutes. The reframe:

> **"The hard part of building a clinical AI agent isn't technical. It's that someone has to know enough medicine to notice when the output is subtly wrong. That person is you. That's not a skill you can outsource to the IT department."**

**Slide 22 — cost.** 90 seconds.

> **"The tea for this CME cost more than running a departmental guideline agent for a year."**

Be honest:

> **"Those are model costs only. The staff time to set it up and govern it is the real cost, and it isn't zero."**

**⏱ Leave by 13:08.**

---

## 13:08 · FUTURE + MONDAY — 3 min

**Slide 24 — the next three years.** 2 minutes. Don't let this become the talk.

> **"Every one of these exists in a lab today. The gap between a lab and a district hospital in Karnataka isn't technology. It's validation, governance, and somebody willing to own it."**

The PHC point lands hardest with this audience — a model running offline on a phone reaches the people who need it most.

**Slide 25 — three things on Monday.** 90 seconds. **This is your close — give it energy.**

Deliver item 3 slowly:

> **"Next time a vendor pitches AI to this hospital, ask them one question. Show me it refusing to answer. Then watch what happens."**

**⏱ Leave by 13:11.**

---

## 13:11 · QR + Q&A — 4 min

Put slide 26 up and **leave it up**.

> **"Everything's behind that code. The four prototypes, the recipe, the prompt pack, the safety checklist. Questions?"**

### Answers to the questions you will get

**"Is this legal / approved?"**
> As decision support, with a clinician in the loop and no identifiable data, you're on ordinary ground. The moment it directs management or touches patient identifiers, you need ethics approval and probably IT and regulatory involvement. Start where I started.

**"What about patient privacy?"**
> Nothing identifiable goes into a public AI service. You saw the check that catches it. For real deployment you need de-identification plus a hospital agreement, and DPDP Act duties apply.

**"Will it replace us?"**
> It didn't diagnose anything today. It refused when it didn't know. The job it removed was retyping, not deciding.

**"Which model should we use?"**
> Whichever is cheapest that passes the three tests. The model is the most swappable part of the whole system — that's the point of the design.

**"How do I get my department started?"**
> One person, one guideline, thirty minutes, no patient data. Show it to your HOD before you ask anyone for a budget.

**"How accurate is it?"**
> Honestly: unmeasured, for these prototypes. That's why nothing here decides anything. If you want to deploy for real, measuring accuracy against a gold standard is the work — and it's exactly the kind of study this institution can do.

---

## 13:15 · STOP

> **"The link's on the screen. I'll be here through lunch — come and find me."**

**Do not run into the lunch break. Ever.**
