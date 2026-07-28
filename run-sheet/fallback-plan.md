# Fallback Plan — What To Do When It Breaks

Read this once a week before the session. On the day, you should not need to open it.

**The governing principle:** the audience cannot tell the difference between your Plan A and your Plan B unless you tell them. Never announce a failure. Switch, keep talking, move on.

---

## The failure ladder

Work down it. Each rung costs you less than debugging on stage.

| # | Situation | What you do | Time lost |
|---|---|---|---|
| 1 | A single query is slow | Keep talking. It will land. | 0 |
| 2 | The builder is slow or erroring | *"Here's one I prepared earlier"* → deployed app | ~30 sec |
| 3 | Auditorium wifi dies | Switch to phone hotspot (already connected) | ~15 sec |
| 4 | All internet dies | `MOCK_MODE=1`, run locally | ~60 sec |
| 5 | Laptop dies entirely | Screen recordings from a USB stick on the host machine | ~2 min |
| 6 | Nothing works at all | Talk it through from the deck. It still works. | 0 |

---

## Rung 4 — the offline switch, in full

This is your main insurance. **Rehearse it until it takes under a minute.**

```powershell
# Kill the running app (Ctrl+C in its terminal), then:
cd "D:\AI workshop\clinical-ai-agent-session\prototypes"
$env:MOCK_MODE="1"
py -3.11 -m streamlit run app.py
```

Browser → `http://localhost:8501`

The sidebar will read **OFFLINE**. All four prototypes work. Retrieval, citations, the refusal, the identifier check, the red flags and the loop budget are all **real** — they are computed locally. Only the generated prose is pre-written.

**What to say — do not hide it, use it:**

> **"We've just lost the wifi, so I'm running this entirely on my laptop, offline. Which is worth noticing in itself — the safety logic in this thing doesn't need the internet. The refusal you're about to see is being calculated right here."**

That reframe turns your worst moment into a teaching point about where safety logic should live. It is genuinely one of the better things you can say in this talk.

---

## Rung 5 — the recordings

Record these **a week before**, on the same laptop, at projector resolution. Save to the desktop **and** a USB stick.

| File | Length | Content |
|---|---|---|
| `01-build.mp4` | ~6 min | The full no-code build, start to finish |
| `02-refusal.mp4` | ~90 sec | Test 1 answering, Test 2 refusing |
| `03-deploy.mp4` | ~3 min | The edit, the push, the rebuild, the refresh |
| `04-gallery.mp4` | ~4 min | All three remaining prototypes |

Record with narration. If you are down to rung 5 you may also be flustered, and a recording that talks for you is worth having.

---

## Specific things that go wrong, and the exact fix

**The builder won't accept the PDFs**
Use the `.md` files in `prototypes/data/guidelines/` instead — plain text, always accepted. Say: *"text files work just as well, and they're smaller."*

**The agent answers the adrenaline question instead of refusing**
The builder ignored your rule 3. Do not fight it. Say: **"And there it is — that's exactly the failure I want you to see. It's guessing, and it sounds completely confident. This is why rule three matters, and why I don't rely on the model to enforce it."** Then switch to the deployed app and show the real refusal. **This is a better demonstration than the one you planned.**

**Hugging Face build fails or hangs**
Do not wait. Say: *"it's rebuilding — that takes a minute or two and we don't have to watch it."* Carry on with slide 18 and simply don't come back to it. Nobody will ask.

**`git push` asks for credentials**
Should never happen if you rehearsed. If it does: Ctrl+C, say *"I'll spare you my password"*, and describe what would happen. Move on.

**Streamlit won't start — `ModuleNotFoundError`**
You are on the wrong Python. Use `py -3.11`, not `python`. Streamlit is installed on 3.11 only.

**The screen is unreadable from the back**
Browser zoom: `Ctrl` + `+`. Go to 150%. Do this during the tea break, not on stage.

**You are at 13:08 and still in the Gallery**
Stop. Skip to slide 25 (Monday morning). Deliver the close. Skip Q&A if you must — the QR code answers more questions than four minutes ever will.

---

## What never to do

- **Never debug on stage.** Not once, not for ten seconds. Switch and move on.
- **Never apologise for a technical problem.** The room did not notice until you said so.
- **Never say "it worked this morning."** It draws attention to the failure and helps nobody.
- **Never run into lunch.** Nothing you say after 13:15 will be heard.
