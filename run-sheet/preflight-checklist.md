# Pre-Flight Checklist

Three checkpoints. Do them in order. The whole point is that by 12:30 on the day there is nothing left to discover.

---

## ☐ T-minus 1 week — build it once, for real

- [ ] Free **Google AI Studio** API key created → https://aistudio.google.com/apikey
- [ ] Free **Hugging Face** account created, and a Space deployed from `deploy/huggingface-space-setup.md`
- [ ] The public Space URL **opens on your phone over mobile data** (not just on your laptop)
- [ ] Free **no-code builder** account ready and logged in (Gemini Gem, Custom GPT, or Claude Project)
- [ ] You have **built GuideBot in the builder once already** — start-to-finish, timed
- [ ] It took you **under 8 minutes**. If not, cut a step and try again.
- [ ] Guideline PDFs downloaded to the **desktop**, in one folder, ready to drag
- [ ] QR code generated for your takeaway link and **pasted onto slide 26**

**The single most important item on this page:** you have run the live build once, end to end, and timed it. Everything else is recoverable. An unrehearsed live build is not.

---

## ☐ T-minus 1 day — prove the fallbacks

```powershell
cd "D:\AI workshop\clinical-ai-agent-session\prototypes"
py -3.11 test_grounding.py     # must print ALL PASS
py -3.11 test_agents.py        # must print ALL PASS
```

- [ ] Both test scripts print **ALL PASS**
- [ ] App runs locally: `py -3.11 -m streamlit run app.py`
- [ ] **Offline test — do this properly:**
  - [ ] Turn the wifi **off** on your laptop
  - [ ] `$env:MOCK_MODE="1"` then run the app
  - [ ] Click through **all four** prototypes. Everything works.
  - [ ] Turn wifi back on
- [ ] Screen recordings made (see `fallback-plan.md`) and saved to the **desktop**
- [ ] Deck opens on your laptop with **presenter view working** and notes visible to you only
- [ ] Laptop tested with an **HDMI projector** — resolution, scaling, no surprises
- [ ] Phone hotspot tested: laptop connects, app loads

---

## ☐ T-minus 1 hour — the room

- [ ] Arrive during the 11:15 tea break, while the auditorium is empty
- [ ] **Plug into the actual projector** and check the back row can read the app text
- [ ] Browser zoom set so the app is readable from the back — usually **125–150%**
- [ ] Laptop on **phone hotspot**, not auditorium wifi. Do not trust conference wifi.
- [ ] Loaded and confirmed working: builder tab, deployed app tab, terminal, deck
- [ ] Laptop **plugged into power**
- [ ] **Sleep and screensaver disabled.** Notifications off. Do Not Disturb on.
- [ ] Phone silenced

---

## ☐ T-minus 5 minutes — the lectern

- [ ] `stage-script.md` printed and on the lectern
- [ ] Water within reach
- [ ] Deck in presenter view, on slide 1
- [ ] **GuideBot open behind the deck**, one alt-tab away, ready for the cold open
- [ ] Terminal at `prototypes/`, `git status` clean
- [ ] A glance at the clock. You stop at **13:15**.

---

## The two questions to ask yourself before you walk on

**1. If the internet dies right now, what do I do?**
You set `MOCK_MODE=1` and run locally. Everything still works. You say *"we're running this offline, which is itself worth noticing."*

**2. If the live build fails, what do I do?**
You say *"and here's one I prepared earlier"*, switch to the deployed app, and carry on. You lose nothing.

If you can answer both without looking anything up, you are ready.
