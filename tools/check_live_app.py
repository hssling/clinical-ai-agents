"""Pre-flight check on the DEPLOYED app.

    python check_live_app.py [url]

The CI `live-check` workflow only asks whether the URL answers. This asks the
questions that actually matter on the day:

  * is it awake, or will the audience watch a 40-second cold start?
  * is it in LIVE mode, or silently running on mock responses?
  * does GuideBot still REFUSE the out-of-scope question?

That last one is the demo. Everything else is scenery.

Note: Streamlit Community Cloud serves the app inside a NESTED IFRAME
(`<host>/~/+/`). The outer document is empty, so everything here works against
that frame rather than the page.

Needs: pip install playwright && playwright install chromium
"""

from __future__ import annotations

import sys

from playwright.sync_api import Frame, Page, sync_playwright

DEFAULT_URL = "https://clinical-ai-agents.streamlit.app"


def app_frame(page: Page) -> Frame | None:
    """Find the frame the Streamlit app is actually rendered in."""
    for frame in page.frames:
        try:
            text = frame.evaluate("() => document.body.innerText || ''")
        except Exception:  # noqa: BLE001 - frame detached mid-load
            continue
        if "GuideBot" in text or "Clinical AI Agents" in text:
            return frame
    return None


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    print(f"Checking {url}\n")
    problems: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 950})
        page.goto(url, wait_until="domcontentloaded", timeout=90000)

        # A sleeping Community Cloud app shows a wake button instead of the app.
        try:
            wake = page.get_by_role("button", name="Yes, get this app back up!")
            if wake.count():
                print("!  App was ASLEEP. Waking it now.")
                print("   Cold start is 30-60s -- open it 10 min before the session.\n")
                wake.click()
                problems.append("was asleep")
        except Exception:  # noqa: BLE001
            pass

        frame, body = None, ""
        for _ in range(45):
            page.wait_for_timeout(2000)
            frame = app_frame(page)
            if frame:
                body = frame.evaluate("() => document.body.innerText || ''")
                if "GuideBot" in body and "Mode" in body:
                    break

        if not frame or "GuideBot" not in body:
            print("FAIL  App did not finish rendering within 90 seconds.")
            page.screenshot(path="check_live_failure.png", full_page=True)
            print("      Screenshot saved: check_live_failure.png")
            browser.close()
            return 1

        print("PASS  App rendered")

        if "21 guideline sections loaded" in body:
            print("PASS  All 21 guideline sections loaded")
        else:
            print("FAIL  Guideline sections did not load")
            problems.append("guidelines missing")

        if "OFFLINE" in body:
            print("WARN  Running in OFFLINE mock mode")
            print("      No API key is reaching the app. Streamlit -> Settings -> Secrets,")
            print("      set OPENROUTER_API_KEY (or GOOGLE_API_KEY), then Reboot app.")
            print("      The demo still works offline -- but answers are pre-written.")
            problems.append("offline mode")
        elif "LIVE" in body:
            model = next((line for line in body.splitlines() if "LIVE" in line), "").strip()
            print(f"PASS  Running in LIVE mode  ({model})")
        else:
            print("WARN  Could not read the mode indicator")

        # The refusal is the session. Verify it end to end.
        try:
            frame.get_by_role("button", name="Out of scope").click(timeout=15000)
            page.wait_for_timeout(5000)
            after = frame.evaluate("() => document.body.innerText || ''")
            if "REFUSED" in after:
                print("PASS  GuideBot REFUSED the out-of-scope question  <-- the demo works")
            else:
                print("FAIL  GuideBot did NOT refuse. The core demo is broken.")
                problems.append("refusal broken")
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL  Could not run the refusal check: {type(exc).__name__}")
            problems.append("refusal untested")

        browser.close()

    print()
    # Offline mode and a cold start are warnings; the session survives both.
    fatal = [p for p in problems if p not in ("offline mode", "was asleep")]
    if problems:
        print("NOTED: " + ", ".join(problems))
    if fatal:
        return 1
    print("Ready." if not problems else "Usable, with the notes above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
