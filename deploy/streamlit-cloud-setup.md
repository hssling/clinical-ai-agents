# Deploying to Streamlit Community Cloud

**This is the primary deployment.** Your Streamlit account is already connected to GitHub, so this is a one-form job — after that, every `git push` redeploys automatically.

> **Honest note on automation:** Streamlit Community Cloud has **no deploy API and no CLI**. The first app creation must be done in the browser. Everything *after* that is automated: pushes redeploy on their own, GitHub Actions tests every change before it lands, and a scheduled workflow checks the live app is still up.

---

## 1 · Create the app — the only manual step

1. Go to **https://share.streamlit.io/** (you are already signed in as `hssling`)
2. Click **Create app** → **Deploy a public app from GitHub**
3. Fill in:

   | Field | Value |
   |---|---|
   | Repository | `hssling/clinical-ai-agents` |
   | Branch | `main` |
   | Main file path | `streamlit_app.py` |
   | App URL | `clinical-ai-agents` *(gives `clinical-ai-agents.streamlit.app`)* |

4. Click **Deploy**

First build takes 2–4 minutes.

> The main file path is already the Streamlit default, so the form should pre-fill it correctly. `streamlit_app.py` at the repo root is a thin shim that hands over to `prototypes/app.py`.

---

## 2 · Add your API key

**App menu (⋮)** → **Settings** → **Secrets**, then paste **one** of these:

```toml
# Most reliable — OpenAI. Requires billing on the account.
OPENAI_API_KEY = "sk-proj-..."
MOCK_MODE = "0"
```

```toml
# Free — OpenRouter. The app falls back through a chain of free
# models when one is throttled.
OPENROUTER_API_KEY = "sk-or-v1-..."
MOCK_MODE = "0"
```

```toml
# Alternative — Google Gemini
GOOGLE_API_KEY = "AIza..."
MOCK_MODE = "0"
```

Save. The app restarts automatically.

Providers are checked in the order **OpenAI → OpenRouter → Gemini → mock**. That order is deliberate: **adding a paid OpenAI key on the day takes over automatically**, with no code or config change, and removes free-tier throttling from the live demo. Leave the OpenRouter key in place as the layer beneath it.

> ⚠️ **An OpenAI key that authenticates is not a key that works.** An account with no credit lists models happily and then returns `429 — you exceeded your current quota` on every completion. The app degrades to mock responses rather than erroring, so this failure is *silent*. Add billing at platform.openai.com **before** the day, and verify:
>
> ```bash
> python prototypes/agents/provider.py
> ```
>
> It prints the active provider, sends a real request, and names the exact problem if one fails.

**If you skip this, the app still works** — it detects the missing key and runs in offline mock mode. Worth knowing: a revoked or exhausted key degrades the app rather than breaking it.

### Why OpenRouter is the better default here

Free models on OpenRouter are shared capacity and **throttle upstream without warning**. Measured on this project within a single minute: one model returned 0/3 successes while four others returned 3/3. A single free model is not something to stand in front of an audience with.

So `provider.py` walks a chain (`OPENROUTER_FALLBACKS`) and takes the first model that answers. Re-check availability before the session:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
python tools/probe_models.py          # test the configured chain
python tools/probe_models.py --all    # discover and test every free model
```

It reports reliability **and** whether output is clean — "reasoning" models leak their thinking into the answer, which looks terrible projected and breaks the structured-output agents. Reorder `OPENROUTER_FALLBACKS` in `prototypes/agents/provider.py` if the tool suggests it.

> 🔑 Secrets live in Streamlit, never in the repo. `.streamlit/secrets.toml` is gitignored. A key committed to a public repo is scraped within minutes — Google now auto-revokes keys it detects as leaked. If it happens, revoke and reissue; rewriting git history is not enough.

---

## 3 · Tell the workflows where the app lives

So the scheduled health check knows what to ping:

```bash
gh variable set STREAMLIT_APP_URL --body "https://clinical-ai-agents.streamlit.app"
```

Then run it once to confirm:

```bash
gh workflow run live-check.yml
gh run watch
```

---

## 4 · Verify — properly

- [ ] App loads at your `.streamlit.app` URL
- [ ] Sidebar reads **LIVE**, not OFFLINE *(if OFFLINE, the secret did not take — check the key name is exactly `GOOGLE_API_KEY`)*
- [ ] All four prototypes work
- [ ] **GuideBot refuses the adrenaline question** ← the whole demo rests on this
- [ ] DischargeDraft fires the identifier warning on the seeded notes
- [ ] TriageAssist escalates the chest-pain case immediately
- [ ] **Opens on your phone over mobile data**, not just laptop wifi
- [ ] QR code generated from the URL and pasted onto slide 26

---

## How the CI/CD actually fits together

```
   you edit code
        │
        ├──► git push ──┬──► GitHub Actions ── tests + boot check + rebuilds deck/PDFs
        │               │
        │               └──► Streamlit Cloud ── detects the push, redeploys (~90s)
        │
        └──► daily 12:00 IST ──► live-check workflow ── is the app actually up?
```

**Three workflows, three jobs:**

| Workflow | Job | Catches |
|---|---|---|
| `ci.yml` | `agents` | A broken guardrail — the refusal or the red flags stop working |
| `ci.yml` | `boot` | An import error or missing dependency, **before** Streamlit Cloud hits it |
| `ci.yml` | `materials` | A deck or PDF that no longer builds; uploads fresh copies as artifacts |
| `live-check.yml` | `reachable` | A deployment that is down, broken, or asleep |

The `boot` job is the one that earns its keep: it starts the exact entry point Streamlit Cloud uses and waits for a health response. Nearly every Community Cloud failure is a startup error, and this finds them in about 40 seconds instead of after a 3-minute cloud build.

---

## The live deploy demo on stage

This is what makes the deployment worth having:

```bash
# In prototypes/agents/guidebot.py change:
#   GROUNDING_THRESHOLD = 0.30   ->   0.75

git add -A
git commit -m "Raise grounding threshold for stricter refusal"
git push
```

Streamlit Cloud picks it up and rebuilds in roughly 90 seconds. **Do not watch the progress bar** — advance to slide 18 and talk over it, then return and refresh. The agent now refuses questions it previously answered.

One number, one line, a visible behaviour change. Rehearse it **twice** with a stopwatch. If your rebuild runs over two minutes, prepare a second slide of material to talk over.

---

## Troubleshooting

**Build fails: `ModuleNotFoundError`**
`requirements.txt` must be at the **repository root** (it is). If you add an import, add the package there too — the `boot` CI job will catch this before Streamlit does.

**Sidebar says OFFLINE on the deployed app**
The secret is missing or misnamed. It must be exactly `GOOGLE_API_KEY`. Check **Settings → Secrets**, then **Reboot app** — secrets are read at startup.

**App has gone to sleep**
Community Cloud sleeps apps after inactivity. It wakes on first visit, but a cold start is 30–60 seconds. **Open your app 10 minutes before the session.** This is on the pre-flight checklist for a reason — a cold start during your cold open is a bad way to begin.

**Push succeeded but the app did not change**
Check the app is tracking `main`, and look at **Manage app → logs** in the Streamlit UI. Occasionally a manual **Reboot app** is needed.

**Everything is broken on the morning of the session**
Do not fix it. Run locally with `MOCK_MODE=1`. See `run-sheet/fallback-plan.md`. The session works fine without a deployed app — you describe the deploy step instead of performing it.

---

## Alternative: Hugging Face Spaces

`huggingface-space-setup.md` in this folder covers a Spaces deployment. It is a viable second home — useful as a backup URL if you want one, though maintaining two deployments is usually more work than it is worth. Streamlit Cloud is the better fit here because it is already wired to your GitHub account.
