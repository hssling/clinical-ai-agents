# Post-Session Assessment & Feedback

**Session:** Build Your Own Clinical AI Agent<br>
**CME:** Artificial Intelligence in Healthcare — From Theory to Clinical Mastery<br>
**SIMS&RH Tumkur · 12 August 2026 · 12:30–13:15**<br>
**Faculty:** Dr. Siddalingaiah H S, Professor, Dept. of Community Medicine

*For KMC credit hour documentation.*

Name: _______________________  Designation: _______________  Dept: ____________

---

## Part A — Assessment (5 questions, single best answer)

**1. Which of the following best distinguishes an AI *agent* from an AI *chatbot*?**

- A. An agent uses a larger language model
- B. An agent pursues a goal over multiple steps and can use tools, deciding its own next step within limits set by the user
- C. An agent is trained on medical data specifically
- D. An agent does not make mistakes

---

**2. A clinician builds a guideline assistant and asks it a question that the uploaded guidelines do not address. The tool produces a confident, fluent, plausible answer. This most likely indicates:**

- A. The tool has additional medical knowledge and is being helpful
- B. The tool lacks an effective grounding guardrail and is generating an ungrounded answer
- C. The guidelines were uploaded incorrectly
- D. The model needs to be retrained

---

**3. Which statement about safety rules in a clinical AI agent is correct?**

- A. Safety rules written into the prompt are enforced by the model and cannot be bypassed
- B. Safety rules implemented in the surrounding application code are more reliably enforced than rules written into the prompt
- C. Safety rules are unnecessary if the model is recent enough
- D. Safety rules should be added only after the tool is deployed

---

**4. Before pasting clinical text into a public AI service, the *minimum* requirement is:**

- A. Informed consent from the patient for AI use
- B. Removal of identifiers — name, contact details, hospital number, address, full date of birth
- C. Approval from the hospital's IT department
- D. Nothing, provided the clinician does not save the output

---

**5. A vendor demonstrates an AI tool for clinical decision support. Which single request is most informative about its safety?**

- A. "Show me your accuracy figures"
- B. "Show me the list of hospitals using it"
- C. "Show me it refusing to answer a question outside its knowledge"
- D. "Show me which model it uses"

---

<div style="page-break-after: always;"></div>

## Part B — Feedback

**1. Rate this session** (1 = poor, 5 = excellent)

| | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Relevance to my work | ☐ | ☐ | ☐ | ☐ | ☐ |
| Clarity of explanation | ☐ | ☐ | ☐ | ☐ | ☐ |
| Usefulness of the live demonstration | ☐ | ☐ | ☐ | ☐ | ☐ |
| Practical takeaways I can use | ☐ | ☐ | ☐ | ☐ | ☐ |
| Pace and time management | ☐ | ☐ | ☐ | ☐ | ☐ |

**2. How likely are you to build an AI agent yourself in the next month?**

☐ Already planning one  ☐ Likely  ☐ Unsure  ☐ Unlikely

**3. What is the one thing from this session you will actually use?**

_______________________________________________________________

**4. What did you want more of? What would you cut?**

_______________________________________________________________

**5. Would you attend a hands-on workshop where you build one yourself?**

☐ Yes, half day  ☐ Yes, full day  ☐ No

**6. Anything else:**

_______________________________________________________________

---

<div style="page-break-after: always;"></div>

## Answer Key — For Faculty Use

| Q | Answer | Teaching point |
|---|---|---|
| **1** | **B** | The defining feature is the *loop*: multi-step, tool-using, self-directed within limits. Model size and training data are irrelevant to the distinction. D is false of any AI system. |
| **2** | **B** | This is ungrounded generation — "hallucination". Fluency and confidence are **not** correlated with correctness, which is precisely why a refusal mechanism matters. |
| **3** | **B** | Prompt-based rules are requests the model may or may not honour. Rules enforced in surrounding code execute deterministically. Demonstrated live via the pre-model grounding threshold. |
| **4** | **B** | De-identification is the minimum. C may also be required institutionally, and consent (A) becomes relevant for wider deployment — but neither substitutes for removing identifiers first. |
| **5** | **C** | Accuracy figures are vendor-selected; deployment lists say nothing about safety. A demonstrated refusal is the single hardest thing to fake and the most informative about grounding. |

**Suggested pass mark:** 4 of 5.

**If a cohort scores poorly on Q3**, it is worth re-emphasising in future sessions — it is the least intuitive point and the most consequential for anyone actually procuring a tool.
