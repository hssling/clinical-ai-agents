# Deploying the Prototypes — Hugging Face Spaces

**Do this at least a week before the session.** Not the night before.

You end up with a public URL anyone can open on their phone, and a `git push` that rebuilds it in about 90 seconds — which is the live deploy demo.

**Time: ~30 minutes the first time.** Free, no card.

---

## Why Hugging Face

Free, no credit card, Streamlit supported natively, and `git push` triggers a visible rebuild. That visible rebuild *is* the demo — the audience watches a change go live.

Streamlit Community Cloud also works and requires a GitHub repo. If you already live in GitHub, use that instead; the live-edit demo works the same way.

---

## 1 · Create the Space

1. Sign up at https://huggingface.co/join
2. **New Space** → https://huggingface.co/new-space
3. Fill in:
   - **Space name:** `clinical-ai-agents`
   - **License:** MIT
   - **SDK:** **Streamlit**
   - **Hardware:** CPU basic (free)
   - **Visibility:** **Public** ← must be public for the QR code to work

---

## 2 · Add your API key as a secret

**Settings** → **Variables and secrets** → **New secret**

- Name: `GOOGLE_API_KEY`
- Value: your key from https://aistudio.google.com/apikey

> 🔑 **Never put the key in a file.** A key committed to a public repo is scraped within minutes. If you ever do it by accident, revoke it immediately — rewriting git history is not enough.

**If you skip this step the app still works** — it detects the missing key and runs in offline mock mode. That is by design, but you want the real thing live.

---

## 3 · Push the code

```bash
git clone https://huggingface.co/spaces/YOUR-USERNAME/clinical-ai-agents
cd clinical-ai-agents

# Copy the prototypes in (adjust the source path)
cp -r "D:/AI workshop/clinical-ai-agent-session/prototypes/." .

git add -A
git commit -m "Clinical AI agent prototypes"
git push
```

Watch the **Building** indicator on your Space page. First build takes 2–4 minutes.

---

## 4 · Add the Space header

Hugging Face needs a `README.md` at the repo root with this front-matter:

```markdown
---
title: Clinical AI Agents
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.50.0
app_file: app.py
pinned: false
license: mit
---

# Clinical AI Agents — Four Working Prototypes

Educational prototypes from the CME *Artificial Intelligence in Healthcare*,
SIMS&RH Tumkur, 12 August 2026.

**Not medical devices. Not for clinical use. No real patient data.**
```

Commit and push it. The Space will rebuild.

---

## 5 · Verify — properly

- [ ] `https://huggingface.co/spaces/YOUR-USERNAME/clinical-ai-agents` loads
- [ ] Sidebar shows **LIVE**, not OFFLINE (if it says OFFLINE, the secret didn't take)
- [ ] All four prototypes work
- [ ] **GuideBot refuses** the adrenaline question ← the demo depends on this
- [ ] **Opens on your phone over mobile data**, not just on your laptop wifi
- [ ] QR code generated from the URL and pasted onto slide 26

---

## 6 · Rehearse the live edit — the actual demo

Run this **twice** before the day, with a stopwatch.

```bash
cd clinical-ai-agents

# Edit agents/guidebot.py:  GROUNDING_THRESHOLD = 0.30  ->  0.75

git add -A
git commit -m "Raise grounding threshold for stricter refusal"
git push
```

Then:
1. Switch to the Space page — it shows **Building**
2. **Advance to slide 18 and talk for 90 seconds.** Do not watch the bar.
3. When it goes green, refresh and re-ask a question that previously worked
4. It now refuses — the threshold is stricter

**Time it.** If your rebuild takes over two minutes, you need a second slide of material to talk over. Know that in advance.

> 💡 Why this edit and not another: it is **one number**, on **one line**, and the behaviour change is **visible in one query**. Resist the urge to demo something more impressive — on stage, legible beats clever.

---

## If a push asks for credentials

Hugging Face wants an access token, not your password.

1. https://huggingface.co/settings/tokens → **New token** → **Write** access
2. Use the token as the password when git prompts
3. Cache it so it never prompts on stage:

```bash
git config --global credential.helper store
```

Push once manually so the token is stored. **Do this before the day** — a credential prompt mid-demo is avoidable and looks bad.

---

## Troubleshooting

**Build fails: `ModuleNotFoundError`**
`requirements.txt` is missing or incomplete. It must be at the repo root and list `streamlit` and `google-genai`.

**Sidebar says OFFLINE on the live Space**
The secret is missing or misnamed. It must be exactly `GOOGLE_API_KEY`. Re-add it in Settings and **restart the Space** — secrets are read at startup.

**Space sleeps and is slow to wake**
Free Spaces sleep after inactivity. **Open your Space 10 minutes before the session** so it is warm. Put this on the pre-flight checklist — a 40-second cold start during your cold open is a bad way to begin.

**Build succeeds, app shows a blank page**
Check `app_file: app.py` in the README front-matter matches your actual filename.

**Everything is broken and it is the morning of the session**
Do not fix it. Run locally with `MOCK_MODE=1` and use the local URL. See `run-sheet/fallback-plan.md`. The session works fine without a deployed Space — you just describe the deploy step instead of performing it.
