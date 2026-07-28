# The Clinical AI Safety Checklist

**Ten questions to ask before any AI tool touches your patients** — whether you built it or a vendor is selling it to you.

Print this. Take it to the meeting.

---

### 1 · Can it say "I don't know"?

Ask it something outside its knowledge. **Does it refuse, or does it guess?**

> A tool that never refuses is guessing and not telling you. If a vendor cannot demonstrate a refusal on demand, that is your answer.

☐ Demonstrated ☐ Failed ☐ Not tested

---

### 2 · Where did that answer come from?

Every clinical claim should point to a source you can open and check.

> "The AI said so" is not a source. If you cannot trace a statement back to a document, you cannot defend the decision built on it.

☐ Cites checkable sources ☐ No sources ☐ Sources given but wrong

---

### 3 · Who is clinically responsible for its output?

A **named** person, not a department or a committee.

> If nobody's name is on it, nobody is checking it. This is the question that most often has no good answer.

Named owner: ________________________

---

### 4 · What happens to the data we put in?

Is it stored? For how long? Is it used to train the model? Which country is it in?

> Under the **Digital Personal Data Protection Act 2023**, you have duties as a data fiduciary. "The vendor handles that" is not a defence.

☐ Answered in writing ☐ Vague ☐ Not answered

---

### 5 · Has identifiable patient data been excluded — and how do you know?

Not "we told staff not to." **What automatically stops it?**

> Names, phone numbers, hospital numbers, addresses, full dates of birth, photographs. A check that depends on people remembering will fail on a busy day.

☐ Automated check ☐ Policy only ☐ Nothing

---

### 6 · How well does it actually perform — measured against what?

Accuracy on what sample, judged by whom, compared to which standard?

> Vendor demos are chosen to succeed. Ask for performance on cases the vendor did not pick, ideally yours.

☐ Independent evaluation ☐ Vendor figures only ☐ No data

---

### 7 · How does it fail?

Not *whether* — *how*. Does it fail loudly or silently?

> A tool that fails loudly is safe. A tool that quietly returns a plausible wrong answer is dangerous, and the more fluent it is, the more dangerous.

☐ Fails visibly ☐ Fails silently ☐ Unknown

---

### 8 · Can a human override it, and is that easy?

The override must be at least as easy as accepting.

> If disagreeing takes four extra clicks and accepting takes none, the tool is making the decisions regardless of what the policy says.

☐ Easy override ☐ Difficult ☐ None

---

### 9 · Is there an audit trail?

Who asked what, when, what it answered, and what the clinician did with it.

> You need this for incident review, for medico-legal defence, and for knowing whether the thing is being used at all. Build it in from day one — it cannot be added retrospectively.

☐ Full log ☐ Partial ☐ None

---

### 10 · What is it *not* for — written down, agreed, and communicated?

The boundary must exist on paper before the tool is in use.

> Every AI incident in healthcare so far has involved a tool used slightly outside what it was validated for. The boundary you don't write down is the one that gets crossed.

Not to be used for: ________________________________

---

## Scoring

| Answered well | What it means |
|---|---|
| **9–10** | Proceed, with monitoring |
| **6–8** | Pilot only. Fix the gaps before wider use. |
| **3–5** | Not ready. Do not put this in front of patients. |
| **0–2** | Walk away. |

---

## The three questions that matter most

If you only have five minutes in that meeting, ask these:

1. **"Show me it refusing to answer something."** *(Question 1)*
2. **"Whose name is on the output?"** *(Question 3)*
3. **"What is this NOT for?"** *(Question 10)*

The quality of the pause before each answer tells you most of what you need to know.

---

*Prepared for the CME on Artificial Intelligence in Healthcare, SIMS&RH Tumkur, 12 August 2026 — session: Build Your Own Clinical AI Agent, Dr. Siddalingaiah H S, Dept. of Community Medicine.*
